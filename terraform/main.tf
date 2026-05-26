data "aws_route53_zone" "root" {
  name         = var.root_domain
  private_zone = false
}

module "psyko" {
  source = "./modules/static-site"

  subdomain        = "psyko"
  root_domain      = var.root_domain
  route53_zone_id  = data.aws_route53_zone.root.zone_id

  providers = {
    aws           = aws
    aws.us_east_1 = aws.us_east_1
  }
}
