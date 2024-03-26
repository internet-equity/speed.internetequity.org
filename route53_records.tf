data "aws_route53_zone" "site" {
  name = var.zone_id != null && var.zone_id != "" ? null : regex("[^.]+\\.[^.]+$", var.domain_name)
  zone_id = var.zone_id
}

resource "aws_route53_record" "site" {
  zone_id = data.aws_route53_zone.site.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name  = aws_cloudfront_distribution.site.domain_name
    zone_id = aws_cloudfront_distribution.site.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "www" {
  zone_id = data.aws_route53_zone.site.zone_id
  name    = "www.${var.domain_name}"
  type    = "A"

  alias {
    name  = aws_cloudfront_distribution.site.domain_name
    zone_id = aws_cloudfront_distribution.site.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.site.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.site.zone_id
}
