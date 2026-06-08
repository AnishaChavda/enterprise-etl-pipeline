import os
import json
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_alert(job_name, status, execution_duration, error_details=None, records_processed=0):
    """
    Sends format-rich alerts to Slack via Webhooks.
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Select color and emoji based on status
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

if __name__ == "__main__":
    send_slack_alert("daily_etl_pipeline", "SUCCESS", 45.2, records_processed=125)
