output "function_app_name" {
  value = azurerm_linux_function_app.function_app.name
}

output "function_app_hostname" {
  value = azurerm_linux_function_app.function_app.default_hostname
}

output "cosmos_endpoint" {
  value = azurerm_cosmosdb_account.function_app.endpoint
}

output "cosmos_key" {
  value     = azurerm_cosmosdb_account.function_app.primary_key
  sensitive = true
}

output "cosmos_database_name" {
  value = azurerm_cosmosdb_sql_database.function_app.name
}

output "cosmos_container_name" {
  value = azurerm_cosmosdb_sql_container.users.name
}
