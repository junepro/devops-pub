# -----------------------------------------------------------------------------
# VPC Module
# -----------------------------------------------------------------------------
module "vpc" {
  source = "./modules/vpc"

  name_prefix                            = local.name
  vpc_name                               = var.vpc_name
  vpc_cidr_block                         = var.vpc_cidr_block
  vpc_availability_zones                 = var.vpc_availability_zones
  vpc_public_subnets                     = var.vpc_public_subnets
  vpc_private_subnets                    = var.vpc_private_subnets
  vpc_database_subnets                   = var.vpc_database_subnets
  vpc_create_database_subnet_group       = var.vpc_create_database_subnet_group
  vpc_create_database_subnet_route_table = var.vpc_create_database_subnet_route_table
  vpc_enable_nat_gateway                 = var.vpc_enable_nat_gateway
  vpc_single_nat_gateway                 = var.vpc_single_nat_gateway
  common_tags                            = local.common_tags
}

# -----------------------------------------------------------------------------
# Security Groups Module
# -----------------------------------------------------------------------------
module "security_groups" {
  source     = "./modules/security-groups"
  depends_on = [module.vpc]

  vpc_id         = module.vpc.vpc_id
  vpc_cidr_block = module.vpc.vpc_cidr_block
  common_tags    = local.common_tags
}

# -----------------------------------------------------------------------------
# ACM Module (depends on Route53 zone from data)
# -----------------------------------------------------------------------------
module "acm" {
  source = "./modules/acm"

  domain_name               = trimsuffix(data.aws_route53_zone.mydomain.name, ".")
  zone_id                   = data.aws_route53_zone.mydomain.zone_id
  subject_alternative_names = ["*.${trimsuffix(data.aws_route53_zone.mydomain.name, ".")}"]
  common_tags               = local.common_tags
}

# -----------------------------------------------------------------------------
# EC2 Module
# -----------------------------------------------------------------------------
module "ec2" {
  source     = "./modules/ec2"
  depends_on = [module.vpc, module.security_groups]

  environment            = var.environment
  ami_id                 = data.aws_ami.amzlinux2.id
  instance_type          = var.instance_type
  instance_keypair       = var.instance_keypair
  private_instance_count = var.private_instance_count
  vpc_id                 = module.vpc.vpc_id
  public_subnet_id       = module.vpc.public_subnets[0]
  private_subnet_ids     = module.vpc.private_subnets
  bastion_sg_id          = module.security_groups.public_bastion_sg_id
  private_sg_id          = module.security_groups.private_sg_id
  common_tags            = local.common_tags

  app1_user_data  = file("${path.module}/app1-install.sh")
  app2_user_data  = fileexists("${path.module}/app2-install.sh") ? file("${path.module}/app2-install.sh") : ""
  app3_user_data  = fileexists("${path.module}/app3-ums-install.tmpl") ? templatefile("${path.module}/app3-ums-install.tmpl", { rds_db_endpoint = var.rds_db_endpoint }) : ""
  rds_db_endpoint = var.rds_db_endpoint
}

# -----------------------------------------------------------------------------
# Elastic IP for Bastion (at root - references EC2 module)
# -----------------------------------------------------------------------------
resource "aws_eip" "bastion_eip" {
  depends_on = [module.ec2, module.vpc]
  instance   = module.ec2.bastion_instance_id
  domain     = "vpc"
  tags       = local.common_tags

  provisioner "local-exec" {
    command     = "echo Destroy time prov `date` >> destroy-time-prov.txt"
    working_dir = "local-exec-output-files/"
    when        = destroy
  }
}

# -----------------------------------------------------------------------------
# Null Resource - Bastion provisioners (at root for private_key path)
# -----------------------------------------------------------------------------
resource "null_resource" "name" {
  depends_on = [module.ec2, aws_eip.bastion_eip]

  connection {
    type        = "ssh"
    host        = aws_eip.bastion_eip.public_ip
    user        = "ec2-user"
    private_key = file("${path.module}/private-key/terraform-key.pem")
  }

  provisioner "file" {
    source      = "${path.module}/private-key/terraform-key.pem"
    destination = "/tmp/terraform-key.pem"
  }

  provisioner "remote-exec" {
    inline = ["sudo chmod 400 /tmp/terraform-key.pem"]
  }

  provisioner "local-exec" {
    command     = "echo VPC created on `date` and VPC ID: ${module.vpc.vpc_id} >> creation-time-vpc-id.txt"
    working_dir = "local-exec-output-files/"
  }
}

# -----------------------------------------------------------------------------
# ALB Module
# -----------------------------------------------------------------------------
module "alb" {
  source     = "./modules/alb"
  depends_on = [module.vpc, module.security_groups, module.acm]

  name_prefix         = local.name
  vpc_id              = module.vpc.vpc_id
  public_subnet_ids   = module.vpc.public_subnets
  loadbalancer_sg_id  = module.security_groups.loadbalancer_sg_id
  acm_certificate_arn = module.acm.acm_certificate_arn
  common_tags         = local.common_tags
}

# -----------------------------------------------------------------------------
# Route53 DNS Record
# -----------------------------------------------------------------------------
module "route53" {
  source     = "./modules/route53"
  depends_on = [module.alb]

  zone_id      = data.aws_route53_zone.mydomain.zone_id
  record_name  = var.route53_record_name
  alb_dns_name = module.alb.dns_name
  alb_zone_id  = module.alb.zone_id
}

# -----------------------------------------------------------------------------
# Autoscaling Module (depends on ALB target group)
# -----------------------------------------------------------------------------
module "autoscaling" {
  source     = "./modules/autoscaling"
  depends_on = [module.vpc, module.security_groups, module.alb]

  ami_id                           = data.aws_ami.amzlinux2.id
  instance_type                    = var.instance_type
  instance_keypair                 = var.instance_keypair
  private_sg_id                    = module.security_groups.private_sg_id
  private_subnet_ids               = module.vpc.private_subnets
  target_group_arn                 = module.alb.target_groups["mytg1"].arn
  alb_arn_suffix                   = module.alb.arn_suffix
  target_group_arn_suffix          = module.alb.target_groups["mytg1"].arn_suffix
  launch_template_user_data_base64 = filebase64("${path.module}/app1-install.sh")
  sns_topic_suffix                 = random_pet.this.id
  sns_notification_email           = var.sns_notification_email
  common_tags                      = local.common_tags
}

# -----------------------------------------------------------------------------
# CloudWatch Module
# -----------------------------------------------------------------------------
module "cloudwatch" {
  source     = "./modules/cloudwatch"
  depends_on = [module.autoscaling]

  asg_name                   = module.autoscaling.autoscaling_group_name
  sns_topic_arn              = module.autoscaling.sns_topic_arn
  high_cpu_policy_arn        = module.autoscaling.high_cpu_policy_arn
  alb_arn_suffix             = module.alb.arn_suffix
  random_suffix              = random_pet.this.id
  synthetics_canary_zip_path = "${path.module}/sswebsite2/sswebsite2v1.zip"
  common_tags                = local.common_tags
}
