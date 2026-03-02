from __future__ import annotations
import os
import argparse
import math
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import mlflow
import mlflow.sklearn

def parse_args():
    p = argparse.ArgumentParser("Simple MLflow demo (wine prediction)")
    p.add_argument("--csv", default="data/wine_sample.csv", help="Path to CSV (default: data/wine_sample.csv)")
    p.add_argument("--target", default="quality", help="Target column name (default: quality)")
    p.add_argument("--experiment", default="wine-prediction", help="MLflow experiment name")
    p.add_argument("--run", default="run-2", help="MLflow run name")
    p.add_argument("--n-estimators", type=int, default=50, help="RandomForest n_estimators (default: 50)")
    p.add_argument("--max-depth", type=int, default=5, help="RandomForest max_depth (default: 5)")
    p.add_argument("--test-size", type=float, default=0.2, help="Test split fraction (default: 0.3)")
    p.add_argument("--random-state", type=int, default=42, help="Random seed (default: 42)")
    return p.parse_args()

def main():
    args = parse_args()

    # Set MLflow tracking URI from env or use default
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:7006")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(args.experiment)

    # Load CSV
    if not os.path.exists(args.csv):
        raise SystemExit(f"CSV not found: {args.csv}. Create or copy wine_sample.csv next to this script.")
    df = pd.read_csv(args.csv)

    if args.target not in df.columns:
        raise SystemExit(f"Target column '{args.target}' not found in CSV. Columns: {list(df.columns)}")

    # Prepare data
    X = df.drop(columns=[args.target])
    y = df[args.target]

    # 피처(X)와 타겟(y) 분리
    # X = df.drop(columns=["quality"])와 y = df["quality"]를 실행한 결과입니다.

    # X (Features): 모델이 학습할 때 참고할 '재료'입니다. (정답 컬럼 제외)
    #     | alcohol | acidity | sugar |
    #     | :--- | :--- | :--- |
    #     | 12.5 | 0.5 | 2.1 |
    #     | 13.2 | 0.8 | 1.9 |
    #     | ... | ... | ... |

    # y (Target): 모델이 맞춰야 할 '정답'입니다.
    #     | quality |
    #     | :--- |
    #     | 6 |
    #     | 5 |
    #     | ... |

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_state
    )
    # train_test_split을 하면 전체 데이터를 test_size=0.2(20%) 비율로 무작위로 섞어서 나눕니다. (총 5개 데이터 중 1개가 테스트용이 됨)

    # 학습 세트 (80%): 모델이 공부하는 데 사용

        # X_train: [12.5, 0.5, 2.1], [11.0, 0.3, 5.5], [12.1, 0.4, 2.0], [14.0, 0.6, 1.8]
        # y_train: [6, 7, 6, 8]

    # 테스트 세트 (20%): 모델이 얼마나 잘 맞추는지 시험 보는 데 사용

        # X_test: [13.2, 0.8, 1.9] (시험 문제)
        # y_test: [5] (실제 정답 - 모델의 예측값과 비교용)

    # Train and log with MLflow
    with mlflow.start_run(run_name=args.run) as run:
        # Log simple params
        mlflow.log_param("n_estimators", args.n_estimators)
        mlflow.log_param("max_depth", args.max_depth)
        mlflow.log_param("test_size", args.test_size)
        mlflow.log_param("random_state", args.random_state)
        mlflow.log_param("train_rows", len(X_train))
        mlflow.log_param("test_rows", len(X_test))

        # Train model
        model = RandomForestRegressor(
            n_estimators=args.n_estimators,
            max_depth=args.max_depth,
            random_state=args.random_state,
        )
        model.fit(X_train, y_train)

        # Predict + metrics
        preds = model.predict(X_test)
        mse = mean_squared_error(y_test, preds)          # MSE is stable across sklearn versions
        rmse = float(math.sqrt(mse))                     # avoid `squared=` kw argument issues
        r2 = float(r2_score(y_test, preds))

    # MSE (Mean Squared Error, 평균 제곱 오차)
    #     가장 표준적인 오차 지표입니다.

    #     정의: (실제값 - 예측값)을 제곱하여 모두 더한 뒤 평균을 낸 값

    # RMSE (Root Mean Squared Error, 평균 제곱근 오차)
    # MSE에 루트를 씌운 값으로 실무에서 가장 많이 참조합니다. 
    # 정의: MSE에 **루트($\sqrt{ }$)**를 씌운 값입니다.
    # 모델의 예측이 평균적으로 실제값과 이 정도 차이가 난다

    # r2 Score (R-squared, 결정계수)
    #     모델이 데이터를 얼마나 잘 설명하는지 나타내는 '상대적' 지표입니다.
    #     정의: 전체 분산 중 모델이 설명하는 분산의 비율입니다.
    #     해석:
    #     1.0: 완벽한 모델 (모든 정답을 다 맞춤)
    #     0.0: 그냥 평균값으로만 찍는 모델 (학습 효과 없음)
    #     음수: 평균값으로 찍는 것보다도 못한 모델특징: MSE나 RMSE는 데이터의 단위에 따라 숫자가 커질 수 있지만, r2는 보통 0~1 사이로 나오므로 여러 모델의 성능을 비교할 때 아주 좋습니다.

        # Log metrics
        mlflow.log_metric("mse", float(mse))
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)

if __name__ == "__main__":
    main()
