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

variable "instance_type_list" {
  description = "EC2 instance type"
  type = list(string)
  default = ["t2.micro","t2.small","t2.large"]
}

variable "instance_type_map" {
  description = "EC2 instance map"
  type = map(string)
  default = {
    "dev" = "t2.micro"
    "qa" = "t2.small"
    "prod" = "t2.large"
  }
}

