import os

import requests


YAHOO_QUOTE_URL = "https://query1.finance.yahoo.com/v7/finance/quote"


def get_latest_prices_for_symbols(symbols: list[str]) -> dict[str, float]:
    if not symbols:
        return {}

    response = requests.get(
        os.getenv("MARKET_DATA_URL", YAHOO_QUOTE_URL),
        params={"symbols": ",".join(symbols)},
        timeout=20,
    )
    response.raise_for_status()

    payload = response.json()
    results = payload.get("quoteResponse", {}).get("result", [])

    price_map: dict[str, float] = {}
    for quote in results:
        symbol = str(quote.get("symbol") or "").upper()
        close_price = quote.get("regularMarketPreviousClose")

        if symbol and isinstance(close_price, (int, float)):
            price_map[symbol] = float(close_price)

    return price_map
