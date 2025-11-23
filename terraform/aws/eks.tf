module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0" # Stick to v20.x as v21 may not be released/stable yet

  # Cluster Basic Config (Top-level arguments)
  cluster_name    = "mce-eks-${var.project_suffix}"
  cluster_version = "1.30"

  # Network Config
  vpc_id                   = aws_vpc.main.id
  subnet_ids               = aws_subnet.private[*].id
  control_plane_subnet_ids = aws_subnet.private[*].id

  # Endpoint Access (Top-level arguments)
  cluster_endpoint_public_access  = true
  cluster_endpoint_private_access = true

  # IRSA
  enable_irsa = true

  # Add-ons (Correct argument name is 'cluster_addons')
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

  # Managed Node Groups
  eks_managed_node_groups = {
    mce_nodes = {
      desired_size = 2
      min_size     = 1
      max_size     = 4

      instance_types = ["t3.medium"]
    }
  }

  tags = {
    Project = var.project_suffix
  }
}