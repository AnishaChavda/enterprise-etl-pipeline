import os
import json
import logging
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Slack Settings
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# Email Settings
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM", "notifier@enterprise-etl.com")
EMAIL_TO = os.getenv("EMAIL_TO", "krushillukhi1911@gmail.com")

def send_slack_alert(job_name, status, execution_duration=0.0, error_details=None, records_processed=0):
    """
    Sends format-rich alerts to Slack via Webhooks.
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    if status.upper() == "SUCCESS":
        color = "#2EB886"  # green
        emoji = "✅"
    elif status.upper() == "FAILED":
        color = "#A30200"  # red
        emoji = "🚨"
    elif status.upper() == "SLA_MISS":
        color = "#DAA520"  # goldenrod
        emoji = "⏰"
    else:
        color = "#707070"  # grey
        emoji = "⚠️"

    payload = {
        "attachments": [
            {
                "fallback": f"{emoji} {job_name} - {status}",
                "color": color,
                "pretext": f"{emoji} *Pipeline Status Alert*",
                "title": f"Job: {job_name}",
                "fields": [
                    {
                        "title": "Status",
                        "value": status.upper(),
                        "short": True
                    },
                    {
                        "title": "Execution Duration",
                        "value": f"{execution_duration:.2f} seconds",
                        "short": True
                    },
                    {
                        "title": "Records Processed",
                        "value": str(records_processed),
                        "short": True
                    },
                    {
                        "title": "Timestamp",
                        "value": timestamp,
                        "short": True
                    }
                ],
                "footer": "Enterprise ETL Monitor",
                "ts": int(datetime.utcnow().timestamp())
            }
        ]
    }

    if error_details:
        payload["attachments"][0]["fields"].append({
            "title": "Error Details",
            "value": f"```{error_details}```",
            "short": False
        })

    if not SLACK_WEBHOOK_URL or SLACK_WEBHOOK_URL.startswith("your_") or SLACK_WEBHOOK_URL == "dummy":
        logging.warning("[SLACK MOCK ALERT] Webhook URL not configured. Payload:")
        logging.warning(json.dumps(payload, indent=4))
        return False

    try:
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            logging.info("Slack alert sent successfully.")
            return True
        else:
            logging.error(f"Failed to send Slack alert. Status code: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        logging.error(f"Exception sending Slack alert: {e}")
        return False

def send_email_alert(subject, body_html, alert_type="INFO"):
    """
    Sends SMTP email alerts for pipeline failures or validation errors.
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    full_subject = f"[{alert_type}] Enterprise ETL - {subject} ({timestamp})"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = full_subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    html_template = f"""
    <html>
      <body style="font-family: sans-serif; color: #333;">
        <div style="background-color: #f8f9fa; padding: 20px; border-bottom: 3px solid #007bff;">
          <h2 style="margin: 0; color: #007bff;">Enterprise ETL Notification</h2>
        </div>
        <div style="padding: 20px;">
          {body_html}
        </div>
        <div style="font-size: 11px; color: #777; padding: 20px; border-top: 1px solid #eee; margin-top: 20px;">
          Generated automatically by Enterprise ETL Pipeline at {timestamp}.
        </div>
      </body>
    </html>
    """
    msg.attach(MIMEText(html_template, "html"))

    if not SMTP_HOST or SMTP_HOST.startswith("your_") or SMTP_HOST == "dummy":
        logging.warning("[EMAIL MOCK ALERT] SMTP server not configured. Mail details:")
        logging.warning(f"Subject: {full_subject}")
        logging.warning(f"From: {EMAIL_FROM} | To: {EMAIL_TO}")
        logging.warning(f"Body:\n{body_html}")
        return False

    try:
        logging.info(f"Connecting to SMTP host {SMTP_HOST}:{SMTP_PORT}...")
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        if SMTP_USER and SMTP_PASSWORD:
            server.login(SMTP_USER, SMTP_PASSWORD)
        
        logging.info(f"Sending alert email to {EMAIL_TO}...")
        server.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string())
        server.quit()
        logging.info("Email alert sent successfully.")
        return True
    except Exception as e:
        logging.error(f"Failed to send email alert: {e}")
        return False
