from app import app

application = app


# WSGI란?
# **WSGI(Web Server Gateway Interface)**는 파이썬 애플리케이션이 웹 서버와 통신하기 위한 표준 약속입니다.

# 웹 서버 (예: Nginx): HTTP 요청을 받지만, 파이썬 코드를 직접 실행할 줄 모릅니다.

# 애플리케이션 (예: Flask): 파이썬 코드로직은 알지만, 대규모 인터넷 접속을 직접 처리하기엔 약합니다.

# WSGI (예: gunicorn, uWSGI): 이 둘 사이에서 통역사 역할을 합니다.


# 왜 사용하나요? (역할)
# 배포의 표준: 개발 환경에서는 python app.py로 서버를 띄우지만, 실제 서비스(운영 환경)에서는 안정성을 위해 gunicorn wsgi:application 명령어를 사용해 서버를 실행합니다.

# 진입점(Entry Point) 분리: 실제 서비스 로직이 담긴 app.py와 서버 실행을 위한 wsgi.py를 분리하여 관리함으로써 코드를 깔끔하게 유지합니다.