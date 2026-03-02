variable "aws_region" {
  description = "Region in which AWS Resources to be created"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment Variable used as a prefix"
  type        = string
  default     = "dev"
}

variable "business_divsion" {
  description = "Business Division in the large organization this Infrastructure belongs"
  type        = string
  default     = "SAP"
}

# VPC
variable "vpc_name" {
  description = "VPC Name"
  type        = string
  default     = "myvpc"
}

variable "vpc_cidr_block" {
  description = "VPC CIDR Block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "vpc_availability_zones" {
  description = "VPC Availability Zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "vpc_public_subnets" {
  description = "VPC Public Subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
}

variable "vpc_private_subnets" {
  description = "VPC Private Subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "vpc_database_subnets" {
  description = "VPC Database Subnets"
  type        = list(string)
  default     = ["10.0.151.0/24", "10.0.152.0/24"]
}

variable "vpc_create_database_subnet_group" {
  description = "VPC Create Database Subnet Group"
  type        = bool
  default     = true
}

variable "vpc_create_database_subnet_route_table" {
  description = "VPC Create Database Subnet Route Table"
  type        = bool
  default     = true
}

variable "vpc_enable_nat_gateway" {
  description = "Enable NAT Gateways for Private Subnets"
  type        = bool
  default     = true
}

variable "vpc_single_nat_gateway" {
  description = "Single NAT Gateway for all private subnets"
  type        = bool
  default     = true
}

# EC2
variable "instance_type" {
  description = "EC2 Instance Type"
  type        = string
  default     = "t3.micro"
}

variable "instance_keypair" {
  description = "AWS EC2 Key pair that need to be associated with EC2 Instance"
  type        = string
  default     = "terraform-key"
}

variable "private_instance_count" {
  description = "AWS EC2 Private Instances Count"
  type        = number
  default     = 1
}

variable "rds_db_endpoint" {
  description = "RDS DB endpoint for app3 (optional, set when RDS module is used)"
  type        = string
  default     = ""
  sensitive   = true
}

# Route53
variable "route53_zone_name" {
  description = "Route53 hosted zone name (e.g. devopsincloud.com)"
  type        = string
  default     = "devopsincloud.com"
}

variable "route53_record_name" {
  description = "DNS record name for the app (e.g. cloudwatch.devopsincloud.com)"
  type        = string
  default     = "cloudwatch.devopsincloud.com"
}

# Autoscaling / SNS
variable "sns_notification_email" {
  description = "Email for ASG/SNS notifications"
  type        = string
  default     = "''"
}
