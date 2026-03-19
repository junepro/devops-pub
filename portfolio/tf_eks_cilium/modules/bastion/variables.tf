variable "name" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "public_subnet_id" {
  type = string
}

variable "cluster_name" {
  type = string
}

variable "cluster_endpoint" {
  type = string
}

variable "cluster_version" {
  type = string
}

variable "allowed_cidrs" {
  type = list(string)
}

variable "instance_type" {
  type = string
}

variable "key_name" {
  type    = string
  default = null
}

variable "public_key_path" {
  type    = string
  default = null
}

variable "ami_id" {
  type    = string
  default = null
}

variable "tags" {
  type = map(string)
}

variable "aws_region" {
  type = string
}
