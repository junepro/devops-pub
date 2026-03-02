output "instance_publicip" {
  value = toset([for instance in aws_instance.myec2vm: instance.public_ip])
}

output "instance_publicdns" {
  value = toset([for instance in aws_instance.myec2vm: instance.public_dns])
}

output "instance_publicdns2" {
  value = tomap({for az, instance in aws_instance.myec2vm: az => instance.public_dns})
}