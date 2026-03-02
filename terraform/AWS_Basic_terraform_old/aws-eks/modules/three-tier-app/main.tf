# 3-Tier App: Web (frontend), App (backend API), Data (internal/cache tier)
# Exposed via single ALB with path-based routing

resource "kubernetes_namespace" "app" {
  metadata {
    name = var.namespace
  }
}

# --- Web Tier (Frontend) ---
resource "kubernetes_deployment" "web" {
  metadata {
    name      = "web-tier"
    namespace = kubernetes_namespace.app.metadata[0].name
    labels = {
      app = "web-tier"
    }
  }
  spec {
    replicas = 2
    selector {
      match_labels = { app = "web-tier" }
    }
    template {
      metadata {
        labels = { app = "web-tier" }
      }
      spec {
        container {
          name  = "web"
          image = "nginx:alpine"
          port {
            container_port = 80
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "web" {
  metadata {
    name      = "web-tier"
    namespace = kubernetes_namespace.app.metadata[0].name
  }
  spec {
    selector = { app = "web-tier" }
    port {
      port        = 80
      target_port = 80
    }
    type = "ClusterIP"
  }
}

# --- App Tier (Backend API) ---
resource "kubernetes_deployment" "app" {
  metadata {
    name      = "app-tier"
    namespace = kubernetes_namespace.app.metadata[0].name
    labels = {
      app = "app-tier"
    }
  }
  spec {
    replicas = 2
    selector {
      match_labels = { app = "app-tier" }
    }
    template {
      metadata {
        labels = { app = "app-tier" }
      }
      spec {
        container {
          name  = "app"
          image = "hashicorp/http-echo:latest"
          args  = ["-text=App Tier API", "-listen=:8080"]
          port {
            container_port = 8080
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "app" {
  metadata {
    name      = "app-tier"
    namespace = kubernetes_namespace.app.metadata[0].name
  }
  spec {
    selector = { app = "app-tier" }
    port {
      port        = 80
      target_port = 8080
    }
    type = "ClusterIP"
  }
}

# --- Data Tier (internal service, e.g. cache/worker) ---
resource "kubernetes_deployment" "data" {
  metadata {
    name      = "data-tier"
    namespace = kubernetes_namespace.app.metadata[0].name
    labels = {
      app = "data-tier"
    }
  }
  spec {
    replicas = 1
    selector {
      match_labels = { app = "data-tier" }
    }
    template {
      metadata {
        labels = { app = "data-tier" }
      }
      spec {
        container {
          name  = "data"
          image = "hashicorp/http-echo:latest"
          args  = ["-text=Data Tier", "-listen=:9090"]
          port {
            container_port = 9090
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "data" {
  metadata {
    name      = "data-tier"
    namespace = kubernetes_namespace.app.metadata[0].name
  }
  spec {
    selector = { app = "data-tier" }
    port {
      port        = 80
      target_port = 9090
    }
    type = "ClusterIP"
  }
}

# --- Ingress: Single ALB with path-based routing ---
resource "kubernetes_ingress_v1" "alb" {
  metadata {
    name      = "three-tier-alb"
    namespace = kubernetes_namespace.app.metadata[0].name
    annotations = {
      "kubernetes.io/ingress.class"                            = "alb"
      "alb.ingress.kubernetes.io/scheme"                       = "internet-facing"
      "alb.ingress.kubernetes.io/target-type"                  = "ip"
      "alb.ingress.kubernetes.io/healthcheck-path"             = "/"
      "alb.ingress.kubernetes.io/healthcheck-interval-seconds" = "15"
      "alb.ingress.kubernetes.io/healthcheck-timeout-seconds"  = "5"
      "alb.ingress.kubernetes.io/healthy-threshold-count"      = "2"
      "alb.ingress.kubernetes.io/unhealthy-threshold-count"    = "2"
    }
  }
  spec {
    ingress_class_name = var.ingress_class
    rule {
      http {
        path {
          path      = "/"
          path_type = "Prefix"
          backend {
            service {
              name = kubernetes_service.web.metadata[0].name
              port {
                number = 80
              }
            }
          }
        }
        path {
          path      = "/api"
          path_type = "Prefix"
          backend {
            service {
              name = kubernetes_service.app.metadata[0].name
              port {
                number = 80
              }
            }
          }
        }
        path {
          path      = "/data"
          path_type = "Prefix"
          backend {
            service {
              name = kubernetes_service.data.metadata[0].name
              port {
                number = 80
              }
            }
          }
        }
      }
    }
  }
}
