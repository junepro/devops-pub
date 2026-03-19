# EKS Terraform Example

구성:
- Region: us-east-1
- Worker Node: 2 x t3.medium
- CNI: AWS VPC CNI + Cilium chaining mode
- Storage: Amazon EBS CSI Driver
- Ingress: AWS Load Balancer Controller (ALB)
- Bastion: Public subnet EC2 1대 (SSH + SSM 가능)

## 실행 순서

```bash
terraform init
terraform plan -out tfplan
terraform apply tfplan
```

## Bastion 사용 방식
- 퍼블릭 서브넷에 EC2 1대 생성
- SSH 22 포트는 `bastion_allowed_cidrs`로 제한
- `AmazonSSMManagedInstanceCore`를 붙여 Session Manager 접속도 가능
- `bastion_public_key_path`를 주면 AWS key pair를 생성하고, `bastion_key_name`을 주면 기존 key pair 사용

## 참고
- ALB Controller는 IRSA 기반 Helm 설치
- EBS CSI는 EKS managed addon
- Cilium은 aws-cni chaining mode 적용
- EKS API endpoint는 public access 기준

- Bastion IAM Role은 EKS Access Entry로 cluster admin 권한 예시를 부여
