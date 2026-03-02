output "public_ip" {
  value = aws_eip.bastion.public_ip
}

output "instance_id" {
  value = aws_instance.bastion.id
}

output "security_group_id" {
  value = aws_security_group.bastion.id
}

output "iam_role_arn" {
  value = aws_iam_role.bastion.arn
}

output "role_arn" {
  value = aws_iam_role.bastion.arn
}