output "psyko_bucket" {
  description = "S3 bucket name for psyko site uploads."
  value       = module.psyko.bucket_name
}

output "psyko_distribution_id" {
  description = "CloudFront distribution ID for cache invalidations."
  value       = module.psyko.distribution_id
}

output "psyko_url" {
  description = "Public URL of the deployed site."
  value       = module.psyko.site_url
}
