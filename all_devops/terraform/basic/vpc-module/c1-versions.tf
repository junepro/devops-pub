terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.0"
    }
  }
# Remote Backend
  backend "s3" {
    bucket = "terraform-demo-study"
    key = "vpc/dev/terraform.tfstate"
    region = "ap-northeast-2"
    encrypt = true
    use_lockfile = true
  }
}

provider "aws" {
  region = var.aws_region
}