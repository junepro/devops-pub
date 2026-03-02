# AWS EKS 3-Tier + ALB (Terraform)

EKS 클러스터와 **3티어(Web / App / Data)** 애플리케이션을 단일 **ALB(Application Load Balancer)** 로 노출하는 Terraform 구성입니다.

## 아키텍처

- **VPC**: EKS 및 ALB용 public/private 서브넷 (표준 EKS 서브넷 태그)
- **EKS**: Kubernetes **1.33** + 관리형 노드 그룹, IRSA 활성화
- **에드온 4종**: `vpc-cni`, `coredns`, `kube-proxy`, `aws-ebs-csi-driver` (최신 버전 자동 적용)
- **AWS Load Balancer Controller**: IRSA + Helm 설치, Ingress 리소스로 ALB 생성
- **3-Tier App**:
  - **Web Tier**: `nginx:alpine` (경로 `/`)
  - **App Tier**: `http-echo` API (경로 `/api`)
  - **Data Tier**: `http-echo` (경로 `/data`)

단일 ALB가 path 기반 라우팅으로 위 세 서비스로 트래픽을 분기합니다.

## 사전 요구사항

- Terraform >= 1.6
- AWS CLI 설정 (자격 증명, 리전)
- `kubectl` (ALB URL 확인용)

## 사용 방법

### 1. 변수 (선택)

`terraform.tfvars` 예시:

```hcl
aws_region   = "ap-northeast-2"
environment  = "dev"
name_prefix  = "eks-3tier"
```

### 2. 적용 (2단계 권장)

Kubernetes/Helm provider가 EKS 클러스터 정보에 의존하므로, **첫 적용은 인프라만** 적용한 뒤 **전체 적용**을 한 번 더 하는 것을 권장합니다.

```bash
# 1) VPC + EKS + LBC IAM만 먼저 적용
terraform init
terraform apply -target=module.vpc -target=module.eks -target=module.load_balancer_controller

# 2) 전체 적용 (Helm LBC + 3-tier 앱)
terraform apply
```

한 번에 적용해도 되지만, provider 초기화 순서에 따라 첫 실행에서 Helm/K8s 리소스 적용이 실패할 수 있으므로 위 2단계를 추천합니다.

### 3. kubectl 설정 및 ALB URL 확인

```bash
aws eks update-kubeconfig --region <region> --name <cluster_name>
kubectl get ingress -n three-tier
# ADDRESS 컬럼에 ALB DNS 이름이 생성되면 사용 가능
```

- `http://<ALB_DNS>/` → Web Tier (nginx)
- `http://<ALB_DNS>/api` → App Tier
- `http://<ALB_DNS>/data` → Data Tier

## 디렉터리 구조

```
aws-eks/
├── main.tf                 # 모듈 호출, provider, Helm, 3-tier 모듈
├── variables.tf
├── locals.tf
├── versions.tf
├── outputs.tf
├── README.md
└── modules/
    ├── vpc/                 # EKS용 VPC, 서브넷 태그
    ├── eks/                 # EKS 클러스터 + 노드 그룹
    ├── load-balancer-controller/  # LBC IRSA (IAM)
    └── three-tier-app/      # Web/App/Data Deployment, Service, Ingress(ALB)
```

## 이미지 변경

`modules/three-tier-app/main.tf`에서 각 Deployment의 `image`를 실제 사용할 이미지로 바꾸면 됩니다.
