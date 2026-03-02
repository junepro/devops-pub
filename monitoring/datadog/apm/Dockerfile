FROM python:3.9-slim

WORKDIR /app

# 핵심: ddtrace 패키지를 직접 설치
RUN pip install --no-cache-dir flask flask-sqlalchemy ddtrace

COPY main.py .

EXPOSE 8000

# 핵심: 실행 시 ddtrace-run을 통해 앱을 래핑(Wrapping)함
ENTRYPOINT ["ddtrace-run"]
CMD ["python", "main.py"]