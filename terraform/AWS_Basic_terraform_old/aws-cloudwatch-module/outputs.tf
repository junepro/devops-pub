# Data / Route53
output "mydomain_zoneid" {
  description = "The Hosted Zone id of the desired Hosted Zone"
  value       = data.aws_route53_zone.mydomain.zone_id
}

output "mydomain_name" {
  description = "The Hosted Zone name of the desired Hosted Zone"
  value       = data.aws_route53_zone.mydomain.name
}

# VPC
output "vpc_id" {
  description = "The ID of the VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "The CIDR block of the VPC"
  value       = module.vpc.vpc_cidr_block
}

output "private_subnets" {
  description = "List of IDs of private subnets"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "List of IDs of public subnets"
  value       = module.vpc.public_subnets
}

output "nat_public_ips" {
  description = "List of public Elastic IPs created for AWS NAT Gateway"
  value       = module.vpc.nat_public_ips
}

output "azs" {
  description = "A list of availability zones"
  value       = module.vpc.azs
}

# Security Groups
output "public_bastion_sg_group_id" {
  description = "The ID of the public bastion security group"
  value       = module.security_groups.public_bastion_sg_id
}

output "private_sg_group_id" {
  description = "The ID of the private security group"
  value       = module.security_groups.private_sg_id
}

# EC2
output "ec2_bastion_public_instance_ids" {
  description = "Bastion EC2 instance ID"
  value       = module.ec2.bastion_instance_id
}

output "ec2_bastion_public_ip" {
  description = "Bastion EC2 public IP"
  value       = module.ec2.bastion_public_ip
}

# ACM
output "this_acm_certificate_arn" {
  description = "The ARN of the certificate"
  value       = module.acm.acm_certificate_arn
}

# ALB
output "lb_id" {
  description = "The ID of the load balancer"
  value       = module.alb.id
}

output "lb_dns_name" {
  description = "The DNS name of the load balancer"
  value       = module.alb.dns_name
}

output "lb_arn_suffix" {
  description = "ARN suffix of our load balancer - can be used with CloudWatch"
  value       = module.alb.arn_suffix
}

output "target_groups" {
  description = "Map of target groups created and their attributes"
  value       = module.alb.target_groups
}

# Autoscaling
output "autoscaling_group_id" {
  description = "Autoscaling Group ID"
  value       = module.autoscaling.autoscaling_group_id
}

output "autoscaling_group_name" {
  description = "Autoscaling Group Name"
  value       = module.autoscaling.autoscaling_group_name
}

output "launch_template_id" {
  description = "Launch Template ID"
  value       = module.autoscaling.launch_template_id
}
