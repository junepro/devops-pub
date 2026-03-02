# AWS EC2 Security Group Terraform Module
# Security Group for private ec2
module "private_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  #  version = "3.18.0"
  version = "5.1.0"

  name = "private-sg"
  description = "private block"
  vpc_id = module.vpc.vpc_id
  # Ingress Rules & CIDR Blocks
  ingress_rules = ["ssh-tcp","http-80-tcp"]
  ingress_cidr_blocks = [module.vpc.vpc_cidr_block]
  # Egress Rule - all-all open
  egress_rules = ["all-all"]
  tags = local.common_tags
}