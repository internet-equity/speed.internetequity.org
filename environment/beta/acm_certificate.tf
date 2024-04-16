resource "aws_acm_certificate" "site" {
  # certificate applied to cloudfront MUST be in region us-east-1
  provider                  = aws.us-east-1

  domain_name               = var.domain_name
  subject_alternative_names = ["*.${var.domain_name}"]

  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_acm_certificate" "api" {
  # certificate applied to api must be in same region as api
  domain_name               = "api.${var.domain_name}"

  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}
