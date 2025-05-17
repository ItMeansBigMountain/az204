terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
  required_version = ">= 1.2.0"
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

resource "azurerm_resource_group" "main" {
  name     = "az204"
  location = "Central US"
}

resource "azurerm_service_plan" "linux_plan" {
  name                = "trapistan-linux-plan"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  sku_name            = "F1"
}

resource "azurerm_linux_web_app" "blazor_webapp" {
  name                = "trapistan-Blazor"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.linux_plan.id

  site_config {
    application_stack {
      dotnet_version = "9.0"
    }
    always_on = false
  }

  app_settings = {
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
  }

  identity {
    type = "SystemAssigned"
  }

  depends_on = [azurerm_service_plan.linux_plan]
}

resource "azurerm_linux_web_app" "frequencyHZ_webapp" {
  name                = "trapistan-FrequencyHZ"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.linux_plan.id

  site_config {
    application_stack {
      docker_image_name = "trapistanacr.azurecr.io/trapistanwebapp:latest"
      # docker_registry_url = "trapistanacr.azurecr.io"
    }
    always_on       = false
  }

  app_settings = {
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
    "BUILD_VERSION" = timestamp()
  }

  identity {
    type = "SystemAssigned"
  }
} 
