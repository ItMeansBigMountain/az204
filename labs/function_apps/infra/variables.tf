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

variable "market_data_provider_order" {
  type        = string
  default     = "twelvedata,finnhub,fmp,alphavantage"
  description = "Ordered list of stock quote providers to try."
}

variable "market_data_timeout_seconds" {
  type        = string
  default     = "20"
  description = "HTTP timeout used for market data providers."
}

variable "twelvedata_api_key" {
  type        = string
  default     = ""
  description = "Twelve Data API key."
  sensitive   = true
}

variable "twelvedata_quote_url" {
  type        = string
  default     = "https://api.twelvedata.com/quote"
  description = "Twelve Data quote endpoint."
}

variable "finnhub_api_key" {
  type        = string
  default     = ""
  description = "Finnhub API key."
  sensitive   = true
}

variable "finnhub_quote_url" {
  type        = string
  default     = "https://finnhub.io/api/v1/quote"
  description = "Finnhub quote endpoint."
}

variable "fmp_api_key" {
  type        = string
  default     = ""
  description = "Financial Modeling Prep API key."
  sensitive   = true
}

variable "fmp_quote_url" {
  type        = string
  default     = "https://financialmodelingprep.com/stable/quote"
  description = "Financial Modeling Prep quote endpoint."
}

variable "alphavantage_api_key" {
  type        = string
  default     = ""
  description = "Alpha Vantage API key."
  sensitive   = true
}

variable "alphavantage_quote_url" {
  type        = string
  default     = "https://www.alphavantage.co/query"
  description = "Alpha Vantage quote endpoint."
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
