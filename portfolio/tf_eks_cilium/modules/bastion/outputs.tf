output "instance_id" {
  value = aws_instance.this.id
}

output "public_ip" {
  value = aws_instance.this.public_ip
}

output "private_ip" {
  value = aws_instance.this.private_ip
}

output "security_group_id" {
  value = aws_security_group.this.id
}

output "key_name" {
  value = local.effective_key_name
}

output "iam_role_arn" {
  value = aws_iam_role.this.arn
}
output "iam_role_name" {
  value = aws_iam_role.this.name
}