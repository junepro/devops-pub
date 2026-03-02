import argparse
import logging
import tempfile
import warnings
from pathlib import Path

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from mlflow.models.signature import infer_signature
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train & evaluate ElasticNet with MLflow.")
    parser.add_argument("--data-path", type=str, default="red-wine-quality.csv")
    parser.add_argument("--target", type=str, default="quality")
    parser.add_argument("--experiment-name", type=str, default="experiment_custom_sklearn")
    parser.add_argument("--run-name", type=str, default=None)
    parser.add_argument("--tracking-uri", type=str, default=None)

    parser.add_argument("--alpha", type=float, default=0.4)
    parser.add_argument("--l1-ratio", type=float, default=0.4)
    parser.add_argument("--test-size", type=float, default=0.25)
    parser.add_argument("--random-state", type=int, default=42)

    parser.add_argument("--registered-model-name", type=str, default=None)
    return parser.parse_args()


def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae = float(mean_absolute_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))
    return {"rmse": rmse, "mae": mae, "r2": r2}


def main() -> None:
    warnings.filterwarnings("ignore")
    args = parse_args()

    if args.tracking_uri:
        mlflow.set_tracking_uri(args.tracking_uri)

    exp = mlflow.set_experiment(args.experiment_name)
    logger.info("MLflow tracking URI: %s", mlflow.get_tracking_uri())
    logger.info("Experiment: %s (%s)", exp.name, exp.experiment_id)

    data_path = Path(args.data_path)
    df = pd.read_csv(data_path)

    if args.target not in df.columns:
        raise ValueError(f"target column '{args.target}' not found in data: {list(df.columns)}")

    train_df, test_df = train_test_split(
        df, test_size=args.test_size, random_state=args.random_state
    )

    X_train = train_df.drop(columns=[args.target])
    y_train = train_df[args.target]
    X_test = test_df.drop(columns=[args.target])
    y_test = test_df[args.target]

    model = ElasticNet(alpha=args.alpha, l1_ratio=args.l1_ratio, random_state=args.random_state)

    with mlflow.start_run(run_name=args.run_name) as run:
        mlflow.set_tags(
            {
                "engineering": "ML platform",
                "release.candidate": "RC1",
                "release.version": "2.0",
            }
        )

        mlflow.log_params(
            {
                "alpha": args.alpha,
                "l1_ratio": args.l1_ratio,
                "test_size": args.test_size,
                "random_state": args.random_state,
                "data_path": str(data_path),
                "target": args.target,
            }
        )

        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        metrics = regression_metrics(y_test.to_numpy(), preds)
        mlflow.log_metrics(metrics)

        signature = infer_signature(X_train, model.predict(X_train))
        model_info = mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            signature=signature,
            input_example=X_train.head(5),
            registered_model_name=args.registered_model_name,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            train_path = tmpdir_path / "train.csv"
            test_path = tmpdir_path / "test.csv"
            data_path_out = tmpdir_path / "data.csv"
            train_df.to_csv(train_path, index=False)
            test_df.to_csv(test_path, index=False)
            df.to_csv(data_path_out, index=False)
            mlflow.log_artifacts(str(tmpdir_path), artifact_path="data")

        mlflow.evaluate(
            model=model_info.model_uri,
            data=test_df,
            targets=args.target,
            model_type="regressor",
            evaluators=["default"],
        )

        logger.info("Run ID: %s", run.info.run_id)
        logger.info("Model URI: %s", model_info.model_uri)
        logger.info("Metrics: %s", metrics)


if __name__ == "__main__":
    main()