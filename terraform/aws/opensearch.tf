resource "aws_opensearch_domain" "search" {
  domain_name     = "mce-search-${var.project_suffix}"
  engine_version  = "OpenSearch_3.1"

  cluster_config {
    instance_type          = "t3.small.search"
    instance_count         = 2
    zone_awareness_enabled = true
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 10
  }

  vpc_options {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.msk.id]
  }

  domain_endpoint_options {
    enforce_https = true
  }

  advanced_options = {
    "rest.action.multi.allow_explicit_index" = "true"
  }

  tags = { Project = var.project_suffix }

}