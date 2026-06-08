import logging
import os
import smtplib
import ssl
from email.message import EmailMessage

import requests

from configs.config import (
    ALERT_EMAIL_FROM,
    ALERT_EMAIL_TO,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USERNAME,
    SLACK_WEBHOOK_URL,
)

LOGGER = logging.getLogger("utils.notifications")
logging.basicConfig(level=logging.INFO)


def send_slack_notification(message: str) -> None:
    if not SLACK_WEBHOOK_URL:
        LOGGER.warning("Slack webhook not configured. Skipping Slack notification.")
        return

    payload = {"text": message}
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        LOGGER.info("Slack notification sent")
    except Exception as exc:
        LOGGER.error("Slack notification failed: %s", exc)


def send_email(subject: str, body: str, recipients: list[str] | None = None) -> None:
    recipients = recipients or [ALERT_EMAIL_TO]
    if not SMTP_HOST or not SMTP_USERNAME or not SMTP_PASSWORD:
        LOGGER.warning("SMTP configuration missing. Skipping email alert.")
        return

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = ALERT_EMAIL_FROM
    message["To"] = ", ".join(recipients)
    message.set_content(body)

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            server.starttls(context=context)
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)
        LOGGER.info("Email alert sent to %s", recipients)
    except Exception as exc:
        LOGGER.error("Email alert failed: %s", exc)


def format_slack_message(job_name: str, status: str, details: str) -> str:
    return f"*{job_name}* status: *{status}*\n{details}"


def airflow_failure_alert(context: dict):
    task = context.get("task_instance")
    dag_id = task.dag_id if task else "unknown"
    message = format_slack_message(
        job_name=f"Airflow DAG {dag_id}",
        status="FAILED",
        details=str(context.get("exception", "Unknown error")),
    )
    send_slack_notification(message)
    send_email(
        subject=f"Airflow Failure: {dag_id}",
        body=message,
    )
