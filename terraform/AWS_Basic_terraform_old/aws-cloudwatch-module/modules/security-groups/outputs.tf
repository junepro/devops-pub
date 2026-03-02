output "public_bastion_sg_id" {
  description = "The ID of the public bastion security group"
  value       = module.public_bastion_sg.security_group_id
}

output "public_bastion_sg_vpc_id" {
  description = "The VPC ID of the public bastion security group"
  value       = module.public_bastion_sg.security_group_vpc_id
}

output "public_bastion_sg_name" {
  description = "The name of the public bastion security group"
  value       = module.public_bastion_sg.security_group_name
}

output "private_sg_id" {
  description = "The ID of the private security group"
  value       = module.private_sg.security_group_id
}

output "private_sg_vpc_id" {
  description = "The VPC ID of the private security group"
  value       = module.private_sg.security_group_vpc_id
}

output "private_sg_name" {
  description = "The name of the private security group"
  value       = module.private_sg.security_group_name
}

output "loadbalancer_sg_id" {
  description = "The ID of the load balancer security group"
  value       = module.loadbalancer_sg.security_group_id
}
