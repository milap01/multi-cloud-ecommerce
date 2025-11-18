data "aws_caller_identity" "current" {}

# 1. Define the access entry (without policy association)
resource "aws_eks_access_entry" "admin" {
  cluster_name  = module.eks.cluster_name
  principal_arn = data.aws_caller_identity.current.arn
  type          = "STANDARD"
}

# 2. Use a separate resource to associate the policy
resource "aws_eks_access_policy_association" "admin_policy" {
  cluster_name  = aws_eks_access_entry.admin.cluster_name
  principal_arn = aws_eks_access_entry.admin.principal_arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSAdminPolicy"

  access_scope {
    type = "cluster"
    # Removed 'namespaces = []' as it is optional and unnecessary for cluster-scope access
  }
}