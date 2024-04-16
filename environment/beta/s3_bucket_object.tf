# fileset() nearly works but does not provide content-type
module "html" {
  source                  = "hashicorp/dir/template"
  base_dir                = var.html_path != null ? var.html_path : "${path.module}/html"
}

resource "aws_s3_object" "html" {
  # upload everything from the html/ directory – so long as it's not documentation (such as License.md or README.adoc)
  for_each                = {
    for key, value in module.html.files: key => value
    if length(regexall("\\.(?i:(?:adoc)|(?:asciidoc)|(?:md)|(?:markdown))$", key)) == 0
  }

  bucket                  = aws_s3_bucket.site.id

  key                     = "html/${each.key}"

  # exactly one of these two will be set
  content                 = each.value.content
  source                  = each.value.source_path

  content_type            = each.value.content_type
  source_hash             = each.value.digests.md5
}
