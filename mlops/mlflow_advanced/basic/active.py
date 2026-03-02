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

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2

def main():
    warnings.filterwarnings("ignore")
    np.random.seed(40)

    # 1. 인수 파싱
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha", type=float, default=0.7)
    parser.add_argument("--l1_ratio", type=float, default=0.7)
    args = parser.parse_args()

    # 2. 데이터 로드 및 분할
    try:
        data = pd.read_csv("red-wine-quality.csv")
    except Exception as e:
        logger.exception("데이터 파일을 찾을 수 없습니다. 경로를 확인하세요. Error: %s", e)
        return

    train, test = train_test_split(data)
    train_x = train.drop(["quality"], axis=1)
    test_x = test.drop(["quality"], axis=1)
    train_y = train[["quality"]]
    test_y = test[["quality"]]

    # 3. MLflow 설정
    # 로컬 실행 시 기본값으로 두거나 특정 서버 주소를 입력합니다.
    mlflow.set_tracking_uri(uri="http://127.0.0.1:5000") 
    experiment_name = "wine_quality_experiment"
    
    # 실험이 없으면 생성, 있으면 가져오기
    if not mlflow.get_experiment_by_name(experiment_name):
        mlflow.create_experiment(name=experiment_name)
    mlflow.set_experiment(experiment_name)

    # 4. 모델 학습 및 MLflow 기록 (Context Manager 사용)
    with mlflow.start_run():
        alpha = args.alpha
        l1_ratio = args.l1_ratio

        lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
        lr.fit(train_x, train_y)

        predicted_qualities = lr.predict(test_x)
        (rmse, mae, r2) = eval_metrics(test_y, predicted_qualities)

        print(f"Elasticnet model (alpha={alpha:f}, l1_ratio={l1_ratio:f}):")
        print(f"  RMSE: {rmse}")
        print(f"  MAE: {mae}")
        print(f"  R2: {r2}")

        # 하이퍼파라미터 및 메트릭 기록
        mlflow.log_params({"alpha": alpha, "l1_ratio": l1_ratio})
        mlflow.log_metrics({"rmse": rmse, "mae": mae, "r2": r2})

        # 모델 기록 (Signature 포함 권장)
        mlflow.sklearn.log_model(
            sk_model=lr, 
            artifact_path="model",
            input_example=train_x.iloc[:5] # 최신 경향: 데이터 예시를 함께 저장
        )
        
        run_info = mlflow.active_run().info
        print(f"Active run id: {run_info.run_id}")

if __name__ == "__main__":
    main()