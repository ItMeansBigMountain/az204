import json
import os
from pathlib import Path

from dotenv import load_dotenv
from azure.cosmos import CosmosClient, PartitionKey, exceptions


def main() -> None:
    load_dotenv(Path(__file__).resolve().parent / ".env")

    endpoint = require_env("COSMOS_ENDPOINT")
    key = require_env("COSMOS_KEY")
    database_name = os.getenv("COSMOS_DATABASE_NAME", "portfolio-db")
    container_name = os.getenv("COSMOS_CONTAINER_NAME", "users")
    data_file = Path(os.getenv("SEED_DATA_FILE", default_seed_file()))

    client = CosmosClient(endpoint, credential=key)
    database = client.create_database_if_not_exists(id=database_name)
    container = database.create_container_if_not_exists(
        id=container_name,
        partition_key=PartitionKey(path="/partitionKey"),
    )

    users = load_users(data_file)

    created = 0
    updated = 0

    for raw_user in users:
        normalized_user = normalize_user(raw_user)
        partition_key = normalized_user["partitionKey"]
        user_id = normalized_user["id"]

        try:
            existing = container.read_item(item=user_id, partition_key=partition_key)
            if "lastReportDate" in existing and "lastReportDate" not in normalized_user:
                normalized_user["lastReportDate"] = existing["lastReportDate"]
            updated += 1
        except exceptions.CosmosResourceNotFoundError:
            created += 1

        container.upsert_item(normalized_user)

    print(
        f"Seed complete for {database_name}/{container_name}. "
        f"created={created}, updated={updated}, total={len(users)}."
    )


def load_users(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def default_seed_file() -> str:
    return str(Path(__file__).resolve().parent.parent / "data" / "test_users.json")


def normalize_user(raw_user: dict) -> dict:
    user_id = str(raw_user.get("id", "")).strip()
    email = str(raw_user.get("email", "")).strip()

    if not user_id:
        raise RuntimeError("Each user must have a non-empty 'id'.")
    if not email:
        raise RuntimeError(f"User '{user_id}' must have a non-empty 'email'.")

    partition_key = str(raw_user.get("partitionKey") or user_id).strip() or user_id
    stocks = normalize_stocks(raw_user.get("stocks", []))
    is_active = bool(raw_user.get("isActive", True))

    normalized = {
        "id": user_id,
        "partitionKey": partition_key,
        "email": email,
        "isActive": is_active,
        "stocks": stocks,
        "schemaVersion": 2,
    }

    last_report_date = raw_user.get("lastReportDate")
    if last_report_date:
        normalized["lastReportDate"] = str(last_report_date)

    return normalized


def normalize_stocks(raw_stocks: object) -> list[dict]:
    if not isinstance(raw_stocks, list):
        return []

    symbols: set[str] = set()

    for stock in raw_stocks:
        if isinstance(stock, dict):
            symbol = normalize_symbol(stock.get("symbol"))
        else:
            symbol = normalize_symbol(stock)

        if symbol:
            symbols.add(symbol)

    return [{"symbol": symbol} for symbol in sorted(symbols)]


def normalize_symbol(value: object) -> str:
    return str(value or "").strip().upper()


def require_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise RuntimeError(
        f"Missing required environment variable '{name}'. "
        "Set it in scripts/.env or in your shell environment."
    )


if __name__ == "__main__":
    main()
