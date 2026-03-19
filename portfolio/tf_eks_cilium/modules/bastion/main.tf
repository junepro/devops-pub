locals {
  create_key_pair = var.key_name == null && var.public_key_path != null
  effective_key_name = var.key_name != null ? var.key_name : (local.create_key_pair ? aws_key_pair.this[0].key_name : null)
}

data "aws_ssm_parameter" "ubuntu_2204" {
  name = "/aws/service/canonical/ubuntu/server/22.04/stable/current/amd64/hvm/ebs-gp2/ami-id"
}

resource "aws_key_pair" "this" {
  count      = local.create_key_pair ? 1 : 0
  key_name   = "${var.name}-bastion-key"
  public_key = file(var.public_key_path)

  tags = merge(var.tags, {
    Name = "${var.name}-bastion-key"
  })
}

resource "aws_security_group" "this" {
  name_prefix = "${var.name}-bastion-"
  description = "Security group for bastion host"
  vpc_id      = var.vpc_id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.name}-bastion-sg"
  })
}

resource "aws_iam_role" "this" {
  name = "${var.name}-bastion-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.this.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "this" {
  name = "${var.name}-bastion-profile"
  role = aws_iam_role.this.name
}

resource "aws_iam_policy" "bastion_eks_describe" {
  name = "${var.name}-bastion-eks-describe"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "eks:DescribeCluster"
        ]
        Resource = "arn:aws:eks:${var.aws_region}:${data.aws_caller_identity.current.account_id}:cluster/${var.name}"
      }
    ]
  })
}

# resource "aws_iam_role_policy_attachment" "bastion_eks_describe_attach" {
#   role       = aws_iam_role.this.name
#   policy_arn = aws_iam_policy.bastion_eks_describe.arn
# }

resource "aws_iam_role_policy_attachment" "bastion_admin" {
  role       = aws_iam_role.this.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}
data "aws_caller_identity" "current" {}

resource "aws_instance" "this" {
  ami                         = coalesce(var.ami_id, data.aws_ssm_parameter.ubuntu_2204.value)
  instance_type               = var.instance_type
  subnet_id                   = var.public_subnet_id
  vpc_security_group_ids      = [aws_security_group.this.id]
  associate_public_ip_address = true
  iam_instance_profile        = aws_iam_instance_profile.this.name
  key_name                    = local.effective_key_name

  user_data = base64encode(<<-EOF
            #!/bin/bash
            set -euxo pipefail
            export DEBIAN_FRONTEND=noninteractive

            apt-get update -y
            apt-get upgrade -y
            apt-get install -y unzip tar gzip jq curl ca-certificates apt-transport-https gnupg lsb-release

            curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip"
            unzip -q /tmp/awscliv2.zip -d /tmp
            /tmp/aws/install --update

            curl -LO "https://dl.k8s.io/release/v${var.cluster_version}.0/bin/linux/amd64/kubectl"
            install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

            curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

            mkdir -p /home/ubuntu/.kube
            chown -R ubuntu:ubuntu /home/ubuntu/.kube

            cat >/etc/profile.d/eks_env.sh <<PROFILE
            export AWS_DEFAULT_REGION=${var.aws_region}
            PROFILE

            cat >/home/ubuntu/bootstrap-eks-access.sh <<SCRIPT
            #!/bin/bash
            set -euo pipefail
            rm -f /home/ubuntu/.kube/config
            aws eks update-kubeconfig --region ${var.aws_region} --name ${var.cluster_name}
            chown ubuntu:ubuntu /home/ubuntu/.kube/config
            SCRIPT

            chmod +x /home/ubuntu/bootstrap-eks-access.sh
            chown ubuntu:ubuntu /home/ubuntu/bootstrap-eks-access.sh
            EOF
  )

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  tags = merge(var.tags, {
    Name = "${var.name}-bastion"
  })
}
