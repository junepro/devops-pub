variable "aws_region" {
  description = " aws region created"
  type = string
  default = "us-east-1"
}

variable "instance_type" {
  description = "ec2 instance type"
  type = string
  default = "t2.micro"
}

variable "instance_keypair" {
  type = string
  default = "terraform-key"
}