output "apps_dns_fqdn" {
  description = "FQDN of the Route53 record"
  value       = aws_route53_record.apps_dns.fqdn
}
