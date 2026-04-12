import logging
import os

import requests


DEFAULT_PROVIDER_ORDER = "twelvedata,finnhub,fmp,alphavantage"
DEFAULT_TIMEOUT_SECONDS = 20
MAX_LOGGED_RESPONSE_CHARS = 300


def get_latest_prices_for_symbols(symbols: list[str]) -> dict[str, dict]:
    if not symbols:
        return {}

    normalized_symbols = sorted({str(symbol or "").strip().upper() for symbol in symbols if str(symbol or "").strip()})
    if not normalized_symbols:
        return {}

    provider_order = load_provider_order()
    price_map: dict[str, dict] = {}
    remaining_symbols = normalized_symbols[:]

    with requests.Session() as session:
        for provider_name in provider_order:
            if not remaining_symbols:
                break

            fetcher = PROVIDERS.get(provider_name)
            if fetcher is None:
                logging.warning("Unknown market data provider '%s'. Skipping.", provider_name)
                continue

            try:
                provider_prices = fetcher(session, remaining_symbols)
            except requests.RequestException as exc:
                logging.warning("Market data provider '%s' failed: %s", provider_name, exc)
                continue
            except ValueError as exc:
                logging.warning("Market data provider '%s' returned invalid data: %s", provider_name, exc)
                continue

            if not provider_prices:
                logging.warning(
                    "Market data provider '%s' returned no usable prices for symbols: %s",
                    provider_name,
                    ", ".join(remaining_symbols),
                )
                continue

            price_map.update(provider_prices)
            missing_symbols = [symbol for symbol in remaining_symbols if symbol not in provider_prices]
            remaining_symbols = [symbol for symbol in remaining_symbols if symbol not in provider_prices]

            logging.info(
                "Market data provider '%s' resolved %s/%s symbols. missing=%s",
                provider_name,
                len(provider_prices),
                len(remaining_symbols) + len(provider_prices),
                ",".join(missing_symbols) if missing_symbols else "none",
            )

    if remaining_symbols:
        logging.warning("No market data was found for symbols: %s", ", ".join(remaining_symbols))

    return price_map


def load_provider_order() -> list[str]:
    raw_value = os.getenv("MARKET_DATA_PROVIDER_ORDER", DEFAULT_PROVIDER_ORDER)
    providers = [item.strip().lower() for item in raw_value.split(",") if item.strip()]
    return providers or DEFAULT_PROVIDER_ORDER.split(",")


def get_timeout_seconds() -> int:
    try:
        value = int(os.getenv("MARKET_DATA_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)))
    except ValueError:
        return DEFAULT_TIMEOUT_SECONDS
    return value if value > 0 else DEFAULT_TIMEOUT_SECONDS


def build_price(current: object, previous_close: object) -> dict | None:
    current_price = safe_float(current)
    prev_close = safe_float(previous_close)
    if current_price is None or prev_close is None:
        return None
    return {
        "current": current_price,
        "previousClose": prev_close,
    }


def safe_float(value: object) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def log_provider_skip(provider_name: str, env_var_name: str) -> None:
    logging.info(
        "Market data provider '%s' skipped because '%s' is not configured.",
        provider_name,
        env_var_name,
    )


def summarize_payload(payload: object) -> str:
    text = str(payload).replace("\n", " ").strip()
    if len(text) <= MAX_LOGGED_RESPONSE_CHARS:
        return text
    return f"{text[:MAX_LOGGED_RESPONSE_CHARS]}..."


def raise_for_status_with_context(response: requests.Response, provider_name: str, symbol: str | None = None) -> None:
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        symbol_text = f" symbol='{symbol}'" if symbol else ""
        body_preview = summarize_payload(response.text)
        logging.warning(
            "Market data provider '%s' HTTP %s.%s body=%s",
            provider_name,
            response.status_code,
            symbol_text,
            body_preview,
        )
        raise exc


def log_provider_payload_issue(provider_name: str, symbol: str, payload: object, reason: str) -> None:
    logging.warning(
        "Market data provider '%s' returned unusable data for symbol '%s': %s payload=%s",
        provider_name,
        symbol,
        reason,
        summarize_payload(payload),
    )


def fetch_from_twelvedata(session: requests.Session, symbols: list[str]) -> dict[str, dict]:
    api_key = os.getenv("TWELVEDATA_API_KEY", "").strip()
    if not api_key:
        log_provider_skip("twelvedata", "TWELVEDATA_API_KEY")
        return {}

    base_url = os.getenv("TWELVEDATA_QUOTE_URL", "https://api.twelvedata.com/quote")
    timeout = get_timeout_seconds()
    price_map: dict[str, dict] = {}

    for symbol in symbols:
        response = session.get(
            base_url,
            params={"symbol": symbol, "apikey": api_key},
            timeout=timeout,
        )
        raise_for_status_with_context(response, "twelvedata", symbol)
        payload = response.json()

        if payload.get("code"):
            log_provider_payload_issue(
                "twelvedata",
                symbol,
                payload,
                f"provider error code={payload.get('code')}",
            )
            continue

        price = build_price(payload.get("close"), payload.get("previous_close"))
        if price:
            price_map[symbol] = price
        else:
            log_provider_payload_issue(
                "twelvedata",
                symbol,
                payload,
                "missing or non-numeric close/previous_close",
            )

    return price_map


def fetch_from_finnhub(session: requests.Session, symbols: list[str]) -> dict[str, dict]:
    api_key = os.getenv("FINNHUB_API_KEY", "").strip()
    if not api_key:
        log_provider_skip("finnhub", "FINNHUB_API_KEY")
        return {}

    base_url = os.getenv("FINNHUB_QUOTE_URL", "https://finnhub.io/api/v1/quote")
    timeout = get_timeout_seconds()
    price_map: dict[str, dict] = {}

    for symbol in symbols:
        response = session.get(
            base_url,
            params={"symbol": symbol, "token": api_key},
            timeout=timeout,
        )
        raise_for_status_with_context(response, "finnhub", symbol)
        payload = response.json()

        price = build_price(payload.get("c"), payload.get("pc"))
        if price:
            price_map[symbol] = price
        else:
            log_provider_payload_issue(
                "finnhub",
                symbol,
                payload,
                "missing or non-numeric c/pc values",
            )

    return price_map


def fetch_from_fmp(session: requests.Session, symbols: list[str]) -> dict[str, dict]:
    api_key = os.getenv("FMP_API_KEY", "").strip()
    if not api_key:
        log_provider_skip("fmp", "FMP_API_KEY")
        return {}

    base_url = os.getenv("FMP_QUOTE_URL", "https://financialmodelingprep.com/stable/quote")
    timeout = get_timeout_seconds()
    response = session.get(
        base_url,
        params={"symbol": ",".join(symbols), "apikey": api_key},
        timeout=timeout,
    )
    raise_for_status_with_context(response, "fmp")

    payload = response.json()
    if not isinstance(payload, list):
        raise ValueError("Expected a list response from FMP.")

    price_map: dict[str, dict] = {}
    for item in payload:
        symbol = str(item.get("symbol") or "").strip().upper()
        if not symbol:
            logging.warning("Market data provider 'fmp' returned an item without a symbol. payload=%s", summarize_payload(item))
            continue

        price = build_price(item.get("price"), item.get("previousClose"))
        if price:
            price_map[symbol] = price
        else:
            log_provider_payload_issue(
                "fmp",
                symbol,
                item,
                "missing or non-numeric price/previousClose",
            )

    return price_map


def fetch_from_alphavantage(session: requests.Session, symbols: list[str]) -> dict[str, dict]:
    api_key = os.getenv("ALPHAVANTAGE_API_KEY", "").strip()
    if not api_key:
        log_provider_skip("alphavantage", "ALPHAVANTAGE_API_KEY")
        return {}

    base_url = os.getenv("ALPHAVANTAGE_QUOTE_URL", "https://www.alphavantage.co/query")
    timeout = get_timeout_seconds()
    price_map: dict[str, dict] = {}

    for symbol in symbols:
        response = session.get(
            base_url,
            params={
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": api_key,
            },
            timeout=timeout,
        )
        raise_for_status_with_context(response, "alphavantage", symbol)
        payload = response.json()
        quote = payload.get("Global Quote", {})

        price = build_price(quote.get("05. price"), quote.get("08. previous close"))
        if price:
            price_map[symbol] = price
        else:
            reason = "missing or non-numeric 05. price/08. previous close"
            if payload.get("Note") or payload.get("Information") or payload.get("Error Message"):
                reason = "provider notice or error returned"
            log_provider_payload_issue("alphavantage", symbol, payload, reason)

    return price_map


PROVIDERS = {
    "twelvedata": fetch_from_twelvedata,
    "finnhub": fetch_from_finnhub,
    "fmp": fetch_from_fmp,
    "alphavantage": fetch_from_alphavantage,
}
