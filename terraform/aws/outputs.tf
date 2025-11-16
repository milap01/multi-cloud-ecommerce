output "ecr_repository_urls" {
  description = "ECR URLs for all microservices"
  value = {
    for svc, repo in aws_ecr_repository.microservices :
    svc => repo.repository_url
  }
}
