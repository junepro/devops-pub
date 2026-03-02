# install

    python3 -m venv .venv

    source .venv/bin/activate

    python3 -m pip install mlflow

    mlflow ui --backend-store-uri sqlite://mlflow.db --port 7006


# kind 설정

    kind create cluster --name=basic-mlflow-cluster

# helm
    helm repo add community-charts https://community-charts.github.io/helm-charts
    helm repo update
    helm install mlfow-community community-charts/mlflow

# port

    kubectl port-forward pod/mlflow-community- 7006:5000 --address 0.0.0.0