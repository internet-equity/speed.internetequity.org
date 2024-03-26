variable "bucket_name" {
  description = "Name to assign to S3 bucket"
  type = string
}

variable "code_name" {
  description = "Name to apply to the infrastructure stack to differentiate resources such as CloudFront Functions which require unique names"
  default = ""
  type = string
}

variable "distribution_description" {
  description = "Comment describing the CloudFront distribution"
  default = "OpenSpeedTest"
  type = string
}

#
# Hosted zone will *not* be created but only adapted as necessary
#

variable "domain_name" {
  description = "Domain name (e.g. site.example.com) to which the CloudFront distribution should respond (and will redirect from www.site.example.com)"
  type = string
}

variable "zone_id" {
  description = "Specify hosted zone id whenever zone cannot be inferred from the domain name"
  default = null
  type = string
}

variable "html_path" {
  description = "Local filesystem path from which static site files should be uploaded (defaults to included html/ directory)"
  default = null
  type = string
}
