variable "aws_region" {
  description = "AWS region for the S3 bucket (CloudFront/ACM always use us-east-1)."
  type        = string
  default     = "eu-west-1"
}

variable "root_domain" {
  description = "Apex domain that owns the Route 53 hosted zone."
  type        = string
  default     = "endrokosai.com"
}
