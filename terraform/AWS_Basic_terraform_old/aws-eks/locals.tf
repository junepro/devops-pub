locals {
  name         = var.name_prefix
  region       = var.aws_region
  cluster_name = "${local.name}-${var.environment}"
  common_tags = {
    Environment = var.environment
    Terraform   = "true"
  }
}
