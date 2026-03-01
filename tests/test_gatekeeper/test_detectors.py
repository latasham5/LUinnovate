"""
Tests for Developer 1's detection modules.
"""

import pytest
from services.gatekeeper.detectors.credential_detector import detect_credentials
from services.gatekeeper.detectors.numeric_extractor import extract_numeric_data
from services.gatekeeper.detectors.financial_detector import detect_financial_data
from services.gatekeeper.detectors.customer_info_detector import detect_customer_information
from services.gatekeeper.detectors.regulated_content_detector import detect_regulated_content
from shared.enums import RiskCategory


class TestCredentialDetector:
    """Tests for credential detection."""

    def test_detects_api_key(self):
        prompt = "My api_key = test_fake_key_abc123def456ghi789"
        results = detect_credentials(prompt)
        assert len(results) > 0
        assert results[0].category == RiskCategory.CREDENTIALS

    def test_detects_bearer_token(self):
        prompt = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        results = detect_credentials(prompt)
        assert len(results) > 0

    def test_detects_password(self):
        prompt = "password = MyS3cureP@ssword!"
        results = detect_credentials(prompt)
        assert len(results) > 0

    def test_detects_internal_url(self):
        prompt = "Check the docs at https://internal.coca-cola.com/api/docs"
        results = detect_credentials(prompt)
        assert len(results) > 0

    def test_no_false_positive_on_clean_text(self):
        prompt = "What is the weather like today?"
        results = detect_credentials(prompt)
        assert len(results) == 0


class TestNumericExtractor:
    """Tests for numeric data extraction."""

    def test_detects_dollar_amounts(self):
        prompt = "Revenue was $4,200,000.00 this quarter."
        results = extract_numeric_data(prompt)
        assert any(r.text.startswith("$") for r in results)

    def test_detects_percentages(self):
        prompt = "Growth rate is 18.5% year over year."
        results = extract_numeric_data(prompt)
        assert any("%" in r.text for r in results)


class TestFinancialDetector:
    """Tests for financial data detection."""

    def test_detects_revenue_keyword(self):
        prompt = "Our revenue target for next quarter is very aggressive."
        results = detect_financial_data(prompt)
        assert len(results) > 0
        assert results[0].category == RiskCategory.FINANCIAL

    def test_detects_margin_keyword(self):
        prompt = "The gross margin has been declining steadily."
        results = detect_financial_data(prompt)
        assert len(results) > 0


class TestCustomerInfoDetector:
    """Tests for customer information detection."""

    def test_detects_customer_name_keyword(self):
        prompt = "The customer name on the account is important."
        results = detect_customer_information(prompt)
        assert len(results) > 0
        assert results[0].category == RiskCategory.CUSTOMER_INFO


class TestRegulatedContentDetector:
    """Tests for regulated content detection."""

    def test_detects_hipaa_keyword(self):
        prompt = "The patient records need to be reviewed."
        results = detect_regulated_content(prompt)
        assert len(results) > 0
        assert results[0].category == RiskCategory.REGULATED

    def test_detects_legal_privilege(self):
        prompt = "This is attorney-client privileged communication."
        results = detect_regulated_content(prompt)
        assert len(results) > 0
