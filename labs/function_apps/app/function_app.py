import logging
import os
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import azure.functions as func

from services.cosmos_service import (
    get_active_users,
    mark_report_sent,
    should_skip_user_for_date,
)
from services.email_service import send_daily_stock_report_email
from services.stock_service import get_latest_prices_for_symbols

app = func.FunctionApp()

def load_report_minute_et() -> int:
    try:
        minute = int(os.getenv("REPORT_MINUTE_ET", "5"))
    except ValueError:
        logging.warning("Invalid REPORT_MINUTE_ET value. Falling back to 5.")
        return 5

    if 0 <= minute <= 59:
        return minute

    logging.warning("REPORT_MINUTE_ET must be between 0 and 59. Falling back to 5.")
    return 5


EASTERN_TZ = ZoneInfo("America/New_York")
SCHEDULE = os.getenv("TIMER_SCHEDULE", "0 */5 20-21 * * 1-5")
REPORT_MINUTE_ET = load_report_minute_et()


@app.timer_trigger(
    schedule=SCHEDULE,
    arg_name="timer",
    run_on_startup=True,
    use_monitor=True,
)
def daily_stock_report(timer: func.TimerRequest) -> None:
    """Send a daily stock move report email after US market close on weekdays."""
    now_utc = datetime.now(UTC)
    now_et = now_utc.astimezone(EASTERN_TZ)
    report_date = now_et.date().isoformat()

    if timer.past_due:
        logging.warning("Timer trigger is running behind schedule.")

    if not should_run_for_current_window(now_et):
        logging.info("Outside the report window. Skipping this invocation.")
        return

    logging.info("Daily stock report job started for %s at %s", report_date, now_et.isoformat())

    users = get_active_users()
    if not users:
        logging.info("No active users found.")
        return

    symbols = build_unique_symbol_list(users)
    if not symbols:
        logging.info("No stock symbols found for active users.")
        return

    price_map = get_latest_prices_for_symbols(symbols)
    if not price_map:
        logging.warning("Market data lookup returned no prices.")
        return

    sent_count = 0
    skipped_count = 0

    for user in users:
        if should_skip_user_for_date(user, report_date):
            skipped_count += 1
            continue

        email = (user.get("email") or "").strip()
        if not email:
            logging.warning("Skipping user with missing email. id=%s", user.get("id"))
            skipped_count += 1
            continue

        report_rows = build_user_report_rows(user.get("stocks", []), price_map)
        if not report_rows:
            logging.info("Skipping %s because no valid stock rows were found.", email)
            skipped_count += 1
            continue

        send_daily_stock_report_email(
            to_email=email,
            report_date=report_date,
            report_rows=report_rows,
        )
        mark_report_sent(user["id"], user.get("partitionKey", user["id"]), report_date)
        sent_count += 1

    logging.info(
        "Daily stock report job finished. users=%s sent=%s skipped=%s",
        len(users),
        sent_count,
        skipped_count,
    )


def should_run_for_current_window(now_et: datetime) -> bool:
    """Allow the job to run once during a narrow ET window while surviving DST changes."""
    return (
        now_et.weekday() < 5
        and now_et.hour == 16
        and REPORT_MINUTE_ET <= now_et.minute < REPORT_MINUTE_ET + 5
    )


def build_unique_symbol_list(users: list[dict]) -> list[str]:
    symbols: set[str] = set()

    for user in users:
        for stock in user.get("stocks", []):
            symbol = normalize_stock_item(stock)
            if symbol:
                symbols.add(symbol)

    return sorted(symbols)


def build_user_report_rows(stocks: list[dict], price_map: dict[str, dict]) -> list[dict]:
    rows = []

    for stock in stocks:
        symbol = normalize_stock_item(stock)
        price_data = price_map.get(symbol)

        if not symbol or not price_data:
            continue

        current_price = safe_float(price_data.get("current"))
        prev_close = safe_float(price_data.get("previousClose"))
        if current_price is None or prev_close is None:
            continue

        daily_change = current_price - prev_close
        daily_change_pct = (daily_change / prev_close * 100) if prev_close > 0 else 0.0

        rows.append(
            {
                "symbol": symbol,
                "previousClose": round(prev_close, 2),
                "current": round(current_price, 2),
                "dailyChange": round(daily_change, 2),
                "dailyChangePct": round(daily_change_pct, 2),
            }
        )

    rows.sort(key=lambda row: row["symbol"])
    return rows


def normalize_symbol(value: object) -> str:
    return str(value or "").strip().upper()


def normalize_stock_item(value: object) -> str:
    if isinstance(value, dict):
        return normalize_symbol(value.get("symbol"))
    return normalize_symbol(value)


def safe_float(value: object) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None
