variable "zone_id" {
  description = "Route53 hosted zone ID"
  type        = string
}

variable "record_name" {
  description = "DNS record name (e.g. cloudwatch.devopsincloud.com)"
  type        = string
}

variable "alb_dns_name" {
  description = "ALB DNS name for alias target"
  type        = string
}

variable "alb_zone_id" {
  description = "ALB zone ID for alias target"
  type        = string
}
