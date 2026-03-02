output "role_arn" {
  description = "IAM role ARN for the controller service account"
  value       = aws_iam_role.lbc.arn
}

output "service_account_name" {
  description = "Service account name"
  value       = var.service_account_name
}

output "namespace" {
  description = "Namespace"
  value       = var.namespace
}
