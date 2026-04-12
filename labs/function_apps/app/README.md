# Daily Portfolio Email Function App

This application is an Azure Function timer job that sends a daily stock price-change report to each active user.

## What the app does

- Runs on a timer trigger during the US market close window.
- Reads active users from Cosmos DB.
- Uses each user's `email` field as the destination email address.
- Reads each user's followed stock symbols from `stocks`.
- Builds a unique symbol list across all users, then fetches prices once.
- Calculates each symbol's daily change using `current - previous close`.
- Sends a simple report per user with a table and small bar indicator for gain/loss.
- Updates `lastReportDate` in Cosmos DB to avoid duplicate sends on the same day.

## APIs and services used

- **Azure Functions (Python)** for scheduling and execution.
- **Azure Cosmos DB SQL API** for user portfolio documents.
- **Stock quote providers** via an ordered fallback chain in `services/stock_service.py`:
  - Twelve Data
  - Finnhub
  - Financial Modeling Prep
  - Alpha Vantage
- **SMTP** for sending outbound emails.

## Local configuration

Use the example files in this folder as the source of truth for required settings:

- `.env.example`
- `local.settings.example.json`

They show every value the app expects for both:

- app-level settings used by the Python code
- Azure Functions host settings required by `func start`

Before running locally:

1. Copy `.env.example` into `.env` and fill in real values.
2. Copy `local.settings.example.json` into `local.settings.json` and fill in the same real values.

Required settings:

- `AzureWebJobsStorage`
- `COSMOS_ENDPOINT`
- `COSMOS_KEY`
- `COSMOS_DATABASE_NAME`
- `COSMOS_CONTAINER_NAME`
- `EMAIL_FROM`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `TIMER_SCHEDULE`
- `REPORT_MINUTE_ET`
- `MARKET_DATA_PROVIDER_ORDER`
- `MARKET_DATA_TIMEOUT_SECONDS`
- `TWELVEDATA_API_KEY`
- `TWELVEDATA_QUOTE_URL`
- `FINNHUB_API_KEY`
- `FINNHUB_QUOTE_URL`
- `FMP_API_KEY`
- `FMP_QUOTE_URL`
- `ALPHAVANTAGE_API_KEY`
- `ALPHAVANTAGE_QUOTE_URL`

Notes:

- `AzureWebJobsStorage` must be a valid Azure Storage connection string for the timer trigger listener.
- `func start` reads `local.settings.json`; it does not automatically load `.env`.
- `.env` is useful as a parallel reference file, but the Functions host still needs `local.settings.json`.
- `MARKET_DATA_PROVIDER_ORDER` controls the fallback order. The app tries each provider and keeps any valid prices it gets back.

## User document shape

```json
{
  "id": "user-1",
  "partitionKey": "user-1",
  "email": "person@example.com",
  "isActive": true,
  "lastReportDate": "2026-03-17",
  "stocks": [
    { "symbol": "AAPL" },
    { "symbol": "MSFT" }
  ]
}
```
