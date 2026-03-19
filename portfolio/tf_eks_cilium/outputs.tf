output "cluster_name" {
  value = module.eks.cluster_name
}

output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "vpc_id" {
  value = module.vpc.vpc_id
}

output "private_subnet_ids" {
  value = module.vpc.private_subnet_ids
}

output "public_subnet_ids" {
  value = module.vpc.public_subnet_ids
}

output "bastion_public_ip" {
  value = var.create_bastion ? module.bastion[0].public_ip : null
}

output "bastion_private_ip" {
  value = var.create_bastion ? module.bastion[0].private_ip : null
}

output "bastion_security_group_id" {
  value = var.create_bastion ? module.bastion[0].security_group_id : null
}

output "bastion_key_name" {
  value = var.create_bastion ? module.bastion[0].key_name : null
}

# output "istio_ingress_namespace" {
#   value = module.istio.ingress_namespace
# }

# output "istio_ingress_release_name" {
#   value = module.istio.ingress_release_name
# }

# output "istio_version" {
#   value = module.istio.istio_version
# }