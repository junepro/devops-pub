output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "EKS cluster API endpoint"
  value       = module.eks.cluster_endpoint
}

output "cluster_oidc_issuer_url" {
  description = "OIDC issuer URL for the cluster"
  value       = module.eks.oidc_provider
}

# ALB URL is created by AWS Load Balancer Controller from Ingress.
# After apply, get it with: kubectl get ingress -n three-tier
output "configure_kubectl" {
  description = "Configure kubectl for EKS"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}

output "get_alb_hostname" {
  description = "Get ALB hostname after controller has created it"
  value       = "kubectl get ingress -n three-tier -o jsonpath='{.items[0].status.loadBalancer.ingress[0].hostname}'"
}
