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
from mlflow.models import infer_signature
from pathlib import Path
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    np.random.seed(40)

    # 인수 설정
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha", type=float, default=0.7)
    parser.add_argument("--l1_ratio", type=float, default=0.7)
    args = parser.parse_args()

    # 데이터 준비 및 로컬 저장
    data_path = Path("data")
    data_path.mkdir(exist_ok=True)
    
    data = pd.read_csv("red-wine-quality.csv")
    train, test = train_test_split(data)
    
    data.to_csv(data_path / "red-wine-quality.csv", index=False)
    train.to_csv(data_path / "train.csv", index=False)
    test.to_csv(data_path / "test.csv", index=False)

    train_x = train.drop(["quality"], axis=1)
    test_x = test.drop(["quality"], axis=1)
    train_y = train[["quality"]]
    test_y = test[["quality"]]

    # MLflow 설정
    mlflow.set_tracking_uri(uri="http://127.0.0.1:5000") # 실무 권장 방식
    experiment_name = "experiment_4"
    mlflow.set_experiment(experiment_name)

    # 런 시작 (Context Manager 사용)
    with mlflow.start_run() as run:
        # 모델 학습
        lr = ElasticNet(alpha=args.alpha, l1_ratio=args.l1_ratio, random_state=42)
        lr.fit(train_x, train_y)
        
        predicted_qualities = lr.predict(test_x)
        (rmse, mae, r2) = eval_metrics(test_y, predicted_qualities)

        # 로그 기록 (Batch)
        mlflow.log_params({"alpha": args.alpha, "l1_ratio": args.l1_ratio})
        mlflow.log_metrics({"rmse": rmse, "mae": mae, "r2": r2})
        
        # Artifacts 기록 (데이터 파일들)
        mlflow.log_artifacts("data/")

        # 모델 시그니처 생성 (입출력 스키마 정의)
        signature = infer_signature(train_x, predicted_qualities)

        # 모델 기록
        mlflow.sklearn.log_model(
            sk_model=lr, 
            artifact_path="model", 
            signature=signature,
            input_example=train_x.iloc[:3]
        )

        print(f"Run ID: {run.info.run_id}")
        print(f"Artifact URI: {mlflow.get_artifact_uri()}")