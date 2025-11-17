# ArgoCD install helper

1. Ensure kubectl context points to EKS cluster.
2. Install ArgoCD (see commands below).
3. Patch argocd-server service for LoadBalancer.
4. Apply clusterrolebinding if needed.

Commands (see main repo README for full list).
