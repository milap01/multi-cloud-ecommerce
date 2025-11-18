variable "project_suffix" {
  type        = string
  description = "Suffix to ensure unique resource names"
  default     = "mce"
}

variable "location" {
  type        = string
  description = "Azure Region"
  default     = "East US"
}