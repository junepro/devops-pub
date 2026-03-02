import warnings
import argparse
import logging
import pandas as pd
import numpy as np
from pathlib import Path

# Scikit-learn
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet, Ridge, Lasso

# MLflow
import mlflow
import mlflow.sklearn
from mlflow.models.signature import infer_signature
from mlflow.data.pandas_dataset import PandasDataset

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 파서 설정 (기본값 설정용)
parser = argparse.ArgumentParser()
parser.add_argument("--alpha", type=float, required=False, default=0.7)
parser.add_argument("--l1_ratio", type=float, required=False, default=0.7)
args = parser.parse_args()

def eval_metrics(actual, pred):
    """모델 성능 평가 지표 계산"""
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2

def load_data(filepath):
    """데이터 로드 및 전처리"""
    # 1. 데이터 로드
    try:
        data = pd.read_csv(filepath)
    except Exception as e:
        logger.error(f"데이터 로드 실패: {e}")
        raise

    # 2. 아티팩트 저장을 위한 로컬 폴더 생성
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    data.to_csv(data_dir / "red-wine-quality.csv", index=False)

    # 3. 데이터 분할
    train, test = train_test_split(data, random_state=42)
    train.to_csv(data_dir / "train.csv", index=False)
    test.to_csv(data_dir / "test.csv", index=False)

    train_x = train.drop(["quality"], axis=1)
    test_x = test.drop(["quality"], axis=1)
    train_y = train[["quality"]]
    test_y = test[["quality"]]

    return train_x, test_x, train_y, test_y, data

def run_single_entry(model_class, params, run_name, data_pack, tags):
    """
    단일 실행(Run)을 처리하는 코어 함수
    :param model_class: Sklearn 모델 클래스 (예: ElasticNet, Ridge...)
    :param params: 하이퍼파라미터 딕셔너리
    """
    train_x, test_x, train_y, test_y, raw_df = data_pack

    # Context Manager 사용
    with mlflow.start_run(run_name=run_name):
        # 1. 태그 설정
        mlflow.set_tags(tags)
        
        # 2. 모델 동적 초기화 및 학습 (Key Point!)
        # params 딕셔너리를 언패킹(**params)하여 모델 생성
        model = model_class(**params, random_state=42)
        model.fit(train_x, train_y)

        # 3. 예측 및 평가
        predicted = model.predict(test_x)
        (rmse, mae, r2) = eval_metrics(test_y, predicted)

        # 4. 로깅 (파라미터, 메트릭)
        mlflow.log_params(params)
        mlflow.log_metrics({"rmse": rmse, "r2": r2, "mae": mae})

        # 5. 콘솔 출력
        print(f"  [{run_name}] Model: {model_class.__name__}, Params: {params}")
        print(f"    RMSE: {rmse:.4f}, MAE: {mae:.4f}, R2: {r2:.4f}")

        # 6. [Modern] Dataset API & Signature
        dataset = mlflow.data.from_pandas(raw_df, targets="quality", name="wine_quality")
        mlflow.log_input(dataset, context="training")
        
        signature = infer_signature(train_x, predicted)
        input_example = train_x.iloc[:5]

        # 7. 모델 저장
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            signature=signature,
            input_example=input_example
        )
        
        # 8. 데이터 아티팩트 업로드
        mlflow.log_artifacts("data/")


def run_experiment_cycle(experiment_name, model_class, run_configs, data_pack):
    """
    하나의 실험(Experiment) 그룹을 관리하는 함수
    :param run_configs: 실행할 설정 리스트 (params, run_name)
    """
    print(f"\n========== Starting Experiment: {experiment_name} ==========")
    
    # 실험 생성 또는 설정
    try:
        mlflow.create_experiment(experiment_name)
    except mlflow.exceptions.MlflowException:
        pass # 이미 존재하면 무시
    
    mlflow.set_experiment(experiment_name)
    
    # 공통 태그
    common_tags = {
        "engineering": "ML platform",
        "release.candidate": "RC1",
        "release.version": "2.0",
        "model.type": model_class.__name__
    }

    # 설정된 횟수만큼 반복 실행
    for config in run_configs:
        run_single_entry(
            model_class=model_class,
            params=config['params'],
            run_name=config['run_name'],
            data_pack=data_pack,
            tags=common_tags
        )


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    np.random.seed(40)

    # 1. 데이터 준비
    csv_url = "red-wine-quality.csv"
    if not Path(csv_url).exists():
        logger.warning(f"File {csv_url} not found. Running with dummy/check logic.")
        # exit() 
        
    data_pack = load_data(csv_url) # (train_x, test_x, train_y, test_y, raw_df)

    # 2. 트래킹 서버 설정
    mlflow.set_tracking_uri(uri="") # Local

    # ==========================================
    # 3. 실험 설계 (Configuration) - 여기가 핵심!
    # ==========================================
    # 이 리스트만 수정하면 코드 변경 없이 실험을 늘리거나 줄일 수 있습니다.
    
    experiments_plan = [
        # --- Experiment 1: ElasticNet ---
        {
            "name": "exp_multi_EL",
            "model_class": ElasticNet,
            "runs": [
                {"run_name": "run1.1", "params": {"alpha": args.alpha, "l1_ratio": args.l1_ratio}},
                {"run_name": "run2.1", "params": {"alpha": 0.9, "l1_ratio": 0.9}},
                {"run_name": "run3.1", "params": {"alpha": 0.4, "l1_ratio": 0.4}},
            ]
        },
        # --- Experiment 2: Ridge ---
        {
            "name": "exp_multi_Ridge",
            "model_class": Ridge,
            "runs": [
                {"run_name": "run1.1", "params": {"alpha": args.alpha}},
                {"run_name": "run2.1", "params": {"alpha": 0.9}},
                {"run_name": "run3.1", "params": {"alpha": 0.4}},
            ]
        },
        # --- Experiment 3: Lasso ---
        {
            "name": "exp_multi_Lasso",
            "model_class": Lasso,
            "runs": [
                {"run_name": "run1.1", "params": {"alpha": args.alpha}},
                {"run_name": "run2.1", "params": {"alpha": 0.9}},
                {"run_name": "run3.1", "params": {"alpha": 0.4}},
            ]
        }
    ]

    # 4. 전체 실험 일괄 실행
    for plan in experiments_plan:
        run_experiment_cycle(
            experiment_name=plan["name"],
            model_class=plan["model_class"],
            run_configs=plan["runs"],
            data_pack=data_pack
        )

    print("\nAll experiments completed successfully.")