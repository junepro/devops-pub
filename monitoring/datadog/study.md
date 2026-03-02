kubectl create secret generic datadog-secret \
    --from-literal=api-key="<YOUR_API_KEY>"


helm

helm repo add datadog https://helm.datadoghq.com
helm repo update

helm install datadog-agent -f values.yaml datadog/datadog --namespace datadog


# 1. Helm 차트 삭제
helm uninstall datadog-agent --namespace datadog

# 2. 네임스페이스 삭제 (안에 들어있던 나머지 리소스까지 모두 제거)
kubectl delete namespace datadog

helm upgrade datadog-agent -f values.yaml datadog/datadog -n datadog


# 배포될때 cluster agent 가 먼저 뜨고 노드 뜨는 형식이라 업그레이드 할시 
node agent 다시 뜨게 해야 아구가 맞음



# liveprobness process 항목 설정 

processAgent:
    enabled: true
    processCollection: true      # 반드시 true여야 인자값 수집 및 마스킹이 동작합니다
    processDiscovery: true
    runInCoreAgent: true
    containerCollection: true
    
# 아래 항목들을 직접 수동으로 추가하세요
    scrubArgs: true              # 강의의 scrub_args와 동일 (인자값 마스킹 활성화)
    customSensitiveWords:        # >> 강의의 custom_sensitive_words와 동일
      - "password"
      - "token"
      - "api_key"
      - "secret"



# custom metrics , app 

    공부를 위해서 구조만 파악(올드한 개발방식) 요새는 ddtrace 라이브러리 통해서 하는것이 추새



# event log
datadog:
  logs:
    enabled: true
    containerCollectAll: true # 모든 컨테이너 로그 자동 수집

datadog:
  confd:
# 예시 1: 특정 컨테이너 로그 설정을 강제하고 싶을 때
    kubernetes_state_core.yaml: |-
      logs:
        - type: docker  
          source: kubernetes
          service: my-app
          tags: ["env:prod"]

# 예시 2: 특정 파일 경로의 로그를 수집하고 싶을 때
    custom_log.yaml: |-
      logs:
        - type: file
          path: /var/log/my-app/*.log
          service: my-python-app
          source: python
          tags: ["env:dev", "type:custom"]



## apm

  애플리케이션의 성능을 실시간으로 추적하고 최적화하기 위한 모니터링 솔루션입니다. 
  분산된 환경(마이크로서비스, 클라우드 등)에서 요청이 어떻게 처리되는지 가시성을 제공하여 장애 원인을 빠르게 파악

  분산 트레이싱 (Distributed Tracing): 사용자 요청이 여러 서비스(프론트엔드 -> 백엔드 -> DB)를 거치는 전체 경로를 시각화하고, 어느 단계에서 지연이 발생하는지 확인합니다.

  성능 지표 수집: Latency(응답 속도), Errors(에러율), Throughput(처리량) 등 핵심 지표를 실시간 대시보드로 제공합니다.

  코드 레벨 분석: 특정 요청이 느린 이유가 어떤 함수나 SQL 쿼리 때문인지 코드 단위까지 파고들어 분석(Profiling)할 수 있습니다.

  서비스 맵 (Service Map): 서비스 간의 의존 관계를 자동으로 그려주어 전체 시스템 구조를 한눈에 파악하게 합니다.


\