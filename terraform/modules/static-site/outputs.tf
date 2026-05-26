output "bucket_name" {
  description = "S3 bucket where the site assets live."
  value       = aws_s3_bucket.site.id
}

output "distribution_id" {
  description = "CloudFront distribution ID (use for cache invalidation)."
  value       = aws_cloudfront_distribution.site.id
}

output "distribution_domain_name" {
  description = "CloudFront default domain (xxxx.cloudfront.net)."
  value       = aws_cloudfront_distribution.site.domain_name
}

output "site_url" {
  description = "Public HTTPS URL of the site."
  value       = "https://${local.fqdn}"
}
