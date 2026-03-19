variable "istio_version" {
  description = "Istio chart version"
  type        = string
}

variable "ingress_service_type" {
  description = "Kubernetes service type for Istio ingress gateway"
  type        = string
  default     = "LoadBalancer"
}

variable "ingress_annotations" {
  description = "Annotations for the Istio ingress gateway service"
  type        = map(string)
  default     = {}
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
  default     = {}
}

variable "enabled" {
  description = "Enable Istio installation"
  type        = bool
  default     = true
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
}

variable "ingress_service_annotations" {
  description = "Annotations for Istio ingressgateway service"
  type        = map(string)
  default     = {}
}