terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.1.5"
}

#
# alternate provider configuration for resources which *must* be created in us-east-1
#
# (e.g. cloudfront ssl/tls certificates)
#
provider "aws" {
  alias  = "us-east-1"
  region = "us-east-1"
}
