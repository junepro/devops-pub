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

# 로깅 설정
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

    # 1. 인수 파싱
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha", type=float, default=0.7)
    parser.add_argument("--l1_ratio", type=float, default=0.7)
    args = parser.parse_args()

    # 2. 데이터 준비 및 로컬 저장 (Pathlib 활용)
    data_path = Path("data")
    data_path.mkdir(exist_ok=True)
    
    try:
        data = pd.read_csv("red-wine-quality.csv")
    except FileNotFoundError:
        logger.error("red-wine-quality.csv 파일이 없습니다.")
        exit(1)

    train, test = train_test_split(data)
    
    data.to_csv(data_path / "red-wine-quality.csv", index=False)
    train.to_csv(data_path / "train.csv", index=False)
    test.to_csv(data_path / "test.csv", index=False)

    train_x = train.drop(["quality"], axis=1)
    test_x = test.drop(["quality"], axis=1)
    train_y = train[["quality"]]
    test_y = test[["quality"]]

    # 3. MLflow 설정
    mlflow.set_tracking_uri(uri="http://127.0.0.1:5000") 
    mlflow.set_experiment("experiment_4")

    # 4. 학습 및 기록 (Context Manager 사용)
    with mlflow.start_run() as run:
        # 태그 설정
        mlflow.set_tags({
            "engineering": "ML platform",
            "release.candidate": "RC1",
            "release.version": "2.0"
        })

        lr = ElasticNet(alpha=args.alpha, l1_ratio=args.l1_ratio, random_state=42)
        lr.fit(train_x, train_y)

        predicted_qualities = lr.predict(test_x)
        (rmse, mae, r2) = eval_metrics(test_y, predicted_qualities)

        print(f"Elasticnet model (alpha={args.alpha:f}, l1_ratio={args.l1_ratio:f}):")
        print(f"  RMSE: {rmse}\n  MAE: {mae}\n  R2: {r2}")

        # 파라미터 및 메트릭 일괄 기록
        mlflow.log_params({"alpha": args.alpha, "l1_ratio": args.l1_ratio})
        mlflow.log_metrics({"rmse": rmse, "mae": mae, "r2": r2})
        
        # 아티팩트 기록 (데이터 폴더 전체)
        mlflow.log_artifacts("data/")

        # 모델 시그니처 및 로그
        signature = infer_signature(train_x, predicted_qualities)
        mlflow.sklearn.log_model(
            sk_model=lr, 
            artifact_path="model", 
            signature=signature,
            input_example=train_x.iloc[:3]
        )

        print(f"Active run id: {run.info.run_id}")
        print(f"Artifact URI: {mlflow.get_artifact_uri()}")