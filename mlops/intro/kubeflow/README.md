1. 정의 및 목적

    Kubeflow는 쿠버네티스(Kubernetes) 환경에서 머신러닝(ML) 워크플로우를 구축, 배포, 관리하기 위한 오픈소스 클라우드 네이티브 플랫폼입니다. 머신러닝 모델의 개발부터 배포까지의 전 과정(End-to-End)을 자동화하고 확장성을 확보하는 MLOps의 핵심 도구로 사용됩니다.

2. 주요 특징

    이식성 (Portability): 로컬 PC, 온프레미스 서버, 클라우드(GCP, AWS, Azure) 등 쿠버네티스가 구동되는 곳이라면 어디서든 동일한 환경을 유지합니다.

    확장성 (Scalability): 쿠버네티스의 오케스트레이션 기능을 활용해 CPU, GPU, 메모리 자원을 동적으로 할당하고 확장합니다.

    구성 가능성 (Composability): 여러 독립적인 마이크로서비스 컴포넌트로 구성되어 있어, 필요한 기능만 선택하거나 외부 도구와 연동하기 쉽습니다.

3. 핵심 구성 요소 (Key Components)

    Central Dashboard: 모든 Kubeflow 컴포넌트에 접근할 수 있는 통합 웹 인터페이스(UI)입니다.

    Kubeflow Notebooks: 데이터 사이언티스트가 Jupyter Notebook, VS Code, RStudio 환경에서 직접 코드를 작성하고 실험할 수 있게 지원합니다.

    Kubeflow Pipelines (KFP): 머신러닝 워크플로우를 재사용 가능한 컨테이너 단위로 정의하고 실행, 관리하는 엔진입니다. (DAG 방식의 자동화)

    Katib: 하이퍼파라미터 튜닝(Hyperparameter Tuning) 및 신경망 구조 탐색(NAS)을 자동화하여 모델 성능을 최적화합니다.

    Training Operator: TensorFlow, PyTorch, XGBoost 등 다양한 프레임워크의 분산 학습(Distributed Training)을 관리합니다.

    KServe (formerly KFServing): 학습된 모델을 프로덕션 환경에 API 형태로 배포하고, 오토스케일링 및 카나리 배포 등을 지원하는 서빙 엔진입니다.

4. Kubeflow 기반의 ML 워크플로우


    실험 및 개발: Notebook 환경에서 데이터 탐색 및 모델 코드 작성.

    전처리 및 학습: Training Operator를 이용해 대규모 데이터를 분산 학습.

    최적화: Katib를 통해 가장 성능이 좋은 설정값(하이퍼파라미터) 탐색.

    자동화 파이프라인: 위 과정을 Pipelines로 구성하여 데이터 변경 시 자동 재학습 구조 구축.

    모델 배포: KServe를 통해 실시간 추론 서비스 제공.


5. 도입 시 장점

    인프라 관리 효율화: 데이터 사이언티스트가 복잡한 인프라 설정 없이 자원을 쉽게 할당받아 사용 가능합니다.

    재현성 확보: 모든 과정이 컨테이너화되어 있어, '내 PC에서는 되는데 서버에서는 안 되는' 문제를 해결합니다.

    협업 강화: 실험 결과와 파이프라인을 공유하여 팀 단위의 협업이 원활해집니다.


##  install 
## https://www.kubeflow.org/docs/components/pipelines/operator-guides/installation/
export PIPELINE_VERSION=2.14.3

kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION"
kubectl wait --for condition=established --timeout=60s crd/applications.app.k8s.io
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/dev?ref=$PIPELINE_VERSION" 


kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/platform-agnostic?ref=$PIPELINE_VERSION"


## svc connect
kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80


## 기타 설치 
## install Python kfp package
Create a folder - mkdir kfp
Create a Python virtual environment - python3 -m venv .kfp
Source the virtual environment - source .kfp/bin/activate
Install the package - pip3 install kfp==2.9.0