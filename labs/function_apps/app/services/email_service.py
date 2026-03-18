import os
import smtplib
from email.message import EmailMessage


def send_portfolio_report_email(
    to_email: str,
    report_date: str,
    report_rows: list[dict],
    totals: dict,
) -> None:
    message = EmailMessage()
    message["Subject"] = f"Daily portfolio report for {report_date}"
    message["From"] = os.environ["EMAIL_FROM"]
    message["To"] = to_email
    message.set_content(build_plain_text_body(report_date, report_rows, totals))

    smtp_host = os.environ["SMTP_HOST"]
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.environ["SMTP_USERNAME"]
    smtp_password = os.environ["SMTP_PASSWORD"]

    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as client:
        client.starttls()
        client.login(smtp_username, smtp_password)
        client.send_message(message)


def build_plain_text_body(report_date: str, report_rows: list[dict], totals: dict) -> str:
    lines = [
        f"Portfolio report for {report_date}",
        "",
        "Symbol | Shares | Avg Cost | Close | Gain/Loss | Gain/Loss %",
        "------ | ------ | -------- | ----- | --------- | ------------",
    ]

    for row in report_rows:
        lines.append(
            f"{row['symbol']} | "
            f"{row['shares']:.4f} | "
            f"${row['avgCost']:.2f} | "
            f"${row['close']:.2f} | "
            f"${row['gainLoss']:.2f} | "
            f"{row['gainLossPct']:.2f}%"
        )

    lines.extend(
        [
            "",
            f"Total cost basis: ${totals['totalCostBasis']:.2f}",
            f"Total market value: ${totals['totalMarketValue']:.2f}",
            f"Total gain/loss: ${totals['totalGainLoss']:.2f}",
            f"Total gain/loss %: {totals['totalGainLossPct']:.2f}%",
        ]
    )

    return "\n".join(lines)
