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
from services.email_service import send_portfolio_report_email
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
    run_on_startup=False,
    use_monitor=True,
)
def daily_portfolio_report(timer: func.TimerRequest) -> None:
    """Send a lightweight gain/loss email after US market close on weekdays."""
    now_utc = datetime.now(UTC)
    now_et = now_utc.astimezone(EASTERN_TZ)
    report_date = now_et.date().isoformat()

    if timer.past_due:
        logging.warning("Timer trigger is running behind schedule.")

    if not should_run_for_current_window(now_et):
        logging.info("Outside the report window. Skipping this invocation.")
        return

    logging.info("Portfolio report job started for %s at %s", report_date, now_et.isoformat())

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
            logging.info("Skipping %s because no valid holdings were found.", email)
            skipped_count += 1
            continue

        totals = calculate_portfolio_totals(report_rows)
        send_portfolio_report_email(
            to_email=email,
            report_date=report_date,
            report_rows=report_rows,
            totals=totals,
        )
        mark_report_sent(user["id"], user.get("partitionKey", user["id"]), report_date)
        sent_count += 1

    logging.info(
        "Portfolio report job finished. users=%s sent=%s skipped=%s",
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
            symbol = normalize_symbol(stock.get("symbol"))
            if symbol:
                symbols.add(symbol)

    return sorted(symbols)


def build_user_report_rows(stocks: list[dict], price_map: dict[str, float]) -> list[dict]:
    rows = []

    for stock in stocks:
        symbol = normalize_symbol(stock.get("symbol"))
        shares = safe_float(stock.get("shares"))
        avg_cost = safe_float(stock.get("avgCost"))
        close_price = price_map.get(symbol)

        if not symbol or shares is None or avg_cost is None or close_price is None:
            continue
        if shares <= 0 or avg_cost < 0 or close_price < 0:
            continue

        cost_basis = shares * avg_cost
        market_value = shares * close_price
        gain_loss = market_value - cost_basis
        gain_loss_pct = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0.0

        rows.append(
            {
                "symbol": symbol,
                "shares": round(shares, 4),
                "avgCost": round(avg_cost, 2),
                "close": round(close_price, 2),
                "costBasis": round(cost_basis, 2),
                "marketValue": round(market_value, 2),
                "gainLoss": round(gain_loss, 2),
                "gainLossPct": round(gain_loss_pct, 2),
            }
        )

    rows.sort(key=lambda row: row["symbol"])
    return rows


def calculate_portfolio_totals(report_rows: list[dict]) -> dict:
    total_cost_basis = round(sum(row["costBasis"] for row in report_rows), 2)
    total_market_value = round(sum(row["marketValue"] for row in report_rows), 2)
    total_gain_loss = round(total_market_value - total_cost_basis, 2)
    total_gain_loss_pct = round(
        (total_gain_loss / total_cost_basis * 100) if total_cost_basis > 0 else 0.0,
        2,
    )

    return {
        "totalCostBasis": total_cost_basis,
        "totalMarketValue": total_market_value,
        "totalGainLoss": total_gain_loss,
        "totalGainLossPct": total_gain_loss_pct,
    }


def normalize_symbol(value: object) -> str:
    return str(value or "").strip().upper()


def safe_float(value: object) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None
