import os
from functools import lru_cache

from azure.cosmos import CosmosClient, exceptions


@lru_cache(maxsize=1)
def _get_container():
    endpoint = os.environ["COSMOS_ENDPOINT"]
    key = os.environ["COSMOS_KEY"]
    database_name = os.getenv("COSMOS_DATABASE_NAME", "portfolio-db")
    container_name = os.getenv("COSMOS_CONTAINER_NAME", "users")

    client = CosmosClient(endpoint, credential=key)
    database = client.get_database_client(database_name)
    return database.get_container_client(container_name)


def get_active_users() -> list[dict]:
    container = _get_container()
    query = """
    SELECT c.id, c.email, c.isActive, c.lastReportDate, c.partitionKey, c.stocks
    FROM c
    WHERE c.isActive = true
    """
    return list(container.query_items(query=query, enable_cross_partition_query=True))


def should_skip_user_for_date(user: dict, report_date: str) -> bool:
    if not user.get("isActive", True):
        return True
    return user.get("lastReportDate") == report_date


def mark_report_sent(user_id: str, partition_key: str, report_date: str) -> None:
    container = _get_container()

    try:
        container.patch_item(
            item=user_id,
            partition_key=partition_key,
            patch_operations=[{"op": "add", "path": "/lastReportDate", "value": report_date}],
        )
    except exceptions.CosmosHttpResponseError:
        user = container.read_item(item=user_id, partition_key=partition_key)
        user["lastReportDate"] = report_date
        container.replace_item(item=user_id, body=user)
