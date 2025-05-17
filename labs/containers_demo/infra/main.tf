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

resource "azurerm_container_registry" "trapistan_acr" {
  name                = "trapistanacr"
  resource_group_name = "az204"
  location            = "Central US"
  sku                 = "Basic"
  admin_enabled       = true
}

resource "azurerm_container_group" "trapistan_aci" {
  name                = "trapistan-aci"
  location            = "Central US"
  resource_group_name = "az204"
  os_type             = "Linux"
  restart_policy      = "OnFailure"

  ip_address_type = "Public"
  dns_name_label  = "trapistan-aci"

  image_registry_credential {
    server   = azurerm_container_registry.trapistan_acr.login_server
    username = azurerm_container_registry.trapistan_acr.admin_username
    password = azurerm_container_registry.trapistan_acr.admin_password
  }


  container {
    name   = "trapistan-aci"
    image  = "trapistanacr.azurecr.io/trapistanwebapp:v1"
    cpu    = 1
    memory = 1.5

    ports {
      port     = 80
      protocol = "TCP"
    }
  }

  tags = {}
}
