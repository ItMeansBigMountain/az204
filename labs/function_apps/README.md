# Daily Portfolio Report Function App

This lab folder contains a minimal Azure Functions app that sends one daily gain/loss email per active user after the US market closes.

## What it does

- Runs on a timer every 5 minutes during the 4 PM ET hour window.
- Checks the current Eastern time and only sends during the configured minute window.
- Reads active users from Cosmos DB.
- Fetches market prices once for all unique symbols.
- Sends one plain-text email per user.
- Marks `lastReportDate` on each user document to avoid duplicate sends.

## User document shape

```json
{
  "id": "user-1",
  "partitionKey": "user-1",
  "email": "person@example.com",
  "isActive": true,
  "lastReportDate": "2026-03-15",
  "stocks": [
    { "symbol": "AAPL", "shares": 10, "avgCost": 180.25 },
    { "symbol": "MSFT", "shares": 4, "avgCost": 420.00 }
  ]
}
```

## Notes

- The stock lookup uses Yahoo Finance's quote endpoint to keep the app simple and avoid another paid dependency.
- The timer is expressed in UTC, then narrowed in code so DST changes do not force a schedule update.
- Fill in `local.settings.json` for local runs or set matching app settings in Azure.
- The GitHub Actions workflow at `.github/workflows/function-app-cicd.yml` deploys the Function App and then runs the seed script at `labs/function_apps/scripts/seed_cosmos_test_data.py`.
- The seed script uses `labs/function_apps/data/test_users.json` and upserts documents, so it is safe to run more than once.

## GitHub secrets

Add these repository secrets before using the workflow:

- `AZURE_FUNCTIONAPP_NAME`
- `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`
- `COSMOS_ENDPOINT`
- `COSMOS_KEY`
- `COSMOS_DATABASE_NAME`
- `COSMOS_CONTAINER_NAME`
