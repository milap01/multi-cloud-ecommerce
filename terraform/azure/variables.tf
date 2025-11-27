variable "resource_group_name" {
  default = "mce-azure-rg"
}

variable "location" {
  default = "East US"
}

variable "aks_name" {
  default = "mce-aks-cluster"
}

variable "eventhub_namespace_name" {
  default = "mce-streams"
}

variable "eventhub_events_name" {
  default = "events"
}

variable "eventhub_results_name" {
  default = "results"
}

variable "k8s_node_count" {
  default = 1
}

variable "k8s_node_size" {
  default = "Standard_B4ms"
}