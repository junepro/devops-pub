## 개요

Kubecost는 쿠버네티스 클러스터 내에서 발생하는 비용을 실시간으로 모니터링, 분석 및 최적화할 수 있도록 돕는 오픈소스 기반 솔루션입니다. CNCF 샌드박스 프로젝트인 OpenCost를 기반으로 하며, 특히 AWS, GCP, Azure와 같은 클라우드 서비스 제공업체(CSP)의 실제 빌링 데이터를 연동하여 매우 정확한 비용 산출이 가능합니다.

주요 기능
비용 할당(Cost Allocation): 네임스페이스, 서비스, 파드, 배포 단위 및 사용자 정의 레이블별로 비용을 세분화하여 측정합니다.

통합 모니터링: 클러스터 내부 리소스뿐만 아니라 로드 밸런서, 스토리지 등 클러스터 외부의 클라우드 자산 비용도 함께 관리합니다.

최적화 인사이트: 리소스 사용률(CPU/RAM)을 분석하여 오버 프로비저닝된 워크로드를 식별하고, 적정 크기(Right-sizing) 권장안을 제시합니다.

거버넌스 및 알림: 예산 임계치 초과 시 Slack이나 이메일로 알림을 보냅니다.

## 설치  

  helm upgrade --install kubecost kubecost/cost-analyzer \                                 

    --namespace kubecost \

    --version 2.8.6 \

    -f values.yaml

