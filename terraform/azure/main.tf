resource "azurerm_resource_group" "rg" {
  name     = "mce-analytics-rg-${var.project_suffix}"
  location = var.location
}

resource "azurerm_virtual_network" "vnet" {
  name                = "mce-vnet-${var.project_suffix}"
  address_space       = ["10.50.0.0/16"]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_subnet" "aks_subnet" {
  name                 = "aks-subnet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.50.1.0/24"]
}