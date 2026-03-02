# 'venv'라는 이름의 가상환경 생성
python3 -m venv venv

# 가상환경 활성화 (터미널 앞에 (venv)가 생깁니다)
source venv/bin/activate

pip install mlflow

VS Code 설정
VS Code에서 my-mlflow-project 폴더를 엽니다.

Cmd + Shift + P → Python: Select Interpreter 검색.

목록에서 ./venv/bin/python (우리가 방금 만든 가상환경)을 선택합니다.

종료 시 

deactivate

rm -rf venv  # 가상환경 폴더 삭제


# SQLite를 백엔드로 사용하는 MLflow 서버 실행 명령어

        mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlflow-artifacts --host 127.0.0.1 --port 5000

        mlflow server --backend-store-uri postgresql://user:password@postgres:5432/mlflowdb --default-artifact-root s3://bucket_name --host remote_host --no-serve-artifacts



        --backend-store-uri sqlite:///mlflow.db: 실험의 메타데이터(파라미터, 메트릭, 태그 등)를 저장할 데이터베이스를 지정합니다. sqlite:///파일명.db 형식을 사용하여 로컬에 SQLite 파일 생성 및 연결을 수행합니다.

        --default-artifact-root ./artifacts: 모델 파일, 이미지, 텍스트 파일 등 무거운 결과물(Artifacts)이 저장될 로컬 디렉토리를 지정합니다.


    mlflow server \
        --artifacts-only \
        --default-artifact-root s3://my-mlflow-bucket \
        --host 0.0.0.0 \
        --port 5001

        --artifacts-only 플래그를 사용하면, 서버가 실험 수치나 파라미터 기록 기능은 끄고, 오직 아티팩트(파일)의 업로드/다운로드 통로 역할만 수행하게 됩니다.

## 함수 

1. 실험 및 실행 관리 (Setup & Run)

    mlflow.set_tracking_uri()

        설명: 데이터가 저장될 서버 주소를 설정합니다. (설정 안 할 시 로컬 ./mlruns에 저장)

        파라미터: uri (예: "http://localhost:5000", "sqlite:///mlflow.db")


    mlflow.create_experiment() (추가됨)

        설명: 새로운 실험을 생성하며, 이때 결과물(Artifact) 저장 경로를 지정할 수 있습니다.

        파라미터: name, artifact_location (S3, GCS 경로 등)


    mlflow.set_experiment()

        설명: 현재 작업을 기록할 실험을 활성화합니다. (이름이 없으면 생성하지만, artifact_location 지정 불가)

        파라미터: experiment_name 또는 experiment_id

    mlflow.start_run() / mlflow.end_run()


        설명: 트래킹의 시작과 끝을 선언합니다. (with mlflow.start_run(): 권장)

        파라미터: run_name, nested (중첩 실행 허용 여부), tags

2. 데이터 기록 (Logging)

    mlflow.log_param() / mlflow.log_params()

        설명: 하이퍼파라미터(Learning Rate, Batch Size 등)를 기록합니다. (변경되지 않는 설정값)

        mlflow.log_metric() / mlflow.log_metrics()

        설명: 훈련 중 변하는 수치(Loss, Accuracy)를 기록합니다. step을 명시하여 시계열 차트를 그립니다.


    mlflow.log_artifact() / mlflow.log_artifacts()

        설명: 파일(이미지, CSV, Model File) 또는 디렉토리 전체를 저장소에 업로드합니다.


    mlflow.set_tag() / mlflow.set_tags()

        설명: 실행(Run)에 대한 메타데이터(버전, 작업자, 설명)를 Key-Value로 저장하여 검색에 활용합니다.

3. 자동화 및 모델 저장 (Models)

    mlflow.autolog()

        설명: 프레임워크별(Sklearn, XGBoost 등) 파라미터와 지표를 코드 한 줄로 자동 기록합니다.


    mlflow.<framework>.log_model()

        설  명: 모델 객체를 해당 프레임워크의 고유 포맷(Flavor)으로 저장합니다.

        파라미터: artifact_path (저장 폴더명), registered_model_name (지정 시 즉시 레지스트리에 등록)

    mlflow.pyfunc.log_model()


    설명: 사용자 정의 로직이 포함된 모델을 범용 Python 함수 형태로 저장합니다. (Docker 배포 등에 유리)


4. 모델 레지스트리 관리 (Model Registry & Client)

참고: 이 부분은 MlflowClient 객체가 필요할 수 있습니다.


    mlflow.register_model()

        설명: log_model로 저장된 실행(Run)의 모델 URI를 레지스트리에 등록하여 버전 관리를 시작합니다.

        파라미터: model_uri (runs:/<run_id>/model), name


    client.transition_model_version_stage()

        설명: 모델 버전의 단계를 변경합니다. (None → Staging → Production → Archived)


# MLflow Model component 요약 정리

1. MLflow Model이란? (Concept & Components)

    MLflow Model은 단순히 학습된 파일(.pkl, .h5 등)만 의미하는 것이 아니라, **"어디서든 실행 가능한 표준 패키지"**를 의미합니다.


    Model Flavor (플레이버): 모델을 읽어들이는 '방식'입니다.

        Native Flavor: 특정 라이브러리(Scikit-learn, PyTorch 등) 전용 방식.

        Python Function (pyfunc): 모든 모델을 predict()라는 공통된 파이썬 함수 형태로 감싸서, 어떤 도구에서도 동일하게 실행하게 해주는 추상화 계층입니다.

    Storage Format (저장 구조): 모델 저장 시 하나의 디렉토리가 생성되며 아래 파일들이 포함됩니다.

        MLmodel: 모델의 메타데이터(Flavor 정보, 생성 시간 등)가 담긴 핵심 YAML 파일.

        model.pkl: 실제 모델 객체.

        conda.yaml / requirements.txt: 모델 실행에 필요한 라이브러리 환경 설정.


2. Model Signature & Enforcement (입출력 정의)

    모델이 어떤 데이터를 받고 내뱉는지 명시하는 '규격'입니다.

    Model Signature: 입력 데이터의 컬럼명과 타입(int, float, string 등), 출력 데이터의 타입을 정의합니다.
    

    Signature Enforcement (강제화): * 모델 서빙(Serving) 시, 입력된 데이터가 정의된 스키마와 다르면 MLflow가 자동으로 오류를 발생시킵니다.

            이를 통해 잘못된 데이터로 인한 모델의 오작동(Garbage In, Garbage Out)을 방지합니다.


    Input Example: log_model 시 실제 데이터 샘플을 함께 넣어두면, MLflow가 이를 바탕으로 서명을 자동으로 유추하고 UI에서 테스트 데이터로 활용할 수 있게 해줍니다.

3. Log Signatures & Input Examples 

    서명과 예시 데이터를 모델과 함께 기록하는 실습 내용입니다.

    Input Example: 실제 데이터의 샘플을 함께 저장하여, 나중에 다른 사용자가 이 모델이 어떤 형태의 데이터를 받는지 UI에서 시각적으로 즉시 확인할 수 있게 합니다.

    방법: mlflow.sklearn.log_model(..., signature=signature, input_example=X_train[:5])와 같이 기록합니다.

#

MLflow Flavor 상세 설명

1. 왜 Flavor가 필요한가요?

    머신러닝 생태계에는 수많은 프레임워크가 존재합니다. 만약 Flavor가 없다면, 각 모델마다 불러오는 코드를 다르게 작성해야 합니다.

    Scikit-learn: joblib.load()

    PyTorch: torch.load()

    TensorFlow: tf.saved_model.load()

    MLflow는 이를 Flavor라는 이름으로 표준화하여, 어떤 라이브러리로 만들었든 동일한 인터페이스로 관리하게 해줍니다.

2. Flavor의 두 가지 계층 (Dual Flavors)

    MLflow 모델을 저장하면 보통 두 가지 이상의 Flavor가 동시에 MLmodel 파일에 기록됩니다.

    ① Native Flavor (프레임워크 전용)
        특징: 특정 라이브러리의 고유 기능을 그대로 유지합니다.

        예시: mlflow.sklearn, mlflow.pytorch, mlflow.xgboost 등.

        장점: 모델을 다시 불러왔을 때 원래 라이브러리의 메서드(예: sklearn의 feature_importances_)를 그대로 쓸 수 있습니다.

    ② PyFunc Flavor (범용 파이썬 함수)
        특징: 모든 모델을 predict() 메서드를 가진 파이썬 함수로 추상화합니다.

        예시: mlflow.pyfunc.

        장점: 모델이 무엇으로 만들어졌든 상관없이, 배포 도구(Docker, SageMaker 등)는 pyfunc.load_model() 하나만 알면 모든 모델을 실행할 수 있습니다.

# Model API

1. 모델 저장 API (log_model vs save_model)


    가장 자주 쓰이는 두 가지 API입니다.


    mlflow.<flavor>.log_model():

        설명: 현재 실행 중인 **MLflow Run(실험)**의 일부로 모델을 기록합니다.

        특징: 추적 서버(Tracking Server)에 모델 파일, 환경 설정, 메타데이터가 함께 업로드되어 UI에서 바로 확인 가능합니다.

        용도: 실험 과정에서 모델 성능을 비교하고 이력을 남길 때 사용합니다.


    mlflow.<flavor>.save_model():

        설명: 모델을 로컬 파일 시스템의 특정 경로에 저장합니다.

        특징: MLflow 실험(Run)과 연결되지 않고 독립적인 디렉토리로 생성됩니다.

        용도: 네트워크 연결 없이 모델 파일만 따로 보관하거나, 특정 경로로 모델을 내보낼 때 사용합니다.



2. 모델 불러오기 API (load_model)


    저장된 모델을 다시 파이썬 환경으로 가져와 예측에 사용합니다.

    mlflow.<flavor>.load_model(model_uri):

    설명: 특정 URI(경로 또는 Run ID)에 있는 모델을 원래의 프레임워크 객체(예: Scikit-learn 객체)로 불러옵니다.

    URI 형식: runs:/<run_id>/model 또는 models:/<model_name>/<version>.

    mlflow.pyfunc.load_model():

    설명: 모델을 'Generic Python Function' 형태로 불러옵니다.

    특징: 모델이 원래 무엇으로 만들어졌든 상관없이 predict()라는 통일된 인터페이스로 추론할 수 있게 해줍니다. (배포 시 매우 유용)



3. 스키마 관리 API (infer_signature)


    모델의 입력과 출력 규격을 정의할 때 사용합니다.

    mlflow.models.infer_signature(model_input, model_output):

    설명: 학습 데이터와 예측 결과 샘플을 넣어주면, MLflow가 자동으로 데이터 타입과 컬럼명을 분석해 **Signature(서명)**를 생성합니다.

    활용: log_model을 할 때 이 서명을 함께 저장하면, 나중에 잘못된 데이터가 들어왔을 때 API 수준에서 걸러낼 수 있습니다.


# cmd

mlflow doctor 상태 확인

mlflow doctor --mask-envs

mlflow artifacts list
                 download
                 log-artifacts 

mlflow db upgrade sqlite:///mlflow.db

mlflow experiments create --experiment-name cli_experiment

mlflow run list
           describe