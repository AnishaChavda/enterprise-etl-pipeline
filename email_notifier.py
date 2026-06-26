import os
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM", "notifier@enterprise-etl.com")
EMAIL_TO = os.getenv("EMAIL_TO", "admin@enterprise-etl.com")

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

    # Construct HTML body wrapping the provided content
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

if __name__ == "__main__":
    send_email_alert(
        "Critical Pipeline Failure",
        "<p>The ETL pipeline failed during staging load phase.</p><p>Error: DB connection timed out.</p>",
        "CRITICAL"
    )
