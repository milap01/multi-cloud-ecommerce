output "aks_kubeconfig" {
  value = azurerm_kubernetes_cluster.aks.kube_config_raw
  sensitive = true
}

output "event_hub_conn_str_events" {
  value     = azurerm_eventhub_authorization_rule.events_send.primary_connection_string
  sensitive = true
}

output "event_hub_conn_str_results" {
  value     = azurerm_eventhub_authorization_rule.results_listen.primary_connection_string
  sensitive = true
}