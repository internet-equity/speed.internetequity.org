resource "aws_cloudfront_function" "post_request_ok" {
  name    = var.code_name != "" ? "post-request-ok_${var.code_name}" : "post-request-ok"
  runtime = "cloudfront-js-2.0"
  comment = "viewer-request event handler to give POST requests an immediate response of 204 No Content (rather than the service default of 403 Forbidden)"
  publish = true
  code    = file("${path.module}/cloudfront_function/src/post-request-ok.js")
}

resource "aws_cloudfront_function" "redirect_remove_www" {
  name    = var.code_name != "" ? "redirect-remove-www_${var.code_name}" : "redirect-remove-www"
  runtime = "cloudfront-js-2.0"
  comment = "viewer-request event handler to redirect requests for a www.DO.MAIN host to DO.MAIN"
  publish = true
  code    = file("${path.module}/cloudfront_function/src/redirect-remove-www.js")
}
