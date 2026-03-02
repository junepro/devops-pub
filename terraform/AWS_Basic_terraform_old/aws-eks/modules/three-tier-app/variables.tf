variable "namespace" {
  description = "Kubernetes namespace for 3-tier app"
  type        = string
  default     = "three-tier"
}

variable "lb_controller_sa_name" {
  description = "AWS Load Balancer Controller service account name"
  type        = string
  default     = "aws-load-balancer-controller"
}

variable "lb_controller_sa_namespace" {
  description = "Namespace of the Load Balancer Controller"
  type        = string
  default     = "kube-system"
}

variable "ingress_class" {
  description = "Ingress class name for ALB"
  type        = string
  default     = "alb"
}

variable "tags" {
  description = "Tags for ALB (via ingress annotations)"
  type        = map(string)
  default     = {}
}
