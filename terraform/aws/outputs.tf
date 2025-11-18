output "rds_endpoint" {
  value = aws_db_instance.postgres.address
}

output "msk_bootstrap_brokers_tls" {
  value = aws_msk_cluster.kafka.bootstrap_brokers_tls
  # FIX: Explicit dependency added to ensure the cluster is ACTIVE before reading output.
  depends_on = [aws_msk_cluster.kafka]
}

output "ecr_repositories" {
  value = { for k, r in aws_ecr_repository.microservices : k => r.repository_url }
}

output "eks_cluster_name" {
  value = module.eks.cluster_id
}

output "eks_cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "opensearch_endpoint" {
  value = aws_opensearch_domain.search.endpoint
}