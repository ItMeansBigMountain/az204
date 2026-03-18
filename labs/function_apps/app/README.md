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
- **Yahoo Finance quote API** via:
  `https://query1.finance.yahoo.com/v7/finance/quote`
  (used by `services/stock_service.py` to get `regularMarketPrice` and `regularMarketPreviousClose`).
- **SMTP** for sending outbound emails.

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
