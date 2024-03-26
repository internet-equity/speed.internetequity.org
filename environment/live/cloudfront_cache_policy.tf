data "aws_cloudfront_cache_policy" "cache_default" {
  name = "Managed-CachingOptimized"
}


#
# The above look-up should discover a managed policy along the following lines.
#
# resource "aws_cloudfront_cache_policy" "cache_default" {
#   comment     = "Policy with caching enabled. Supports Gzip and Brotli compression."
#   default_ttl = "86400"
#   max_ttl     = "31536000"
#   min_ttl     = "1"
#   name        = "Managed-CachingOptimized"
# 
#   parameters_in_cache_key_and_forwarded_to_origin {
#     cookies_config {
#       cookie_behavior = "none"
#     }
# 
#     enable_accept_encoding_brotli = "true"
#     enable_accept_encoding_gzip   = "true"
# 
#     headers_config {
#       header_behavior = "none"
#     }
# 
#     query_strings_config {
#       query_string_behavior = "none"
#     }
#   }
# }
