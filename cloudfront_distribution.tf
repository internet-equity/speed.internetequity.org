resource "aws_cloudfront_distribution" "site" {
  aliases = [var.domain_name, "www.${var.domain_name}"]

  comment = var.distribution_description

  #
  # For now, by default, we *do not* attempt to compress objects, out of respect for entities under speed test.
  #
  # (And, this is largely to mirror the OpenSpeedTest default nginx configuration.)
  #
  # HOWEVER:
  #
  #   * the entities under speed test shouldn't be compressible anyway
  #   * with this setup, we end up customizing nearly every endpoint, either to let them be
  #     compressed (static assets) or to give them other special handling (upload)
  #
  # As such, this should perhaps be reversed....
  #

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cache_policy_id        = data.aws_cloudfront_cache_policy.cache_default.id
    cached_methods         = ["GET", "HEAD"]
    compress               = "false"
    default_ttl            = "0"
    max_ttl                = "0"
    min_ttl                = "0"
    smooth_streaming       = "false"

    # target_origin_id should be of the form: "NAME.s3.REGION.amazonaws.com"
    target_origin_id       = aws_s3_bucket.site.bucket_regional_domain_name

    viewer_protocol_policy = "redirect-to-https"
  }

  default_root_object = "index.html"
  enabled             = "true"

  # HTTPv2 CANNOT be used
  http_version        = "http1.1"

  is_ipv6_enabled     = "true"

  #
  # Rule 0: /index.html
  #

  ordered_cache_behavior {
    allowed_methods = ["GET", "HEAD"]
    cache_policy_id = data.aws_cloudfront_cache_policy.cache_default.id
    cached_methods  = ["GET", "HEAD"]
    compress        = "true"
    default_ttl     = "0"

    function_association {
      event_type   = "viewer-request"
      function_arn = aws_cloudfront_function.redirect_remove_www.arn
    }

    max_ttl                = "0"
    min_ttl                = "0"
    path_pattern           = "/index.html"
    smooth_streaming       = "false"

    # target_origin_id should be of the form: "NAME.s3.REGION.amazonaws.com"
    target_origin_id       = aws_s3_bucket.site.bucket_regional_domain_name

    viewer_protocol_policy = "redirect-to-https"
  }

  #
  # Rule 1: assets/*
  #

  ordered_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cache_policy_id        = data.aws_cloudfront_cache_policy.cache_default.id
    cached_methods         = ["GET", "HEAD"]
    compress               = "true"
    default_ttl            = "0"
    max_ttl                = "0"
    min_ttl                = "0"
    path_pattern           = "/assets/*"
    smooth_streaming       = "false"

    # target_origin_id should be of the form: "NAME.s3.REGION.amazonaws.com"
    target_origin_id       = aws_s3_bucket.site.bucket_regional_domain_name

    viewer_protocol_policy = "redirect-to-https"
  }

  #
  # Rule 2: /upload
  #

  ordered_cache_behavior {
    allowed_methods = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cache_policy_id = data.aws_cloudfront_cache_policy.cache_default.id
    cached_methods  = ["GET", "HEAD"]
    compress        = "false"
    default_ttl     = "0"

    function_association {
      event_type   = "viewer-request"
      function_arn = aws_cloudfront_function.post_request_ok.arn
    }

    max_ttl                = "0"
    min_ttl                = "0"
    path_pattern           = "/upload"
    smooth_streaming       = "false"

    # target_origin_id should be of the form: "NAME.s3.REGION.amazonaws.com"
    target_origin_id       = aws_s3_bucket.site.bucket_regional_domain_name

    viewer_protocol_policy = "redirect-to-https"
  }

  origin {
    connection_attempts = "3"
    connection_timeout  = "10"

    # domain_name & origin_id should be of the form: "NAME.s3.REGION.amazonaws.com"
    domain_name         = aws_s3_bucket.site.bucket_regional_domain_name
    origin_id           = aws_s3_bucket.site.bucket_regional_domain_name

    origin_path         = "/html"

    origin_shield {
      enabled              = "true"
      origin_shield_region = aws_s3_bucket.site.region
    }
  }

  price_class = "PriceClass_100"

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  retain_on_delete = "false"
  staging          = "false"

  viewer_certificate {
    acm_certificate_arn            = aws_acm_certificate.site.arn
    cloudfront_default_certificate = "false"
    minimum_protocol_version       = "TLSv1.2_2021"
    ssl_support_method             = "sni-only"
  }
}
