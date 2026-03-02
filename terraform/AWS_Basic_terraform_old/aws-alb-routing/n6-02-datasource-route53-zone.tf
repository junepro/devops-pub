data "aws_route53_zone" "mydomain" {
  name = "example.com"
}

output "mydoamin_zoneid" {
  value = data.aws_route53_zone.mydomain.zone_id
}

output "mydomain_name" {
  value = data.aws_route53_zone.mydomain.name
}