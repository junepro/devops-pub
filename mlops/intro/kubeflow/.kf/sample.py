from kfp import dsl
from kfp import compiler

# 1. 컴포넌트 정의 (Task 단위)
# @dsl.component 데코레이터를 사용하여 일반 파이썬 함수를 Kubeflow 컴포넌트로 변환합니다.
@dsl.component
def add_op(a: float, b: float) -> float:
    """두 숫자를 더하는 간단한 컴포넌트"""
    return a + b

# 2. 파이프라인 정의 (Workflow 단위)
# 정의한 컴포넌트들을 연결하여 전체 작업 흐름을 구성합니다.
@dsl.pipeline(
    name='my-first-pipeline',
    description='A simple pipeline that adds numbers.'
)
def addition_pipeline(x: float, y: float):
    # 첫 번째 더하기 작업
    task1 = add_op(a=x, b=y)
    
    # 두 번째 더하기 작업 (task1의 결과에 10을 더함)
    task2 = add_op(a=task1.output, b=10.0)

# 3. 파이프라인 컴파일
# 작성한 코드를 Kubeflow가 이해할 수 있는 YAML 파일로 변환합니다.
if __name__ == '__main__':
    compiler.Compiler().compile(
        pipeline_func=addition_pipeline,
        package_path='addition_pipeline.yaml'
    )
    print("Pipeline compilation complete: addition_pipeline.yaml")


# 코드 상세 해설
# @dsl.component:

# 이 데코레이터는 파이썬 함수를 독립된 컨테이너 이미지로 패키징할 수 있게 해줍니다.

# 함수 내부에서 필요한 라이브러리가 있다면 base_image나 packages_to_install 인자를 통해 지정할 수 있습니다.

# @dsl.pipeline:

# 여러 컴포넌트 간의 데이터 의존성을 정의합니다.

# 위 예시에서 task2는 task1.output을 입력으로 받기 때문에, Kubeflow는 자동으로 task1이 완료된 후 task2를 실행합니다.

# compiler.Compiler().compile():

# 작성된 파이썬 코드를 Kubeflow Dashboard에 업로드할 수 있는 YAML 파일로 추출합니다.

# 생성된 addition_pipeline.yaml 파일을 Kubeflow UI의 'Pipelines' 메뉴에서 **[Upload Pipeline]**을 통해 등록할 수 있습니다.