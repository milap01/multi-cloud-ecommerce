resource "azurerm_eventhub_namespace" "eh_ns" {
  name                = var.eventhub_namespace_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "Standard"
  capacity            = 1
}

resource "azurerm_eventhub" "events" {
  name                = var.eventhub_events_name
  namespace_name      = azurerm_eventhub_namespace.eh_ns.name
  resource_group_name = azurerm_resource_group.rg.name
  partition_count     = 2
  message_retention   = 1
}

resource "azurerm_eventhub" "results" {
  name                = var.eventhub_results_name
  namespace_name      = azurerm_eventhub_namespace.eh_ns.name
  resource_group_name = azurerm_resource_group.rg.name
  partition_count     = 2
  message_retention   = 1
}

# Shared Access Policy for sending to events
resource "azurerm_eventhub_authorization_rule" "events_send" {
  name                = "eventsSendRule"
  eventhub_name       = azurerm_eventhub.events.name
  namespace_name      = azurerm_eventhub_namespace.eh_ns.name
  resource_group_name = azurerm_resource_group.rg.name

  send = true
}

# Shared Access Policy for receiving from results
resource "azurerm_eventhub_authorization_rule" "results_listen" {
  name                = "resultsListenRule"
  eventhub_name       = azurerm_eventhub.results.name
  namespace_name      = azurerm_eventhub_namespace.eh_ns.name
  resource_group_name = azurerm_resource_group.rg.name

  listen = true
}