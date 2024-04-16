resource "aws_apigatewayv2_api" "api" {
  name          = "speedtest-api_${var.code_name}"
  protocol_type = "HTTP"

  disable_execute_api_endpoint = true

  route_key = "POST /speedtest"

  target = aws_lambda_function.api.arn
}


resource "aws_lambda_permission" "api" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"

  # The /*/* portion grants access from any method on any resource
  # within the API Gateway.
  source_arn = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}


resource "aws_apigatewayv2_domain_name" "api" {
  domain_name              = aws_acm_certificate.api.domain_name

  domain_name_configuration {
    certificate_arn = aws_acm_certificate.api.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }
}

resource "aws_apigatewayv2_api_mapping" "api" {
  api_id      = aws_apigatewayv2_api.api.id
  domain_name = aws_apigatewayv2_domain_name.api.id
  stage       = "$default"
}
