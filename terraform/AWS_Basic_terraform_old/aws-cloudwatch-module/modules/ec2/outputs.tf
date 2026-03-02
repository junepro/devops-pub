output "bastion_instance_id" {
  description = "Bastion EC2 instance ID"
  value       = module.ec2_public.id
}

output "bastion_public_ip" {
  description = "Bastion EC2 public IP"
  value       = module.ec2_public.public_ip
}

output "app1_instance_ids" {
  description = "List of app1 instance IDs"
  value       = module.ec2_private_app1.id
}

output "app2_instance_ids" {
  description = "List of app2 instance IDs"
  value       = module.ec2_private_app2.id
}

output "app3_instance_ids" {
  description = "List of app3 instance IDs"
  value       = module.ec2_private_app3.id
}
