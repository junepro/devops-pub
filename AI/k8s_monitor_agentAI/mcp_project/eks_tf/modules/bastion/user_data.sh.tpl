#!/bin/bash
set -e
exec > >(tee /var/log/user-data.log | logger -t user-data) 2>&1

echo "====== Bastion (Ubuntu 22.04) 초기 설정 시작 ======"

# 패키지 업데이트
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get upgrade -y
apt-get install -y git curl unzip tar ca-certificates gnupg lsb-release

# Python 3.11
apt-get install -y python3.11 python3.11-venv python3-pip
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
python3 --version

# Node.js 18
mkdir -p /etc/apt/keyrings
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
  | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_18.x nodistro main" \
  | tee /etc/apt/sources.list.d/nodesource.list
apt-get update -y
apt-get install -y nodejs
node --version

# kubectl
KUBECTL_VER=$(curl -L -s https://dl.k8s.io/release/stable.txt)
curl -LO "https://dl.k8s.io/release/$${KUBECTL_VER}/bin/linux/amd64/kubectl"
install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
rm -f kubectl
kubectl version --client

# AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -q awscliv2.zip
./aws/install
rm -rf awscliv2.zip aws/
aws --version

# EKS kubeconfig 등록 (ubuntu 기본 유저: ubuntu)
mkdir -p /home/ubuntu/.kube
aws eks update-kubeconfig \
  --region ${aws_region} \
  --name ${eks_cluster_name} \
  --kubeconfig /home/ubuntu/.kube/config || true
chown -R ubuntu:ubuntu /home/ubuntu/.kube

# k8s-mcp-slack 작업 디렉토리 생성
mkdir -p /home/ubuntu/k8s-mcp-slack
chown ubuntu:ubuntu /home/ubuntu/k8s-mcp-slack

echo "====== Bastion 초기 설정 완료 ======"
echo "접속: ssh -i <key>.pem ubuntu@<IP>"
