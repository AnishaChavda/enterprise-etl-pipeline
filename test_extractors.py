import pytest
from unittest.mock import patch, MagicMock
from extraction.stripe_extractor import fetch_stripe_resource, generate_mock_customers
from extraction.salesforce_connector import fetch_salesforce_resource, generate_mock_accounts
from extraction.zendesk_extractor import fetch_zendesk_tickets

def test_stripe_mock_extraction():
    data = fetch_stripe_resource("customers", MagicMock(), generate_mock_customers)
    assert len(data) == 10
    assert data[0]["id"] == "cus_mock_1"
    assert "email" in data[0]

def test_salesforce_mock_extraction():
    # Pass None as client to trigger mock generation
    data = fetch_salesforce_resource(None, "SELECT Id FROM Account", generate_mock_accounts)
    assert len(data) == 10
    assert data[0]["Id"] == "sf_acc_mock_1"

def test_zendesk_mock_extraction():
    # Credentials are dummy, should fallback to mock ticket generation
    data = fetch_zendesk_tickets()
    assert len(data) == 10
    assert data[0]["id"] == "zd_ticket_mock_1"
