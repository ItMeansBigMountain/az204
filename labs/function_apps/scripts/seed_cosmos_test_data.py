import json
import os
from pathlib import Path

from dotenv import load_dotenv
from azure.cosmos import CosmosClient, PartitionKey


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

    for user in users:
        user.setdefault("partitionKey", user["id"])
        user.setdefault("isActive", True)
        container.upsert_item(user)

    print(f"Seeded {len(users)} user documents into {database_name}/{container_name}.")


def load_users(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def default_seed_file() -> str:
    return str(Path(__file__).resolve().parent.parent / "data" / "test_users.json")


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
