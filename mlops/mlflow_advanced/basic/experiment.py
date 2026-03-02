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
from pathlib import Path

# 1. 설정 및 준비
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--alpha", type=float, required=False, default=0.7)
parser.add_argument("--l1_ratio", type=float, required=False, default=0.7)
args = parser.parse_args()

def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    np.random.seed(40)

    # 데이터 로드
    try:
        data = pd.read_csv("red-wine-quality.csv")
    except Exception:
        print("CSV 파일을 찾을 수 없습니다.")
        exit(1)

    train, test = train_test_split(data)
    train_x = train.drop(["quality"], axis=1)
    test_x = test.drop(["quality"], axis=1)
    train_y = train[["quality"]]
    test_y = test[["quality"]]

    alpha = args.alpha
    l1_ratio = args.l1_ratio

    # 2. Tracking URI 설정 (기본값: 로컬 ./mlruns)
    mlflow.set_tracking_uri(uri="")
    print("The set tracking uri is ", mlflow.get_tracking_uri())

    # 3. [중요] 실험 생성 및 아티팩트 경로 지정
    exp_name = "exp_create_exp_artifact"
    # 현재 폴더 아래 'myartifacts'라는 폴더에 모델 파일을 저장하겠다는 의미
    artifact_loc = Path.cwd().joinpath("myartifacts").as_uri()

    # 실험 생성 (재실행 시 에러 방지를 위한 예외 처리)
    try:
        exp_id = mlflow.create_experiment(
            name=exp_name,
            tags={"version": "v1", "priority": "p1"},
            artifact_location=artifact_loc
        )
    except mlflow.exceptions.MlflowException:
        # 이미 실험이 존재하면 ID만 가져옴
        exp_id = mlflow.get_experiment_by_name(exp_name).experiment_id

    # 실험 메타데이터 출력 확인
    get_exp = mlflow.get_experiment(exp_id)
    print("\n--- Experiment Details ---")
    print(f"Name: {get_exp.name}")
    print(f"Experiment_id: {get_exp.experiment_id}")
    print(f"Artifact Location: {get_exp.artifact_location}")
    print(f"Tags: {get_exp.tags}")
    print("--------------------------\n")

    # 4. Autolog 설정 (파라미터 자동 기록)
    mlflow.sklearn.autolog(log_models=False)

    # 5. Run 실행
    with mlflow.start_run(experiment_id=exp_id):
        lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
        lr.fit(train_x, train_y)

        predicted_qualities = lr.predict(test_x)
        (rmse, mae, r2) = eval_metrics(test_y, predicted_qualities)

        print(f"Elasticnet model (alpha={alpha}, l1_ratio={l1_ratio}):")
        print(f"  RMSE: {rmse}")
        print(f"  MAE: {mae}")
        print(f"  R2: {r2}")

        # 사용자 정의 메트릭 추가 기록
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)
        mlflow.log_metric("mae", mae)

        # 6. Signature 생성 및 모델 저장
        signature = infer_signature(train_x, predicted_qualities)

        mlflow.sklearn.log_model(
            sk_model=lr, 
            artifact_path="model", 
            signature=signature,
            input_example=train_x.iloc[:5]
        )