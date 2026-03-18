variable "azure_subscription_id" {
  type        = string
  description = "Azure subscription used for the lab deployment."
  sensitive   = true
}

variable "resource_group_name" {
  type        = string
  default     = "daily-portfolio-report-rg"
  description = "Resource group name for the Function App lab."
}

variable "location" {
  type        = string
  default     = "East US"
  description = "Azure region for the deployment."
}

variable "storage_account_name" {
  type        = string
  default     = "dailyportfoliostore01"
  description = "Globally unique storage account name for Azure Functions."
}

variable "service_plan_name" {
  type        = string
  default     = "daily-portfolio-plan"
  description = "Consumption plan for the Function App."
}

variable "function_app_name" {
  type        = string
  default     = "daily-portfolio-func"
  description = "Function App name."
}

variable "cosmos_account_name" {
  type        = string
  default     = "daily-portfolio-cosmos"
  description = "Globally unique Cosmos DB account name."
}

variable "cosmos_database_name" {
  type        = string
  default     = "portfolio-db"
  description = "Cosmos DB database for user portfolios."
}

variable "cosmos_container_name" {
  type        = string
  default     = "users"
  description = "Cosmos DB container storing user documents."
}

variable "smtp_host" {
  type        = string
  default     = "smtp.gmail.com"
  description = "SMTP host used to send the reports."
}

variable "smtp_port" {
  type        = string
  default     = "587"
  description = "SMTP port used to send the reports."
}

variable "smtp_username" {
  type        = string
  description = "SMTP username."
  sensitive   = true
}

variable "smtp_password" {
  type        = string
  description = "SMTP password or app password."
  sensitive   = true
}

variable "email_from" {
  type        = string
  description = "From address for the daily report emails."
}

variable "market_data_url" {
  type        = string
  default     = "https://query1.finance.yahoo.com/v7/finance/quote"
  description = "Quote endpoint used by the function app."
}

variable "timer_schedule" {
  type        = string
  default     = "0 */5 20-21 * * 1-5"
  description = "Timer schedule in UTC. The app narrows this to a 4:05 PM ET window."
}

variable "report_minute_et" {
  type        = string
  default     = "5"
  description = "Minute after 4 PM ET when the report should send."
}
