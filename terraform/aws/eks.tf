module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"  # Use stable v20.x instead of v21.0.0

  # Cluster basic configuration
  cluster_name    = "mce-eks-${var.project_suffix}"
  cluster_version = "1.30"  # Use a released version (1.30 is stable)

  # VPC + Subnets
  vpc_id                   = aws_vpc.main.id
  subnet_ids               = aws_subnet.private[*].id
  control_plane_subnet_ids = aws_subnet.private[*].id

  # Cluster endpoint access
  cluster_endpoint_private_access = true
  cluster_endpoint_public_access  = true

  # Enable IRSA
  enable_irsa = true

  # Cluster addons
  cluster_addons = {
    vpc-cni = {
      most_recent = true
      configuration_values = jsonencode({
        env = {
          ENABLE_PREFIX_DELEGATION = "true"
        }
      })
    }
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
  }

  # Managed node groups
  eks_managed_node_groups = {
    mce_nodes = {
      desired_size = 2
      min_size     = 1
      max_size     = 4

      instance_types = ["t3.medium"]
      
      # Let the module create the IAM role automatically
      # Remove iam_role_arn unless you have specific requirements
    }
  }

  tags = {
    Project = var.project_suffix
  }
}