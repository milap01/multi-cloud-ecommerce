module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "21.0.0"

  # FIX: Renamed cluster_name to name
  name            = "mce-eks-${var.project_suffix}"
  # FIX: Renamed cluster_version to kubernetes_version
  kubernetes_version = "1.33"

  vpc_id     = aws_vpc.main.id
  subnet_ids = aws_subnet.private[*].id

  eks_managed_node_groups = {
    mce_nodes = {
      min_size       = 1
      desired_size   = 2
      max_size       = 4
      instance_types = ["t3.medium"]
      iam_role_arn   = aws_iam_role.eks_node.arn
    }
  }

  tags = {
    Project = var.project_suffix
  }
}