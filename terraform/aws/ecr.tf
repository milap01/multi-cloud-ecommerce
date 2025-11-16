locals {
  services = [
    "frontend",
    "product",
    "cart",
    "order",
    "search",
    "events-producer"
  ]
}

resource "aws_ecr_repository" "microservices" {
  for_each = toset(local.services)

  name = "${each.key}-repo-${var.project_suffix}"

  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Service = each.key
    Project = var.project_suffix
  }
}
