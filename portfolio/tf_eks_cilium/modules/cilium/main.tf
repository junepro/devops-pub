resource "helm_release" "cilium" {
  name             = "cilium"
  repository       = "https://helm.cilium.io/"
  chart            = "cilium"
  namespace        = "kube-system"
  create_namespace = false

  set {
    name  = "cni.chainingMode"
    value = "aws-cni"
  }

  set {
    name  = "cni.exclusive"
    value = "false"
  }

  set {
    name  = "enableIPv4Masquerade"
    value = "false"
  }

  set {
    name  = "routingMode"
    value = "native"
  }

  set {
    name  = "hubble.relay.enabled"
    value = "true"
  }

  set {
    name  = "hubble.ui.enabled"
    value = "true"
  }
}
