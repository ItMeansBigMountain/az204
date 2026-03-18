import os

import requests


YAHOO_QUOTE_URL = "https://query1.finance.yahoo.com/v7/finance/quote"


def get_latest_prices_for_symbols(symbols: list[str]) -> dict[str, dict]:
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

    price_map: dict[str, dict] = {}
    for quote in results:
        symbol = str(quote.get("symbol") or "").upper()
        current_price = quote.get("regularMarketPrice")
        prev_close = quote.get("regularMarketPreviousClose")

        if symbol and isinstance(current_price, (int, float)) and isinstance(prev_close, (int, float)):
            price_map[symbol] = {
                "current": float(current_price),
                "previousClose": float(prev_close),
            }

    return price_map
