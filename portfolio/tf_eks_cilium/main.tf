locals {
  name = "${var.project_name}-${var.environment}"
  tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.tags
  )
}

module "vpc" {
  source = "./modules/vpc"

  name            = local.name
  vpc_cidr        = var.vpc_cidr
  public_subnets  = var.public_subnets
  private_subnets = var.private_subnets
  aws_region      = var.aws_region
  tags            = local.tags
}

module "eks" {
  source = "./modules/eks"

  name                = local.name
  cluster_version     = var.cluster_version
  subnet_ids          = module.vpc.private_subnet_ids
  vpc_id              = module.vpc.vpc_id
  node_instance_types = var.node_instance_types
  desired_size        = var.node_desired_size
  min_size            = var.node_min_size
  max_size            = var.node_max_size
  tags                = local.tags
}

module "bastion" {
  source = "./modules/bastion"
  count  = var.create_bastion ? 1 : 0

  name                = local.name
  vpc_id              = module.vpc.vpc_id
  public_subnet_id    = module.vpc.public_subnet_ids[0]
  cluster_name        = module.eks.cluster_name
  cluster_endpoint    = module.eks.cluster_endpoint
  cluster_version     = var.cluster_version
  allowed_cidrs       = var.bastion_allowed_cidrs
  instance_type       = var.bastion_instance_type
  key_name            = var.bastion_key_name
  public_key_path     = var.bastion_public_key_path
  ami_id              = var.bastion_ami_id
  aws_region          = var.aws_region
  tags                = local.tags

  depends_on = [module.eks]
}

resource "aws_eks_access_entry" "bastion" {
  count = var.create_bastion ? 1 : 0
  cluster_name  = module.eks.cluster_name
  principal_arn = module.bastion[0].iam_role_arn
  type          = "STANDARD"
}

resource "aws_eks_access_policy_association" "bastion_admin" {
  count = var.create_bastion ? 1 : 0
  cluster_name  = module.eks.cluster_name
  principal_arn = module.bastion[0].iam_role_arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"

  access_scope {
    type = "cluster"
  }
  depends_on = [aws_eks_access_entry.bastion]
}

module "ebs_csi" {
  source = "./modules/ebs-csi"

  cluster_name       = module.eks.cluster_name
  oidc_provider_arn  = module.eks.oidc_provider_arn
  oidc_provider_url  = module.eks.oidc_provider
  tags               = local.tags

  depends_on = [module.eks]
}

module "alb_controller" {
  source = "./modules/alb-controller"

  cluster_name      = module.eks.cluster_name
  cluster_oidc_arn  = module.eks.oidc_provider_arn
  cluster_oidc_url  = module.eks.oidc_provider
  vpc_id            = module.vpc.vpc_id
  region            = var.aws_region
  tags              = local.tags

  depends_on = [module.eks]
}

module "cilium" {
  source = "./modules/cilium"

  cluster_name = module.eks.cluster_name

  depends_on = [module.eks]
}
resource "aws_security_group_rule" "bastion_to_eks_api" {
  count = var.create_bastion ? 1 : 0

  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = module.eks.cluster_primary_security_group_id
  source_security_group_id = module.bastion[0].security_group_id
  description              = "Allow bastion to access EKS API"
}
# module "istio" {
#   source = "./modules/istio"

#   enabled = var.istio_enabled

#   cluster_name = module.eks.cluster_name

#   istio_version               = var.istio_version
#   ingress_service_type        = var.istio_ingress_service_type
#   ingress_service_annotations = var.istio_ingress_annotations

#   depends_on = [
#     module.eks,
#     module.cilium
#   ]
# }