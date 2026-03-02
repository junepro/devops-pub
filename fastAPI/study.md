python3 -m venv fastapi

source fastapienv/bin/activate

deactivate



pip install fastapi

pip install "uvicorn[standard]"

pip install sqlalchemy
 
pip install alembic  //Alembic은 파이썬의 대표적인 SQL 툴킷인 SQLAlchemy를 위한 데이터베이스 마이그레이션(Migration) 도구
                       데이터베이스의 버전 관리 시스템

pip install aiofiles

pip install jinja2

uvicorn books:app --reload

or

fastapi run books.py



# sqlite
     
    sqlite3 todo.db

    .schema


## 문법

 ** (Dictionary Unpacking) 연산자

    딕셔너리의 키(Key)와 값(Value) 쌍을 key=value 형태의 키워드 인자로 풀어헤칩니다.
    
    예: id=1, title='FastAPI', author='Roby', ...

 Optional[int]의 의미

    Optional: typing 모듈에서 제공하는 제네릭 타입입니다.
    **Union[int, None]**과 동일한 의미를 가집니다. 즉, "숫자가 들어와도 되지만, 아무것도 안 들어와도(None) 괜찮다"

 model_config

    Pydantic 모델의 설정 및 메타데이터를 정의하는 곳입니다. 여기서는 특히 **Swagger UI(문서화)**에서 사용자에게 보여줄 **입력 예시(Example)**를 설정하는 역할을 하고 있습니다.


    class BookRequest(BaseModel):
    id: Optional[int] = Field(description='ID is not needed on create', default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1999, lt=2031)
    
        model_config = {
            "json_schema_extra": {
                "example": {
                    "title": "A new book",
                    "author": "codingwithroby",
                    "description": "A new description of a book",
                    "rating": 5,
                    'published_date': 2029
                }
            }
        }
     

## alembic

   1. 초기화 (프로젝트 시작 시 1회)
      Alembic 설정 파일과 마이그레이션 폴더를 생성합니다.
   
   # 현재 디렉토리에 alembic 초기 설정 생성
   alembic init alembic
   
   2. 마이그레이션 파일 생성 (모델 변경 시)
      SQLAlchemy 모델(models.py)을 수정하거나 새로 만든 후, 변경 내역을 기록하는 파일을 만듭니다.
   
   # --autogenerate: 코드와 DB를 비교해서 자동으로 스크립트 작성
   # -m "메시지": 변경 내용에 대한 설명 추가
   alembic revision --autogenerate -m "create_users_table"
   
   3. 데이터베이스에 반영 (업그레이드)
      생성된 마이그레이션 스크립트를 실제 데이터베이스(PostgreSQL 등)에 적용합니다.
   
    최신 버전(head)까지 모든 변경 사항 적용
   alembic upgrade head
   
   # 특정 버전까지만 적용하고 싶을 때 (버전 ID 사용)
   alembic upgrade <revision_id>
   
   4. 이전 상태로 되돌리기 (다운그레이드)
      실수로 잘못 반영했거나 이전 구조로 돌아가야 할 때 사용합니다.
   
   # 바로 직전 단계로 되돌리기
   alembic downgrade -1
   
   # 아예 처음 상태(빈 DB)로 되돌리기
   alembic downgrade base
   
   5. 현재 상태 확인
      현재 DB가 어떤 버전인지, 어떤 이력이 있는지 확인합니다.
   
   # 현재 적용된 마이그레이션 버전 확인
   alembic current
   
   # 생성된 모든 마이그레이션 파일 목록 확인
   alembic history --verbose



