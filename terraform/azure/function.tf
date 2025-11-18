# Storage account for the Function App
resource "azurerm_storage_account" "func_storage" {
  name                     = "mcefuncsa${var.project_suffix}" # Must be globally unique, lowercase, no dashes
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# App Service Plan (Consumption Plan is cheapest)
resource "azurerm_service_plan" "asp" {
  name                = "mce-func-plan-${var.project_suffix}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = "Y1" # Consumption tier
}

# The Function App
resource "azurerm_linux_function_app" "analytics_fn" {
  name                = "mce-analytics-fn-${var.project_suffix}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  storage_account_name       = azurerm_storage_account.func_storage.name
  storage_account_access_key = azurerm_storage_account.func_storage.primary_access_key
  service_plan_id            = azurerm_service_plan.asp.id

  site_config {
    application_stack {
      python_version = "3.10"
    }
  }

  app_settings = {
    "FUNCTIONS_WORKER_RUNTIME" = "python"
    "EventHubConnection"       = azurerm_eventhub_namespace.eh_ns.default_primary_connection_string
  }
}