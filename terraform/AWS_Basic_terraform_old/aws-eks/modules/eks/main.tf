module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "20.10.0"

  cluster_name    = var.cluster_name
  cluster_version = var.cluster_version

  vpc_id     = var.vpc_id
  subnet_ids = var.private_subnet_ids

  enable_irsa = var.enable_irsa

  # 기본 에드온 4개: vpc-cni, coredns, kube-proxy, aws-ebs-csi-driver
  cluster_addons = {
    vpc-cni = {
      most_recent = true
    }
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }

  # EKS managed node groups (3-tier: default group for web/app/data)
  eks_managed_node_groups = length(var.node_groups) > 0 ? var.node_groups : {
    default = {
      min_size       = 2
      max_size       = 5
      desired_size   = 2
      instance_types = ["t3.medium"]
    }
  }

  # Cluster endpoint (public + private for private subnet nodes)
  cluster_endpoint_public_access  = true
  cluster_endpoint_private_access = true

  tags = var.tags
}
