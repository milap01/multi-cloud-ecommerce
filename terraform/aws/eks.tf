module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "19.15.3"

  cluster_name    = "mce-eks-${var.project_suffix}"
  cluster_version = "1.27"

  vpc_id      = aws_vpc.main.id
  subnet_ids  = aws_subnet.private[*].id

  eks_managed_node_groups = {
    mce_nodes = {
      min_size       = 1
      desired_size   = 2
      max_size       = 5
      instance_types = ["t3.medium"]
    }
  }
}

