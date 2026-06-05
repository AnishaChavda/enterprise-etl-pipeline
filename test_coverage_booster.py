import pytest
import os
from unittest.mock import patch, MagicMock
import stripe
from utils.slack_notifier import send_slack_alert
from utils.email_notifier import send_email_alert
from loading.snowflake_upsert import snowflake_upsert
from loading.snowflake_setup import run_snowflake_setup
from loading.connection import get_db_session
from extraction.stripe_extractor import run_stripe_extraction
from extraction.salesforce_connector import run_salesforce_extraction
from extraction.zendesk_extractor import run_zendesk_extraction
from transformation.transformer import parse_datetime

def test_slack_notifier_failure():
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 500
        mock_post.return_value.text = "Internal Server Error"
        with patch.dict(os.environ, {"SLACK_WEBHOOK_URL": "http://mock-slack"}):
            res = send_slack_alert("test", "FAILED", 10.0, "error")
            assert res is False

def test_slack_notifier_exception():
    with patch("requests.post", side_effect=Exception("network error")):
        with patch.dict(os.environ, {"SLACK_WEBHOOK_URL": "http://mock-slack"}):
            res = send_slack_alert("test", "SUCCESS", 5.0)
            assert res is False

def test_email_notifier_failure():
    with patch("smtplib.SMTP") as mock_smtp:
        mock_smtp.side_effect = Exception("SMTP error")
        with patch.dict(os.environ, {"SMTP_HOST": "smtp.mock.com"}):
            res = send_email_alert("test sub", "<p>body</p>")
            assert res is False

def test_snowflake_upsert_exceptions():
    # Test connection exception pathway in snowflake_upsert
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.execute.side_effect = Exception("snowflake query failure")
    
    with pytest.raises(Exception):
        snowflake_upsert(
            conn=mock_conn,
            table_name="CUSTOMERS",
            records=[{"customer_id": "1", "name": "Alice"}],
            pk_column="customer_id",
            dry_run=False
        )

def test_snowflake_setup_exceptions():
    # Test Snowflake setup database failure, overriding import-bound ACCOUNT
    with patch("snowflake.connector.connect") as mock_connect:
        mock_connect.side_effect = Exception("connection failure")
        with patch("loading.snowflake_setup.ACCOUNT", "real_acc"):
            with pytest.raises(Exception):
                run_snowflake_setup(dry_run=False)

def test_stripe_extraction_rate_limiting():
    # Test Stripe extractor rate limit retries, overriding Stripe client checker
    with patch("stripe.Customer.list") as mock_list:
        mock_list.side_effect = [
            stripe.error.RateLimitError("Rate limit"),
            MagicMock(data=[])
        ]
        with patch("extraction.stripe_extractor.get_stripe_client") as mock_client:
            mock_client.return_value = stripe
            with patch("time.sleep") as mock_sleep: # prevent actual sleeping
                from extraction.stripe_extractor import fetch_stripe_resource, generate_mock_customers
                res = fetch_stripe_resource("customers", stripe.Customer.list, generate_mock_customers)
                assert mock_sleep.call_count == 1

def test_stripe_extraction_errors():
    with patch("stripe.Customer.list", side_effect=stripe.error.StripeError("API Error")):
        with patch("extraction.stripe_extractor.get_stripe_client") as mock_client:
            mock_client.return_value = stripe
            with pytest.raises(stripe.error.StripeError):
                from extraction.stripe_extractor import fetch_stripe_resource, generate_mock_customers
                fetch_stripe_resource("customers", stripe.Customer.list, generate_mock_customers)

def test_salesforce_extraction_error():
    # Mocking SOQL execution failure fallback
    mock_sf = MagicMock()
    mock_sf.query_all.side_effect = Exception("SOQL Error")
    from extraction.salesforce_connector import fetch_salesforce_resource, generate_mock_accounts
    res = fetch_salesforce_resource(mock_sf, "SELECT Id FROM Account", generate_mock_accounts)
    # Falls back to mock data
    assert len(res) == 10

def test_zendesk_extraction_rate_limiting():
    # Zendesk rate limits, overriding import-bound SUBDOMAIN, EMAIL, and TOKEN variables
    with patch("requests.get") as mock_get:
        mock_get.side_effect = [
            MagicMock(status_code=429, headers={"Retry-After": "1"}),
            MagicMock(status_code=200, json=lambda: {"tickets": [{"id": 1}], "next_page": None})
        ]
        with patch("extraction.zendesk_extractor.SUBDOMAIN", "real_subdomain"), \
             patch("extraction.zendesk_extractor.EMAIL", "admin@company.com"), \
             patch("extraction.zendesk_extractor.TOKEN", "real_token"):
            with patch("time.sleep") as mock_sleep:
                from extraction.zendesk_extractor import fetch_zendesk_tickets
                res = fetch_zendesk_tickets()
                assert len(res) == 1
                assert mock_sleep.call_count == 1

def test_zendesk_extraction_failures():
    with patch("requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=500, text="internal error")
        from extraction.zendesk_extractor import fetch_zendesk_tickets
        with patch("extraction.zendesk_extractor.SUBDOMAIN", "real_subdomain"), \
             patch("extraction.zendesk_extractor.EMAIL", "admin@company.com"), \
             patch("extraction.zendesk_extractor.TOKEN", "real_token"):
            # Falls back to mock tickets
            res = fetch_zendesk_tickets()
            assert len(res) == 10

def test_datetime_parsing_exceptions():
    with pytest.raises(ValueError):
        parse_datetime("invalid-date-format-xyz")
