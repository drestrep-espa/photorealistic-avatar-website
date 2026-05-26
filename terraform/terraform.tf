terraform {
  required_version = ">= 1.6.0"

  cloud {
    organization = "REPLACE_WITH_YOUR_TFC_ORG"

    workspaces {
      name = "endrokosai-static-sites"
    }
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.70"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}
