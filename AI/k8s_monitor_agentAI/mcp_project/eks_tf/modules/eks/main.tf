locals {
  name = "${var.project_name}-${var.environment}"
}

# ── 클러스터 IAM Role ─────────────────────────────────────────

resource "aws_iam_role" "cluster" {
  name = "${local.name}-eks-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "eks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "cluster_policy" {
  role       = aws_iam_role.cluster.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

resource "aws_iam_role_policy_attachment" "cluster_vpc_controller" {
  role       = aws_iam_role.cluster.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSVPCResourceController"
}

# ── 클러스터 Security Group ───────────────────────────────────

resource "aws_security_group" "cluster" {
  name        = "${local.name}-eks-cluster-sg"
  description = "EKS Cluster API Server Security Group"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Bastion to EKS API"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [var.bastion_sg_id]
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${local.name}-eks-cluster-sg"
  }
}

# ── EKS 클러스터 ──────────────────────────────────────────────

resource "aws_eks_cluster" "this" {
  name     = var.cluster_name
  version  = var.cluster_version
  role_arn = aws_iam_role.cluster.arn

  vpc_config {
    subnet_ids              = var.private_subnet_ids
    security_group_ids      = [aws_security_group.cluster.id]
    endpoint_private_access = true
    endpoint_public_access  = false
  }

  # ── 이 부분을 추가하세요 ─────────────────────────────────────
  lifecycle {
    ignore_changes = [
      access_config[0].authentication_mode,
    ]
  }
  # ──────────────────────────────────────────────────────────

  access_config {
    authentication_mode                         = "API_AND_CONFIG_MAP"
    bootstrap_cluster_creator_admin_permissions = true
  }

  # ── 이 부분을 빈 리스트로 수정하거나 삭제하세요 ──────────────
  enabled_cluster_log_types = [] 
  # ──────────────────────────────────────────────────────────

  depends_on = [
    aws_iam_role_policy_attachment.cluster_policy,
    aws_iam_role_policy_attachment.cluster_vpc_controller,
  ]
}
# ── 노드 IAM Role ─────────────────────────────────────────────

resource "aws_iam_role" "node" {
  name = "${local.name}-eks-node-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "node_worker" {
  role       = aws_iam_role.node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}

resource "aws_iam_role_policy_attachment" "node_cni" {
  role       = aws_iam_role.node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}

resource "aws_iam_role_policy_attachment" "node_ecr" {
  role       = aws_iam_role.node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

# ── EKS Add-ons ──────────────────────────────────────────────

# 1. VPC CNI (네트워크 통신용)
resource "aws_eks_addon" "vpc_cni" {
  cluster_name = aws_eks_cluster.this.name
  addon_name   = "vpc-cni"
  
  # 특정 버전을 지정하지 않으면 최신(Default) 버전이 설치됩니다.
  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "PRESERVE"
}

# 2. CoreDNS (클러스터 내 도메인 이름 해석용)
resource "aws_eks_addon" "coredns" {
  cluster_name = aws_eks_cluster.this.name
  addon_name   = "coredns"
  
  # CoreDNS는 노드가 준비되어야 실행되므로 노드 그룹 생성 후 배포되도록 설정
  depends_on = [aws_eks_node_group.this]
}

# 3. Kube-Proxy (네트워크 프록시)
resource "aws_eks_addon" "kube_proxy" {
  cluster_name = aws_eks_cluster.this.name
  addon_name   = "kube-proxy"
}

# # 4. EBS CSI Driver (EBS 볼륨 사용 시 필수)
# # 주의: 이 애드온은 노드 IAM Role에 AmazonEBSCSIDriverPolicy 권한이 있어야 작동합니다.
# resource "aws_eks_addon" "ebs_csi" {
#   cluster_name = aws_eks_cluster.this.name
#   addon_name   = "aws-ebs-csi-driver"
# }

# ── 노드 Security Group ───────────────────────────────────────

resource "aws_security_group" "node" {
  name        = "${local.name}-eks-node-sg"
  description = "EKS Node Security Group"
  vpc_id      = var.vpc_id

  ingress {
    description = "Node to node"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    self        = true
  }

  ingress {
    description     = "Cluster to node kubelet"
    from_port       = 10250
    to_port         = 10250
    protocol        = "tcp"
    security_groups = [aws_security_group.cluster.id]
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${local.name}-eks-node-sg"
  }
}

# ── 관리형 노드 그룹 ──────────────────────────────────────────

resource "aws_eks_node_group" "this" {
  cluster_name    = aws_eks_cluster.this.name
  node_group_name = "${local.name}-node-group"
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = var.private_subnet_ids

  instance_types = [var.node_instance_type]
  disk_size      = var.node_disk_size

  scaling_config {
    desired_size = var.node_desired_size
    min_size     = var.node_min_size
    max_size     = var.node_max_size
  }

  update_config {
    max_unavailable = 1
  }

  labels = {
    Environment = var.environment
    NodeGroup   = "main"
  }

  depends_on = [
    aws_iam_role_policy_attachment.node_worker,
    aws_iam_role_policy_attachment.node_cni,
    aws_iam_role_policy_attachment.node_ecr,
  ]

  lifecycle {
    ignore_changes = [scaling_config[0].desired_size]
  }
}

# ── OIDC Provider ─────────────────────────────────────────────

data "tls_certificate" "this" {
  url = aws_eks_cluster.this.identity[0].oidc[0].issuer
}

resource "aws_iam_openid_connect_provider" "this" {
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.this.certificates[0].sha1_fingerprint]
  url             = aws_eks_cluster.this.identity[0].oidc[0].issuer
}

# 1. 노드가 클러스터에 조인할 수 있도록 허용 (EC2_LINUX 타입)
# resource "aws_eks_access_entry" "node" {
#   cluster_name      = aws_eks_cluster.this.name
#   principal_arn     = aws_iam_role.node.arn # 기존 노드 IAM Role ARN
#   type              = "EC2_LINUX"
# }

# 2. 베스천 서버 IAM 역할을 관리자(Admin)로 등록
resource "aws_eks_access_entry" "bastion" {
  cluster_name      = aws_eks_cluster.this.name
  principal_arn     = var.bastion_role_arn # 기존 노드 IAM Role ARN
  type              = "STANDARD"
}

# 3. 베스천 서버에 ClusterAdmin 정책 부여
resource "aws_eks_access_policy_association" "bastion_admin" {
  cluster_name  = aws_eks_cluster.this.name
  # ── 아래 ARN에 오타나 앞뒤 공백이 없는지 확인하세요 ──────────
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
  # ──────────────────────────────────────────────────────
  principal_arn     = var.bastion_role_arn # 기존 노드 IAM Role ARN
  
  access_scope {
    type = "cluster"
  }
}