terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  profile = "default"
  region = "ap-northeast-2"
}

resource "aws_instance" "ec2demo" {
  ami = "ami - basicinstance"
  instance_type = "t2.micro"
}

