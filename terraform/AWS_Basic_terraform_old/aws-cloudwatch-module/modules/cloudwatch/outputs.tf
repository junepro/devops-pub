output "cis_log_group_name" {
  description = "CIS CloudWatch log group name"
  value       = aws_cloudwatch_log_group.cis_log_group.name
}

output "synthetics_canary_id" {
  description = "Synthetics canary ID"
  value       = aws_synthetics_canary.sswebsite2.id
}
