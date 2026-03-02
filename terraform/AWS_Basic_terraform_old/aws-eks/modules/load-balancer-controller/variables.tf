variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
}

variable "oidc_provider_arn" {
  description = "OIDC provider ARN for IRSA"
  type        = string
}

variable "oidc_provider" {
  description = "OIDC provider host (e.g. oidc.eks.region.amazonaws.com/id/xxx)"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID (for controller to discover subnets)"
  type        = string
}

variable "namespace" {
  description = "Kubernetes namespace for the controller"
  type        = string
  default     = "kube-system"
}

variable "service_account_name" {
  description = "Service account name for the controller"
  type        = string
  default     = "aws-load-balancer-controller"
}
