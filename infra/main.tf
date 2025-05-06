provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "main" {
  name     = "az204"
  location = "Central US"
}

resource "azurerm_app_service_plan" "linux_plan" {
  name                = "ASP-az204-92eb"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  kind                = "Linux"
  reserved            = true

  sku {
    tier = "Free"
    size = "F1"
  }
}

resource "azurerm_linux_web_app" "trapistan" {
  name                = "trapistan"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_id     = azurerm_app_service_plan.linux_plan.id

  site_config {
    linux_fx_version = "DOTNETCORE|9.0"
  }
}
