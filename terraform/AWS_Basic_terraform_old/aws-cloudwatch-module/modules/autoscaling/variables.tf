variable "ami_id" {
  description = "AMI ID for launch template"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "instance_keypair" {
  description = "EC2 key pair name"
  type        = string
  default     = "terraform-key"
}

variable "private_sg_id" {
  description = "Security group ID for ASG instances"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for ASG"
  type        = list(string)
}

variable "target_group_arn" {
  description = "ALB target group ARN to attach to ASG"
  type        = string
}

variable "alb_arn_suffix" {
  description = "ALB ARN suffix for target tracking policy"
  type        = string
}

variable "target_group_arn_suffix" {
  description = "Target group ARN suffix for target tracking policy"
  type        = string
}

variable "launch_template_user_data_base64" {
  description = "User data for launch template (base64 encoded)"
  type        = string
}

variable "sns_notification_email" {
  description = "Email for ASG SNS notifications"
  type        = string
  default     = "''"
}

variable "sns_topic_suffix" {
  description = "Suffix for SNS topic name (e.g. random_pet id)"
  type        = string
}

variable "common_tags" {
  description = "Common tags"
  type        = map(string)
  default     = {}
}
