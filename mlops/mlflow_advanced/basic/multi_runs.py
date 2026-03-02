import warnings
import argparse
import logging
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet
import mlflow
import mlflow.sklearn
from mlflow.models.signature import infer_signature
from mlflow.data.pandas_dataset import PandasDataset
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 파서 설정
parser = argparse.ArgumentParser()
parser.add_argument("--alpha", type=float, required=False, default=0.7)
parser.add_argument("--l1_ratio", type=float, required=False, default=0.7)
args = parser.parse_args()

def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2

def load_and_prep_data(filepath):
    """데이터 로드 및 분할, 아티팩트 저장 준비"""
    try:
        data = pd.read_csv(filepath)
    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        raise

    # 데이터 저장 (Artifact용)
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    data.to_csv(data_dir / "red-wine-quality.csv", index=False)
    train, test = train_test_split(data, random_state=42) # 재현성을 위해 random_state 고정
    
    train.to_csv(data_dir / "train.csv", index=False)
    test.to_csv(data_dir / "test.csv", index=False)

    train_x = train.drop(["quality"], axis=1)
    test_x = test.drop(["quality"], axis=1)
    train_y = train[["quality"]]
    test_y = test[["quality"]]

    return train_x, test_x, train_y, test_y, train

def train_model(alpha, l1_ratio, run_name, train_x, test_x, train_y, test_y, raw_df):
    """단일 실험 실행을 위한 함수"""
    
    # Context Manager(with)를 사용하여 안전하게 Run 관리
    with mlflow.start_run(run_name=run_name) as run:
        # 1. 태그 설정
        mlflow.set_tags({
            "engineering": "ML platform",
            "release.candidate": "RC1",
            "release.version": "2.0",
            "model.type": "ElasticNet"
        })
        
        logger.info(f"Run ID: {run.info.run_id}, Name: {run.info.run_name}")

        # 2. 모델 학습
        lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
        lr.fit(train_x, train_y)

        # 3. 예측 및 평가
        predicted_qualities = lr.predict(test_x)
        (rmse, mae, r2) = eval_metrics(test_y, predicted_qualities)

        print(f"Elasticnet model (alpha={alpha:f}, l1_ratio={l1_ratio:f}):")
        print(f"  RMSE: {rmse}")
        print(f"  MAE: {mae}")
        print(f"  R2: {r2}")

        # 4. 파라미터 및 메트릭 기록
        mlflow.log_params({
            "alpha": alpha,
            "l1_ratio": l1_ratio
        })

        mlflow.log_metrics({
            "rmse": rmse,
            "r2": r2,
            "mae": mae
        })

        # 5. [Modern] Dataset API 사용 (데이터 계보 추적)
        # MLflow 2.x에서는 데이터셋 객체를 명시적으로 기록하는 것을 권장
        dataset = mlflow.data.from_pandas(raw_df, targets="quality", name="wine_quality_data")
        mlflow.log_input(dataset, context="training")

        # 6. [Modern] Model Signature & Input Example 생성
        # 모델 배포 시 입력 데이터 형식을 검증하기 위해 필수적임
        signature = infer_signature(train_x, predicted_qualities)
        input_example = train_x.iloc[:5]

        # 7. 모델 저장
        mlflow.sklearn.log_model(
            sk_model=lr,
            artifact_path="model",
            signature=signature,       # 입출력 스키마 명시
            input_example=input_example, # 예제 데이터 포함
            registered_model_name="WineQualityElasticNet" # 모델 레지스트리에 자동 등록 (옵션)
        )

        # 8. 추가 아티팩트 저장
        mlflow.log_artifacts("data/")

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    np.random.seed(40)
    
    # 1. 기본 설정
    csv_url = "red-wine-quality.csv" # 혹은 URL
    # 로컬 파일이 없으면 예외 처리나 다운로드 로직 필요 (여기선 파일이 있다고 가정)
    if not Path(csv_url).exists():
        logger.warning(f"File {csv_url} not found. Please ensure the file exists.")
        # 테스트를 위해 더미 파일 생성 방지용 exit (실제 사용시 주석 처리)
        # exit() 

    # 2. 데이터 준비
    train_x, test_x, train_y, test_y, full_train_df = load_and_prep_data(csv_url)

    # 3. MLflow 실험 설정
    mlflow.set_tracking_uri(uri="") # 로컬 ./mlruns 사용
    experiment_name = "experiment_wine_quality"
    
    # 실험이 없으면 생성, 있으면 가져오기
    try:
        exp_id = mlflow.create_experiment(experiment_name)
    except mlflow.exceptions.MlflowException:
        exp_id = mlflow.get_experiment_by_name(experiment_name).experiment_id
    
    mlflow.set_experiment(experiment_name=experiment_name)
    print(f"Experiment ID: {exp_id}")

    # 4. 실험 반복 실행 (Loop 사용으로 중복 제거)
    # (alpha, l1_ratio, run_name) 튜플 리스트
    experiments_config = [
        (args.alpha, args.l1_ratio, "run1.1_custom"), # 사용자 입력값
        (0.9, 0.9, "run2.1_high_reg"),
        (0.4, 0.4, "run3.1_low_reg")
    ]

    for alpha_val, l1_val, run_name in experiments_config:
        print(f"\nStarting Run: {run_name}")
        train_model(alpha_val, l1_val, run_name, train_x, test_x, train_y, test_y, full_train_df)

    # 5. 마지막 실행 정보 확인
    last_run = mlflow.last_active_run()
    if last_run:
        print(f"\nRecent Active run id: {last_run.info.run_id}")
    
    print("All runs completed.")