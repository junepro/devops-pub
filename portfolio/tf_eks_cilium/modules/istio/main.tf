resource "helm_release" "istio_base" {
  name             = "istio-base"
  repository       = "https://istio-release.storage.googleapis.com/charts"
  chart            = "base"
  version          = var.istio_version
  namespace        = "istio-system"
  create_namespace = true
}

resource "helm_release" "istiod" {
  name             = "istiod"
  repository       = "https://istio-release.storage.googleapis.com/charts"
  chart            = "istiod"
  version          = var.istio_version
  namespace        = "istio-system"
  create_namespace = true

  depends_on = [helm_release.istio_base]
}

resource "helm_release" "istio_ingressgateway" {
  name             = "istio-ingressgateway"
  repository       = "https://istio-release.storage.googleapis.com/charts"
  chart            = "gateway"
  version          = var.istio_version
  namespace        = "istio-ingress"
  create_namespace = true

  values = [yamlencode({
    service = {
      type        = var.ingress_service_type
      annotations = var.ingress_annotations
    }
  })]

  depends_on = [helm_release.istiod]
}
