# Identify current user
data "aws_caller_identity" "current" {}

# 1. Create EKS access entry for your IAM user
resource "aws_eks_access_entry" "admin" {
  cluster_name  = module.eks.cluster_name
  principal_arn = data.aws_caller_identity.current.arn
  type          = "STANDARD"
}

# 2. Associate admin policy with the access entry
resource "aws_eks_access_policy_association" "admin_policy" {
<<<<<<< HEAD
  cluster_name  = module.eks.cluster_name
  principal_arn = data.aws_caller_identity.current.arn

  # Recommended new Admin policy for EKS clusters
  policy_arn = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
=======
  cluster_name  = aws_eks_access_entry.admin.cluster_name
  principal_arn = aws_eks_access_entry.admin.principal_arn
  
  # CHANGE THIS LINE:
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
>>>>>>> 604119d35203258af682b42100d5a4008a956b65

  access_scope {
    type = "cluster"
  }
}

