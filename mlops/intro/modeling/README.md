# Intent Classifier Model

This small project demonstrates:
- Training a tiny text classifier.
- Saving the model artifact.
- Serving predictions via a Flask API (`/predict`).

## Quick start (local)
1. Create a virtualenv and install:
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

2. Train the model:
    python model/train.py
    This will create `model/artifacts/intent_model.pkl`.

3. Run the API:
    python app.py
    The API will be available at http://127.0.0.1:6000

4. Example request:
    curl -X POST http://127.0.0.1:6000/predict -H "Content-Type: application/json" -d '{"text":"I want to cancel my subscription"}'

    Response:
    {
        "intent": "complaint",
        "probabilities": {"complaint": 0.85, "question": 0.05, ...}
    }

# wsgi.  실행

pip install gunicorn

 형식: gunicorn [파일이름]:[객체이름]
gunicorn wsgi:application

gunicorn --workers 3 --bind 0.0.0.0:8000 wsgi:application

--workers (또는 -w):서버를 몇 개의 프로세스로 띄울지 결정합니다.보통 (CPU 코어 수 $\times$ 2) + 1개를 권장합니다. (코어가 1개면 3개 설정)

--bind (또는 -b):접속을 허용할 IP와 포트 번호입니다. 0.0.0.0:8000은 모든 IP에서 8000번 포트로 들어오는 접속을 받겠다는 뜻입니다.

--timeout:응답이 너무 오래 걸릴 경우(예: 대용량 파일 업로드) 연결을 끊는 시간입니다. (기본 30초)