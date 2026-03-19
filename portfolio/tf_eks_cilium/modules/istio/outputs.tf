output "istio_version" {
  value = var.istio_version
}

output "ingress_namespace" {
  value = helm_release.istio_ingressgateway.namespace
}

output "ingress_release_name" {
  value = helm_release.istio_ingressgateway.name
}
