variable "subdomain" {
  description = "Subdomain label (e.g. 'psyko' for psyko.endrokosai.com)."
  type        = string
}

variable "root_domain" {
  description = "Apex domain (e.g. endrokosai.com)."
  type        = string
}

variable "route53_zone_id" {
  description = "Route 53 hosted zone ID for the apex domain."
  type        = string
}

variable "price_class" {
  description = "CloudFront price class."
  type        = string
  default     = "PriceClass_100"
}

variable "tags" {
  description = "Tags applied to all resources."
  type        = map(string)
  default     = {}
}
