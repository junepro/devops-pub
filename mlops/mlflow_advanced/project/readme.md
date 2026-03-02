## 아키텍처
![alt text](./실습image/arch.png)


## ec2 생성 후 

apt update 

apt install python3-pip

pip3 install pipenv virtualenv

mkdir mlflow

cd mlflow

pipenv install mlflow awscli boto3 setuptools

aws configure 

mlflow server -h 0.0.0.0 --backend-store-uri sqlite:///mlflow.db --default-artifact-root s3://mlflow-artifacts


## sagemaker 생성

레포 연결 
![alt text](./실습image/image2.png)
![alt text](./실습image/image1.png)

노트북 생성
![alt text](./실습image/image.png)
![alt text](./실습image/image-1.png)

주피터랩 
![alt text](./실습image/image-2.png)

터미널에서 mlflow 설치 및 python run.py
![alt text](./실습image/image-3.png)

![alt text](./실습image/image-4.png)


## deploy

python deploy.py 실행

![alt text](./실습image/image-5.png)

엔드포인트 생성됨
![alt text](./실습image/image-6.png)

테스트 실행
![alt text](./실습image/image-7.png)