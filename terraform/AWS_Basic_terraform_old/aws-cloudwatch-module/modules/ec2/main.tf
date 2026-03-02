module "ec2_public" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "5.6.0"

  name                   = "${var.environment}-BastionHost"
  ami                    = var.ami_id
  instance_type          = var.instance_type
  key_name               = var.instance_keypair
  subnet_id              = var.public_subnet_id
  vpc_security_group_ids = [var.bastion_sg_id]
  tags                   = var.common_tags
}

module "ec2_private_app1" {
  depends_on = [module.ec2_public]
  source     = "terraform-aws-modules/ec2-instance/aws"
  version    = "2.17.0"

  name                   = "${var.environment}-app1"
  ami                    = var.ami_id
  instance_type          = var.instance_type
  key_name               = var.instance_keypair
  vpc_security_group_ids = [var.private_sg_id]
  subnet_ids             = var.private_subnet_ids
  instance_count         = var.private_instance_count
  user_data              = var.app1_user_data
  tags                   = var.common_tags
}

module "ec2_private_app2" {
  depends_on = [module.ec2_public]
  source     = "terraform-aws-modules/ec2-instance/aws"
  version    = "2.17.0"

  name                   = "${var.environment}-app2"
  ami                    = var.ami_id
  instance_type          = var.instance_type
  key_name               = var.instance_keypair
  vpc_security_group_ids = [var.private_sg_id]
  subnet_ids             = var.private_subnet_ids
  instance_count         = var.private_instance_count
  user_data              = var.app2_user_data
  tags                   = var.common_tags
}

module "ec2_private_app3" {
  depends_on = [module.ec2_public]
  source     = "terraform-aws-modules/ec2-instance/aws"
  version    = "2.17.0"

  name                   = "${var.environment}-app3"
  ami                    = var.ami_id
  instance_type          = var.instance_type
  key_name               = var.instance_keypair
  vpc_security_group_ids = [var.private_sg_id]
  subnet_ids             = var.private_subnet_ids
  instance_count         = var.private_instance_count
  user_data              = var.app3_user_data
  tags                   = var.common_tags
}
