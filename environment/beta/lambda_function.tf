data "archive_file" "api_package" {
  type = "zip"
  source_dir = "${path.root}/../../api"
  output_path = "${path.root}/.terraform/tmp/api/api.zip"
}


resource "aws_lambda_function" "api" {
  description = "Endpoint to persist completed speedtest results"
  function_name = var.app_short != "" ? "speedtest-api_${var.app_short}" : "speedtest-api"
  handler = "speedtest.main"
  runtime = "python3.10"

  memory_size = 128
  timeout = 30

  filename = data.archive_file.api_package.output_path
  source_code_hash = data.archive_file.api_package.output_base64sha256

  publish = true

  role = aws_iam_role.lambda_executor.arn

  environment {
    variables = {
      ALLOWED_HOSTS = aws_acm_certificate.api.domain_name
      ALLOWED_ORIGIN = "https://${var.domain_name}"
      STORE_PATH = "s3://${aws_s3_bucket.api.id}/speedtest/"
    }
  }

  logging_config {
    log_format = "Text"
  }

  lifecycle {
    ignore_changes = [
      filename,
    ]
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_logs,
    aws_iam_role_policy_attachment.data,
  ]
}


resource "aws_iam_role" "lambda_executor" {
  name = "speedtest-api_${var.code_name}"
  assume_role_policy = data.aws_iam_policy_document.lambda_executor.json
}


data "aws_iam_policy_document" "lambda_executor" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = [
      "sts:AssumeRole",
    ]
  }
}

# logging

data "aws_iam_policy_document" "lambda_logging" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = ["arn:aws:logs:*:*:*"]
  }
}

resource "aws_iam_policy" "lambda_logging" {
  name        = "lambda_logging_${var.code_name}"
  path        = "/"
  description = "IAM policy for logging from a lambda"
  policy      = data.aws_iam_policy_document.lambda_logging.json
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_executor.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

# S3

data "aws_iam_policy_document" "data" {
  statement {
    effect = "Allow"

    actions = [
      "s3:PutObject",
    ]

    resources = ["${aws_s3_bucket.api.arn}/*"]
  }
}

resource "aws_iam_policy" "data" {
  name        = "lambda_s3_${var.code_name}"
  path        = "/"
  description = "IAM policy for a lambda to write data to s3://${aws_s3_bucket.api.id}"
  policy      = data.aws_iam_policy_document.data.json
}

resource "aws_iam_role_policy_attachment" "data" {
  role       = aws_iam_role.lambda_executor.name
  policy_arn = aws_iam_policy.data.arn
}
