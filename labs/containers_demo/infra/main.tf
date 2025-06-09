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

# resource "azurerm_container_registry" "trapistan_acr" {
#   name                = "trapistanacr"
#   resource_group_name = "az204"
#   location            = "Central US"
#   sku                 = "Basic"
#   admin_enabled       = true
# }

# resource "azurerm_service_plan" "trapistan_frequencyHZ_linux_plan" {
#   name                = "trapistan-frequencyhz-linux-plan"
#   resource_group_name = "az204"
#   location            = "Central US"
#   os_type             = "Linux"
#   sku_name            = "F1"
# }



# resource "azurerm_linux_web_app" "frequencyHZ_webapp" {
#   name                = "trapistan-frequencyhz"
#   location            = "Central US"
#   resource_group_name = "az204"
#   service_plan_id = azurerm_service_plan.trapistan_frequencyHZ_linux_plan.id

#   site_config {
#     application_stack {
#       docker_image_name        = "trapistanwebapp:latest"
#       docker_registry_url      = "https://trapistanacr.azurecr.io"
#       docker_registry_username = azurerm_container_registry.trapistan_acr.admin_username
#       docker_registry_password = azurerm_container_registry.trapistan_acr.admin_password
#     }
#     always_on                               = false
#   }

#   identity {
#     type = "SystemAssigned"
#   }

#   auth_settings {
#     enabled = false
#   }

#   app_settings = {
#     "WEBSITES_ENABLE_APP_SERVICE_STORAGE"        = "false"
#     "BUILD_VERSION"                              = timestamp()
#     "ApplicationInsightsAgent_EXTENSION_VERSION" = "~3"
#     "WEBSITE_HTTPS_ONLY"                         = "true"
#     "WEBSITE_TIME_ZONE"                          = "Central Standard Time"
#     "WEBSITES_PORT"                              = "8181"
#   }
# }












##############################################################################
# AZURE CONTAIN INSTANCE GROUP example 
##############################################################################

# resource "azurerm_container_group" "trapistan_aci" {
#   name                = "trapistan-aci"
#   location            = "Central US"
#   resource_group_name = "az204"
#   os_type             = "Linux"
#   restart_policy      = "OnFailure"

#   ip_address_type = "Public"
#   dns_name_label  = "trapistan-aci"

#   image_registry_credential {
#     server   = azurerm_container_registry.trapistan_acr.login_server
#     username = azurerm_container_registry.trapistan_acr.admin_username
#     password = azurerm_container_registry.trapistan_acr.admin_password
#   }


#   container {
#     name   = "trapistan-aci"
#     image  = "trapistanacr.azurecr.io/trapistanwebapp:latest"
#     cpu    = 1
#     memory = 1.5

#     ports {
#       port     = 80
#       protocol = "TCP"
#     }
#   }

#   tags = {}
# }

##############################################################################