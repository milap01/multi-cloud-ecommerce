resource "azurerm_eventhub_namespace" "eh_ns" {
  name                = "mce-events-ns-${var.project_suffix}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "Basic"
  capacity            = 1
}

resource "azurerm_eventhub" "analytics_topic" {
  name                = "analytics-topic"
  namespace_name      = azurerm_eventhub_namespace.eh_ns.name
  resource_group_name = azurerm_resource_group.rg.name
  partition_count     = 1
  message_retention   = 1
}