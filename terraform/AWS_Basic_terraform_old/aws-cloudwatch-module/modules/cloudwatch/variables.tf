variable "asg_name" {
  description = "Auto Scaling Group name for CPU alarm"
  type        = string
}

variable "sns_topic_arn" {
  description = "SNS topic ARN for alarm actions"
  type        = string
}

variable "high_cpu_policy_arn" {
  description = "ARN of high CPU scaling policy to trigger"
  type        = string
}

variable "alb_arn_suffix" {
  description = "ALB ARN suffix for 4xx alarm dimension"
  type        = string
}

variable "random_suffix" {
  description = "Random suffix for resource names (e.g. random_pet id)"
  type        = string
}

variable "synthetics_canary_zip_path" {
  description = "Path to synthetics canary zip file (relative to root module)"
  type        = string
  default     = "sswebsite2/sswebsite2v1.zip"
}

variable "common_tags" {
  description = "Common tags for resources"
  type        = map(string)
  default     = {}
}
