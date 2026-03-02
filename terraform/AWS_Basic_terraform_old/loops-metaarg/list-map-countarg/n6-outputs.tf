output "for_output_list" {
  description = "for loop list"
  value = [for instance in aws_instance.myec2vm: instance.public_dns]
}

output "for_output_map1" {
  description = "for loop map"
  value = {for instance in aws_instance.myec2vm: instance.id => instance.public_dns}
}

output "for_output_map2" {
  description = "for loop map - advanced"
  value = {for c, instance in aws_instance.myec2vm: c => instance.public_dns}
}

output "legacy_splat_instance_publicdns" {
  description = "legacy splat operator"
  value = aws_instance.myec2vm.*.public_dns
}

output "latest_splat_instance_publicdns" {
  description = "latest splat operator"
  value = aws_instance.myec2vm[*].public_dns
}