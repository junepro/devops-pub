variable "cluster_name" {
  type = string
}

variable "cluster_oidc_arn" {
  type = string
}

variable "cluster_oidc_url" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "region" {
  type = string
}

variable "tags" {
  type = map(string)
}
