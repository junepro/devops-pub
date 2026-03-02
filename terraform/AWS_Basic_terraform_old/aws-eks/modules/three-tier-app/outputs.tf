output "namespace" {
  description = "Namespace of the 3-tier app"
  value       = kubernetes_namespace.app.metadata[0].name
}

output "ingress_name" {
  description = "Ingress resource name (ALB is created by controller)"
  value       = kubernetes_ingress_v1.alb.metadata[0].name
}
