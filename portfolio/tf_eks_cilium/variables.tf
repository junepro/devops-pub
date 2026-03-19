variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name prefix"
  type        = string
  default     = "demo"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "cluster_version" {
  description = "EKS Kubernetes version"
  type        = string
  default     = "1.34"
}

variable "vpc_cidr" {
  description = "VPC CIDR"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnets" {
  description = "Public subnet CIDRs"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnets" {
  description = "Private subnet CIDRs"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

variable "node_instance_types" {
  description = "Managed node group instance types"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "node_desired_size" {
  description = "Desired node count"
  type        = number
  default     = 2
}

variable "node_min_size" {
  description = "Minimum node count"
  type        = number
  default     = 2
}

variable "node_max_size" {
  description = "Maximum node count"
  type        = number
  default     = 2
}

variable "create_bastion" {
  description = "Whether to create a bastion EC2 instance"
  type        = bool
  default     = true
}

variable "bastion_instance_type" {
  description = "Bastion EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "bastion_allowed_cidrs" {
  description = "CIDRs allowed to access bastion SSH port"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "bastion_key_name" {
  description = "Existing AWS EC2 key pair name to attach to bastion. Leave null to create one from public_key_path"
  type        = string
  default     = null
}

variable "bastion_public_key_path" {
  description = "Local path to SSH public key file used when creating a new AWS key pair for bastion"
  type        = string
  default     = null
}

variable "bastion_ami_id" {
  description = "Optional custom AMI ID for bastion. If null, latest Ubuntu Server 22.04 LTS AMI is used"
  type        = string
  default     = null
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
  default     = {}
}

variable "istio_enabled" {
  description = "Enable Istio installation"
  type        = bool
  default     = true
}

variable "istio_version" {
  description = "Istio Helm chart version"
  type        = string
  default     = "1.29.1"
}

variable "istio_ingress_service_type" {
  description = "Istio ingressgateway service type"
  type        = string
  default     = "LoadBalancer"
}

variable "istio_ingress_annotations" {
  description = "Annotations for Istio ingressgateway service"
  type        = map(string)
  default     = {}
}