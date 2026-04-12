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
  subscription_id = var.azure_subscription_id
}

resource "azurerm_resource_group" "function_app" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_storage_account" "function_app" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.function_app.name
  location                 = azurerm_resource_group.function_app.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_service_plan" "function_app" {
  name                = var.service_plan_name
  resource_group_name = azurerm_resource_group.function_app.name
  location            = azurerm_resource_group.function_app.location
  os_type             = "Linux"
  sku_name            = "Y1"
}

resource "azurerm_application_insights" "function_app" {
  name                = "${var.function_app_name}-ai"
  location            = azurerm_resource_group.function_app.location
  resource_group_name = azurerm_resource_group.function_app.name
  application_type    = "web"
}

resource "azurerm_cosmosdb_account" "function_app" {
  name                = var.cosmos_account_name
  location            = azurerm_resource_group.function_app.location
  resource_group_name = azurerm_resource_group.function_app.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  consistency_policy {
    consistency_level = "Session"
  }

  geo_location {
    location          = azurerm_resource_group.function_app.location
    failover_priority = 0
  }
}

resource "azurerm_cosmosdb_sql_database" "function_app" {
  name                = var.cosmos_database_name
  resource_group_name = azurerm_resource_group.function_app.name
  account_name        = azurerm_cosmosdb_account.function_app.name
}

resource "azurerm_cosmosdb_sql_container" "users" {
  name                = var.cosmos_container_name
  resource_group_name = azurerm_resource_group.function_app.name
  account_name        = azurerm_cosmosdb_account.function_app.name
  database_name       = azurerm_cosmosdb_sql_database.function_app.name
  partition_key_paths = ["/partitionKey"]
}

resource "azurerm_linux_function_app" "function_app" {
  name                       = var.function_app_name
  resource_group_name        = azurerm_resource_group.function_app.name
  location                   = azurerm_resource_group.function_app.location
  service_plan_id            = azurerm_service_plan.function_app.id
  storage_account_name       = azurerm_storage_account.function_app.name
  storage_account_access_key = azurerm_storage_account.function_app.primary_access_key
  https_only                 = true

  site_config {
    application_stack {
      python_version = "3.10"
    }
  }

  app_settings = {
    AzureWebJobsStorage                   = azurerm_storage_account.function_app.primary_connection_string
    FUNCTIONS_WORKER_RUNTIME              = "python"
    FUNCTIONS_EXTENSION_VERSION           = "~4"
    SCM_DO_BUILD_DURING_DEPLOYMENT        = "true"
    WEBSITE_RUN_FROM_PACKAGE              = "1"
    APPLICATIONINSIGHTS_CONNECTION_STRING = azurerm_application_insights.function_app.connection_string
    COSMOS_ENDPOINT                       = azurerm_cosmosdb_account.function_app.endpoint
    COSMOS_KEY                            = azurerm_cosmosdb_account.function_app.primary_key
    COSMOS_DATABASE_NAME                  = azurerm_cosmosdb_sql_database.function_app.name
    COSMOS_CONTAINER_NAME                 = azurerm_cosmosdb_sql_container.users.name
    SMTP_HOST                             = var.smtp_host
    SMTP_PORT                             = var.smtp_port
    SMTP_USERNAME                         = var.smtp_username
    SMTP_PASSWORD                         = var.smtp_password
    EMAIL_FROM                            = var.email_from
    TIMER_SCHEDULE                        = var.timer_schedule
    REPORT_MINUTE_ET                      = var.report_minute_et
    MARKET_DATA_PROVIDER_ORDER            = var.market_data_provider_order
    MARKET_DATA_TIMEOUT_SECONDS           = var.market_data_timeout_seconds
    TWELVEDATA_API_KEY                    = var.twelvedata_api_key
    TWELVEDATA_QUOTE_URL                  = var.twelvedata_quote_url
    FINNHUB_API_KEY                       = var.finnhub_api_key
    FINNHUB_QUOTE_URL                     = var.finnhub_quote_url
    FMP_API_KEY                           = var.fmp_api_key
    FMP_QUOTE_URL                         = var.fmp_quote_url
    ALPHAVANTAGE_API_KEY                  = var.alphavantage_api_key
    ALPHAVANTAGE_QUOTE_URL                = var.alphavantage_quote_url
  }
}
