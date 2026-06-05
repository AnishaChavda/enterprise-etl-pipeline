import pytest

from utils.notifications import format_slack_message


def test_format_slack_message_contains_job_and_status():
    message = format_slack_message("daily_etl_pipeline", "SUCCESS", "Loaded 100 records")
    assert "daily_etl_pipeline" in message
    assert "SUCCESS" in message
    assert "Loaded 100 records" in message
