# 환경 설정

  python3 - m venv .venv

  source .venv/bin/activate

  python3 -m pip install dvc

# dvc 설정

  dvc init

  dvc add data/wine_sample.csv >>. wine_sample.csv.dvc 파일 생성됨

  # dvc_s3 install

  python3 -m pip install dvc_s3
  
  # s3 생성 후 
  dvc remote add -d wineremote s3://주소
  
  dvc push





