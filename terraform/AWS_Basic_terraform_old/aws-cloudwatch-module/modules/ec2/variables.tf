variable "environment" {
  description = "Environment name used as prefix"
  type        = string
}

variable "ami_id" {
  description = "AMI ID for EC2 instances"
  type        = string
}

variable "instance_type" {
  description = "EC2 Instance Type"
  type        = string
  default     = "t3.micro"
}

variable "instance_keypair" {
  description = "AWS EC2 Key pair name"
  type        = string
  default     = "terraform-key"
}

variable "private_instance_count" {
  description = "AWS EC2 Private Instances Count"
  type        = number
  default     = 1
}

variable "vpc_id" {
  description = "VPC ID (for depends_on)"
  type        = string
}

variable "public_subnet_id" {
  description = "Public subnet ID for Bastion"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for app instances"
  type        = list(string)
}

variable "bastion_sg_id" {
  description = "Security group ID for Bastion host"
  type        = string
}

variable "private_sg_id" {
  description = "Security group ID for private instances"
  type        = string
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
}

variable "app1_user_data" {
  description = "User data script content for app1"
  type        = string
  default     = ""
}

variable "app2_user_data" {
  description = "User data script content for app2"
  type        = string
  default     = ""
}

variable "app3_user_data" {
  description = "User data script content for app3 (e.g. template-rendered)"
  type        = string
  default     = ""
}

variable "rds_db_endpoint" {
  description = "RDS DB endpoint for app3 (optional)"
  type        = string
  default     = ""
}
