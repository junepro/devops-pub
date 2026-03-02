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
from mlflow.models.signature import infer_signature  # [중요] 입출력 구조(스키마) 자동 파악 도구

# 1. 로깅 설정 (실행 기록을 남기기 위함)
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

# 2. 터미널 실행 옵션 설정 (예: python train.py --alpha 0.5)
parser = argparse.ArgumentParser()
parser.add_argument("--alpha", type=float, required=False, default=0.7)
parser.add_argument("--l1_ratio", type=float, required=False, default=0.7)
args = parser.parse_args()

# 3. 평가 함수 정의 (RMSE, MAE, R2 계산)
def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2

# 메인 실행 블록
if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    np.random.seed(40)

    # 4. 데이터 로드 및 분할
    try:
        data = pd.read_csv("red-wine-quality.csv")
    except Exception as e:
        logger.exception("CSV 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
        exit(1)

    # 데이터를 학습용(train)과 테스트용(test)으로 75:25 분리
    train, test = train_test_split(data)

    # 정답 컬럼(quality)과 문제 데이터(x) 분리
    train_x = train.drop(["quality"], axis=1)
    test_x = test.drop(["quality"], axis=1)
    train_y = train[["quality"]]
    test_y = test[["quality"]]

    # 입력받은 하이퍼파라미터 가져오기
    alpha = args.alpha
    l1_ratio = args.l1_ratio

    # 5. [최신 트렌드] MLflow Autolog 설정
    # 학습 시 파라미터와 메트릭을 자동으로 기록합니다.
    # log_models=False: 모델 저장은 아래에서 Signature와 함께 수동으로 하기 위해 끕니다.
    mlflow.sklearn.autolog(log_models=False)

    # 실험 이름 설정
    exp = mlflow.set_experiment(experiment_name="experiment_1")

    # 6. Run 시작 (컨텍스트 매니저 활용)
    with mlflow.start_run(experiment_id=exp.experiment_id):
        
        # 모델 생성
        lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
        
        # 모델 학습 (여기서 Autolog가 작동해 파라미터가 자동 기록됨)
        lr.fit(train_x, train_y)

        # 예측 수행
        predicted_qualities = lr.predict(test_x)

        # 성능 평가
        (rmse, mae, r2) = eval_metrics(test_y, predicted_qualities)

        # 터미널 출력용 (기록용은 아님)
        print(f"Elasticnet model (alpha={alpha}, l1_ratio={l1_ratio}):")
        print(f"  RMSE: {rmse}")
        print(f"  MAE: {mae}")
        print(f"  R2: {r2}")

        # 7. [최신 트렌드] Signature 생성 및 모델 저장
        # 모델의 입력/출력 데이터 구조(Schema)를 생성
        signature = infer_signature(train_x, predicted_qualities)

        # 모델 + Signature + 입력 예시(Example)를 함께 저장
        mlflow.sklearn.log_model(
            sk_model=lr,
            artifact_path="model",
            signature=signature,           # 배포 시 데이터 검증용
            input_example=train_x.iloc[:5] # 사용자가 참고할 예시 데이터
        )