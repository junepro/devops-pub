terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      # EKS 모듈 20.10의 launch_template이 elastic_gpu_specifications 등 사용 → AWS 5.x에서 제거됨. 4.x 사용
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0" # v3로 올라가지 않도록 고정
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Kubernetes & Helm providers are configured in main.tf after EKS cluster exists
# using data sources and exec-based auth
