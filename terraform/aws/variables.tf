variable "project_suffix" {
  type    = string
  default = "mce-2"
}

variable "region" {
  type    = string
  default = "us-east-1"
}

variable "db_password" {
  type      = string
  sensitive = true
  
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "private_subnet_count" {
  type    = number
  default = 2
}

# Optional: provide ECR lifecycle policy TTL for images (days)
variable "ecr_retention_days" {
  type    = number
  default = 30
}

