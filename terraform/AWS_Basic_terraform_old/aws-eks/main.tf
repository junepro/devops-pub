# -----------------------------------------------------------------------------
# VPC (EKS + ALB subnet tags)
# -----------------------------------------------------------------------------
module "vpc" {
  source = "./modules/vpc"

  name_prefix        = local.name
  cluster_name       = local.cluster_name
  vpc_cidr           = var.vpc_cidr
  azs                = var.azs
  private_subnets    = var.private_subnets
  public_subnets     = var.public_subnets
  enable_nat_gateway = true
  single_nat_gateway = true
  tags               = local.common_tags
}

# -----------------------------------------------------------------------------
# EKS Cluster + Node Group
# -----------------------------------------------------------------------------
module "eks" {
  source = "./modules/eks"

  cluster_name       = local.cluster_name
  cluster_version    = var.cluster_version
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnets
  enable_irsa        = true

  node_groups = {
    default = {
      min_size       = var.node_min_size
      max_size       = var.node_max_size
      desired_size   = var.node_desired_size
      instance_types = var.node_instance_types
    }
  }
  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# AWS Load Balancer Controller - IAM (IRSA)
# -----------------------------------------------------------------------------
module "load_balancer_controller" {
  source = "./modules/load-balancer-controller"

  cluster_name         = module.eks.cluster_name
  oidc_provider_arn    = module.eks.oidc_provider_arn
  oidc_provider        = module.eks.oidc_provider
  vpc_id               = module.vpc.vpc_id
  namespace            = "kube-system"
  service_account_name = "aws-load-balancer-controller"
}

# -----------------------------------------------------------------------------
# Kubernetes & Helm providers (use EKS cluster auth)
# -----------------------------------------------------------------------------
data "aws_eks_cluster" "this" {
  name = module.eks.cluster_name
  depends_on = [module.eks]
}

data "aws_eks_cluster_auth" "this" {
  name = module.eks.cluster_name
}

provider "kubernetes" {
  host                   = data.aws_eks_cluster.this.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.this.certificate_authority[0].data)
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", data.aws_eks_cluster.this.name]
  }
}

provider "helm" {
  kubernetes  {
    host                   = data.aws_eks_cluster.this.endpoint
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.this.certificate_authority[0].data)
    exec  {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args        = ["eks", "get-token", "--cluster-name", data.aws_eks_cluster.this.name]
    }
  }
}

# -----------------------------------------------------------------------------
# AWS Load Balancer Controller - Helm install
# -----------------------------------------------------------------------------
resource "helm_release" "aws_load_balancer_controller" {
  name       = "aws-load-balancer-controller"
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  namespace  = "kube-system"
  version    = "1.6.2"

  set {
    name  = "clusterName"
    value = module.eks.cluster_name
  }
  set {
    name  = "serviceAccount.create"
    value = "true"
  }
  set {
    name  = "serviceAccount.name"
    value = module.load_balancer_controller.service_account_name
  }
  set {
    name  = "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
    value = module.load_balancer_controller.role_arn
  }
  set {
    name  = "vpcId"
    value = module.vpc.vpc_id
  }
  set {
    name  = "region"
    value = var.aws_region
  }
}

# -----------------------------------------------------------------------------
# 3-Tier App (Web / App / Data) + Ingress ALB
# -----------------------------------------------------------------------------
module "three_tier_app" {
  source     = "./modules/three-tier-app"
  depends_on = [helm_release.aws_load_balancer_controller]

  namespace                  = "three-tier"
  ingress_class              = "alb"
  lb_controller_sa_name      = module.load_balancer_controller.service_account_name
  lb_controller_sa_namespace = module.load_balancer_controller.namespace
  tags                       = local.common_tags
}
