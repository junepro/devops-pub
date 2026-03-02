import mlflow.sagemaker
from mlflow.deployments import get_deploy_client

endpoint_name="prod-endpoint"
model_uri="s3://mlflow-project-artifacts/4/artifacts/XGBRegressor"

# Define your configuration parameters as a dictionary
config = {
    "execution_role_arn": "arn:aws:iam:::role/house-price-role",
    "bucket_name": "mlflow-project-artifacts",
    "image_url": ".dkr.ecr.us-east-1.amazonaws.com/xgb:2.9.1",
    "region_name": "us-east-1",
    "archive": False,
    "instance_type": "ml.m5.xlarge",
    "instance_count": 1,
    "synchronous": True
}

# Initialize a deployment client for SageMaker
client = get_deploy_client("sagemaker")

# Create the deployment
client.create_deployment(
    name=endpoint_name,
    model_uri=model_uri,
    flavor="python_function",
    config=config,
)
