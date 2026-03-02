🏗️ LGTM + Alloy 아키텍처
Collector: Grafana Alloy (Telemetry 수집 및 전달)

Logs: Loki

Traces: Tempo

Metrics: Mimir (Prometheus 대체, 장기 저장소)

Storage: MinIO (Loki, Tempo, Mimir의 데이터 저장소)


1. 기본 설정 및 저장소(MinIO) 준비
Mimir와 Loki, Tempo가 데이터를 저장할 Object Storage가 필요합니다.

Bash
# 네임스페이스 생성
kubectl create namespace monitoring

# Helm Repo 추가
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add minio https://charts.min.io/
helm repo update
MinIO 설치 (테스트용):

helm upgrade --install minio minio/minio \
  --namespace monitoring \
  --set rootUser=minio \
  --set rootPassword=minio123 \
  --set persistence.enabled=false \
  --set mode=standalone \
  --set resources.requests.cpu=250m \
  --set resources.requests.memory=512Mi \
  --set resources.limits.cpu=500m \
  --set resources.limits.memory=1Gi   

helm uninstall minio -n monitoring

# Mimir 설치:

helm upgrade --install mimir grafana/mimir-distributed --namespace monitoring -f mimir-val.yaml  --force 

helm uninstall mimir -n monitoring

3. Loki (Logs) & Tempo (Traces) 설치
Loki와 Tempo도 MinIO를 바라보도록 설정합니다.

Loki 설치:

Bash
helm upgrade --install loki grafana/loki   --namespace monitoring  -f loki-val.yaml
helm uninstall loki -n monitoring
  
  kubectl port-forward --namespace monitoring svc/loki-gateway 3100:80 &

Tempo 설치:

Bash
helm upgrade --install tempo grafana/tempo-distributed --namespace monitoring -f tempo-val.yaml

helm repo add grafana https://grafana.github.io/helm-charts
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

kubectl create namespace monitoring

4. Grafana Alloy 구축 (핵심)
이제 Alloy를 설정하여 앱의 메트릭을 Mimir로 전송(remote_write)합니다.

Alloy 설치:

Bash
helm upgrade --install alloy grafana/alloy --namespace monitoring -f alloy-val.yaml


5. Grafana 및 데이터소스 설정
Grafana에서 Mimir를 데이터소스로 등록할 때는 Prometheus 타입을 선택합니다.


Grafana 설치:

Bash
helm upgrade --install grafana grafana/grafana --namespace monitoring -f grafana-val.yaml

   kubectl get secret --namespace monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo

  kubectl --namespace monitoring port-forward svc/grafana 3000:80






  ## alloy 에 타겟서버 추가하는법 (이전 prometheus.yaml target 설정)

      // 1. 수집 대상(Target) 정의
    prometheus.scrape "static_target" {
      targets = [
        {"__address__" = "192.168.0.0:7900", "instance" = "my-server"},
      ]
      forward_to = [prometheus.remote_write.mimir.receiver]
    }

    // 2. 데이터를 보낼 목적지(Mimir/LGTM) 정의
    prometheus.remote_write "mimir" {
      endpoint {
        url = "http://mimir-gateway:8080/api/v1/push"
      }
    }