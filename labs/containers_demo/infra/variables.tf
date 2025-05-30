variable "subscription_id" {
  description = "Azure Subscription ID"
  type        = string
}

variable "service_plan_id" {
  description = "Azure App Service Plan ID"
  type        = string
}

variable "applicationinsights_connection_string" {
  description = "Application Insights Connection String"
  type        = string
}

variable "applicationinsights_instrumentation_key" {
  description = "Application Insights Instrumentation Key"
  type        = string
}

# variable "client_id" {
#   description = "Azure Client ID (Service Principal)"
#   type        = string
# }

# variable "client_secret" {
#   description = "Azure Client Secret"
#   type        = string
#   sensitive   = true
# }

# variable "tenant_id" {
#   description = "Azure Tenant ID"
#   type        = string
# }
