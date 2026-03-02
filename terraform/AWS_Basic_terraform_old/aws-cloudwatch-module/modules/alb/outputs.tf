output "id" {
  description = "The ID of the load balancer"
  value       = module.alb.id
}

output "arn" {
  description = "The ARN of the load balancer"
  value       = module.alb.arn
}

output "dns_name" {
  description = "The DNS name of the load balancer"
  value       = module.alb.dns_name
}

output "arn_suffix" {
  description = "ARN suffix of the load balancer - can be used with CloudWatch"
  value       = module.alb.arn_suffix
}

output "zone_id" {
  description = "The zone_id of the load balancer"
  value       = module.alb.zone_id
}

output "listener_rules" {
  description = "Map of listeners rules created and their attributes"
  value       = module.alb.listener_rules
}

output "listeners" {
  description = "Map of listeners created and their attributes"
  value       = module.alb.listeners
}

output "target_groups" {
  description = "Map of target groups created and their attributes"
  value       = module.alb.target_groups
}
