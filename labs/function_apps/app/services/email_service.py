import os
import smtplib
from email.message import EmailMessage


def send_daily_stock_report_email(
    to_email: str,
    report_date: str,
    report_rows: list[dict],
) -> None:
    message = EmailMessage()
    message["Subject"] = f"Daily stock move report for {report_date}"
    message["From"] = os.environ["EMAIL_FROM"]
    message["To"] = to_email

    text_body = build_plain_text_body(report_date, report_rows)
    html_body = build_html_body(report_date, report_rows)
    message.set_content(text_body)
    message.add_alternative(html_body, subtype="html")

    smtp_host = os.environ["SMTP_HOST"]
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.environ["SMTP_USERNAME"]
    smtp_password = os.environ["SMTP_PASSWORD"]

    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as client:
        client.starttls()
        client.login(smtp_username, smtp_password)
        client.send_message(message)


def build_plain_text_body(report_date: str, report_rows: list[dict]) -> str:
    lines = [
        f"Daily stock move report for {report_date}",
        "",
        "Symbol | Prev Close | Current | Change | Change %",
        "------ | ---------- | ------- | ------ | --------",
    ]

    for row in report_rows:
        lines.append(
            f"{row['symbol']} | "
            f"${row['previousClose']:.2f} | "
            f"${row['current']:.2f} | "
            f"{format_signed_currency(row['dailyChange'])} | "
            f"{format_signed_percent(row['dailyChangePct'])}"
        )

    return "\n".join(lines)


def build_html_body(report_date: str, report_rows: list[dict]) -> str:
    row_html = []
    for row in report_rows:
        change = row["dailyChange"]
        change_pct = row["dailyChangePct"]
        color = "#0a7f2e" if change >= 0 else "#b42318"
        bar_width = min(int(abs(change_pct) * 8), 160)

        row_html.append(
            "<tr>"
            f"<td style='padding:8px;border-bottom:1px solid #e5e7eb;'>{row['symbol']}</td>"
            f"<td style='padding:8px;border-bottom:1px solid #e5e7eb;'>${row['previousClose']:.2f}</td>"
            f"<td style='padding:8px;border-bottom:1px solid #e5e7eb;'>${row['current']:.2f}</td>"
            f"<td style='padding:8px;border-bottom:1px solid #e5e7eb;color:{color};'>{format_signed_currency(change)}</td>"
            f"<td style='padding:8px;border-bottom:1px solid #e5e7eb;color:{color};'>{format_signed_percent(change_pct)}</td>"
            "<td style='padding:8px;border-bottom:1px solid #e5e7eb;'>"
            f"<div style='height:10px;width:{bar_width}px;background:{color};border-radius:3px;'></div>"
            "</td>"
            "</tr>"
        )

    return (
        "<html><body style='font-family:Segoe UI,Arial,sans-serif;'>"
        f"<h3>Daily stock move report for {report_date}</h3>"
        "<table style='border-collapse:collapse;min-width:680px;'>"
        "<thead><tr>"
        "<th style='text-align:left;padding:8px;border-bottom:2px solid #d0d5dd;'>Symbol</th>"
        "<th style='text-align:left;padding:8px;border-bottom:2px solid #d0d5dd;'>Prev Close</th>"
        "<th style='text-align:left;padding:8px;border-bottom:2px solid #d0d5dd;'>Current</th>"
        "<th style='text-align:left;padding:8px;border-bottom:2px solid #d0d5dd;'>Change</th>"
        "<th style='text-align:left;padding:8px;border-bottom:2px solid #d0d5dd;'>Change %</th>"
        "<th style='text-align:left;padding:8px;border-bottom:2px solid #d0d5dd;'>Bar</th>"
        "</tr></thead>"
        f"<tbody>{''.join(row_html)}</tbody>"
        "</table>"
        "</body></html>"
    )


def format_signed_currency(value: float) -> str:
    sign = "+" if value >= 0 else "-"
    return f"{sign}${abs(value):.2f}"


def format_signed_percent(value: float) -> str:
    sign = "+" if value >= 0 else "-"
    return f"{sign}{abs(value):.2f}%"
