variable "domain_name" {
  description = "Domain name (without trailing dot)"
  type        = string
}

variable "zone_id" {
  description = "Route53 hosted zone ID for DNS validation"
  type        = string
}

variable "subject_alternative_names" {
  description = "List of SANs for the certificate"
  type        = list(string)
  default     = []
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
}
