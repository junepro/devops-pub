output "ebs_csi_role_arn" {
  value = module.ebs_csi_irsa.iam_role_arn
}
