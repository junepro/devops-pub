output "launch_template_id" {
  description = "Launch Template ID"
  value       = aws_launch_template.my_launch_template.id
}

output "launch_template_latest_version" {
  description = "Launch Template Latest Version"
  value       = aws_launch_template.my_launch_template.latest_version
}

output "autoscaling_group_id" {
  description = "Autoscaling Group ID"
  value       = aws_autoscaling_group.my_asg.id
}

output "autoscaling_group_name" {
  description = "Autoscaling Group Name"
  value       = aws_autoscaling_group.my_asg.name
}

output "autoscaling_group_arn" {
  description = "Autoscaling Group ARN"
  value       = aws_autoscaling_group.my_asg.arn
}

output "sns_topic_arn" {
  description = "SNS topic ARN for ASG notifications"
  value       = aws_sns_topic.myasg_sns_topic.arn
}

output "high_cpu_policy_arn" {
  description = "ARN of high CPU scaling policy"
  value       = aws_autoscaling_policy.high_cpu.arn
}
