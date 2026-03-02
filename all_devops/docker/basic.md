# docker install 
   # 1. 시스템 업데이트 및 필수 패키지 설치
    sudo apt-get update
    sudo apt-get install ca-certificates curl gnupg

   # 2. Docker 공식 GPG 키 추가
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

   # 3. Docker 레포지토리 등록
    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

   # 4. Docker 엔진 설치
    sudo apt-get update
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

   # 5. 'docker' 그룹 생성 (이미 존재할 수 있음)
    sudo groupadd docker

   # 6. 현재 로그인한 사용자($USER)를 docker 그룹에 추가
    sudo usermod -aG docker $USER

   # 7. 그룹 변경 사항을 즉시 적용 (세션 재시작 대신 사용)
    newgrp docker 

   # 8. 확인 (sudo 없이 실행)
    docker ps    

   # 9. 설치 확인 (Hello World 실행)
    sudo docker run hello-world    


## Build the Docker Image
    docker build -t retail-ui:9.0.0 .

    docker build --no-cache -t retail-ui:9.0.0 .


## Run the Container
    docker run -d --name retail-ui -p 8080:8080 retail-ui:9.0.0

## Connect to Docker Container
    docker exec -it retail-ui sh

## Cleanup
    docker stop retail-ui
    docker rm retail-ui
    docker rmi retail-ui:9.0.0

## Remove ALL Build Cache (including unused images and layers)
    docker builder prune --all
    docker builder prune --all -f
    docker system prune -a --volumes -f


## Check Docker version
    docker version

## Log in to Docker Hub
    docker login

## To Logout from Docker Hub (Optional)
    docker logout


# Docker Compose Install 

    sudo mkdir -p /usr/local/lib/docker/cli-plugins

    wget https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -O docker-compose

    chmod +x docker-compose

    sudo mv docker-compose /usr/local/lib/docker/cli-plugins/docker-compose

    docker compose version

## start
    docker compose -f docker-compose.yaml up
    docker compose up 

## OR start in detached mode (background)
    docker compose -f docker-compose.yaml up -d
    docker compose up -d

## Stop all services (gracefully) (NOT NEEDED NOW - JUST FOR REFERENCE)
    docker compose down

## Verify if service is stopped
    docker compose ps
    docker compose ps -a

## Start a Service
    docker compose start orders

## Restart a Service
    docker compose restart cart

## Logs for all services
    docker compose logs

## Logs for a specific service
    docker compose logs checkout

## Follow logs
    docker compose logs -f checkout

## Connect to a Container
    docker compose exec ui sh

## Stats 
    docker compose stats

## Specific Containers
    docker compose stats ui


# buildx

## 1. Buildx 플러그인 설치 (Ubuntu 기준)
    sudo apt-get update
    sudo apt-get install docker-buildx-plugin

## 2. 현재 설치된 버전 확인
    docker buildx version

## 3. 멀티 아키텍처 빌드를 위한 'builder' 생성 및 선택
    docker buildx create --name mybuilder --use
    docker buildx inspect --bootstrap

## 한 번의 명령으로 Intel/AMD와 Apple Silicon(M1/M2)용 이미지를 동시 빌드 및 푸시
    docker buildx build \
    --platform linux/amd64,linux/arm64 \
    -t <내-도커허브-ID>/<이미지명>:<태그> \
    --push .    

## 빌드 확인
    docker buildx imagetools inspect <내-도커허브-ID>/<이미지명>:<태그>