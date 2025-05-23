import pytest
import smtplib
from unittest.mock import patch, MagicMock
from datetime import datetime
from app.services.email_service import send_email, send_invoice_email

@pytest.fixture
def mock_invoice():
    invoice = MagicMock()
    invoice.id = 1
    invoice.invoice_number = "INV-001"
    invoice.issue_date = datetime(2025, 5, 1)
    invoice.due_date = datetime(2025, 5, 15)
    invoice.currency = "USD"
    invoice.total_amount = 100.00
    invoice.line_items = []
    return invoice

@pytest.fixture
def mock_organization():
    organization = MagicMock()
    organization.id = 1
    organization.name = "Test Organization"
    return organization

@pytest.mark.parametrize(
    "smtp_host,smtp_port,expected_success",
    [
        ("smtp.example.com", 587, True),
        ("", 0, False),
    ],
)
def test_send_email(smtp_host, smtp_port, expected_success, monkeypatch):
    # Mock SMTP settings
    monkeypatch.setattr("app.core.config.settings.SMTP_HOST", smtp_host)
    monkeypatch.setattr("app.core.config.settings.SMTP_PORT", smtp_port)
    monkeypatch.setattr("app.core.config.settings.EMAILS_FROM_EMAIL", "test@example.com")
    
    with patch("smtplib.SMTP") as mock_smtp:
        # Configure mock
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        # Call function
        success, error = send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            body_html="<p>Test HTML</p>",
            body_text="Test plain text",
        )
        
        # Assert results
        assert success == expected_success
        
        if expected_success:
            # If success expected, check SMTP was called correctly
            mock_smtp.assert_called_once_with(smtp_host, smtp_port)
            mock_smtp_instance.sendmail.assert_called_once()
        else:
            # If failure expected, check SMTP not called
            mock_smtp.assert_not_called()


def test_email_retry_logic(monkeypatch):
    # Mock SMTP settings
    monkeypatch.setattr("app.core.config.settings.SMTP_HOST", "smtp.example.com")
    monkeypatch.setattr("app.core.config.settings.SMTP_PORT", 587)
    monkeypatch.setattr("app.core.config.settings.EMAILS_FROM_EMAIL", "test@example.com")
    monkeypatch.setattr("app.core.config.settings.SMTP_TLS", True)
    
    # Mock time.sleep to avoid actual delays during tests
    with patch("time.sleep") as mock_sleep, patch("smtplib.SMTP") as mock_smtp:
        # Configure SMTP mock to fail twice, then succeed
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        # Setup sendmail to fail twice with connection errors, then succeed on third attempt
        mock_smtp_instance.sendmail.side_effect = [
            smtplib.SMTPServerDisconnected("Server disconnected unexpectedly"),
            smtplib.SMTPConnectError(421, "Service not available"),
            None  # Success on third attempt
        ]
        
        # Call function with 3 max retries
        success, error = send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            body_html="<p>Test HTML</p>",
            body_text="Test plain text",
            max_retries=3,
            retry_delay=1
        )
        
        # Assert results
        assert success is True
        assert error is None
        
        # Check that SMTP was created 3 times (for 3 attempts)
        assert mock_smtp.call_count == 3
        
        # Check that sendmail was attempted 3 times
        assert mock_smtp_instance.sendmail.call_count == 3
          # Check that sleep was called between retries (2 times)
        assert mock_sleep.call_count == 2
        mock_sleep.assert_called_with(1)  # Check delay value


def test_email_retry_all_attempts_fail(monkeypatch):
    """Test that email sending returns proper error when all retries fail"""
    # Mock SMTP settings
    monkeypatch.setattr("app.core.config.settings.SMTP_HOST", "smtp.example.com")
    monkeypatch.setattr("app.core.config.settings.SMTP_PORT", 587)
    monkeypatch.setattr("app.core.config.settings.EMAILS_FROM_EMAIL", "test@example.com")
    
    # Mock time.sleep to avoid actual delays during tests
    with patch("time.sleep") as mock_sleep, patch("smtplib.SMTP") as mock_smtp:
        # Configure SMTP mock to fail all attempts
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        # Setup sendmail to fail on all attempts
        mock_smtp_instance.sendmail.side_effect = smtplib.SMTPServerDisconnected("Server disconnected unexpectedly")
        
        # Call function with 2 max retries
        success, error = send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            body_html="<p>Test HTML</p>",
            body_text="Test plain text",
            max_retries=2,
            retry_delay=1
        )
        
        # Assert results
        assert success is False
        assert error is not None
        assert "Failed to send email after 2 attempts" in error
        assert "Server disconnected unexpectedly" in error
        
        # Check that SMTP was created 2 times (for 2 attempts)
        assert mock_smtp.call_count == 2
        
        # Check that sendmail was attempted 2 times
        assert mock_smtp_instance.sendmail.call_count == 2
        
        # Check that sleep was called once (between the two attempts)
        assert mock_sleep.call_count == 1

@patch("app.services.email_service.send_email")
@patch("app.services.pdf_service.generate_invoice_pdf")
def test_send_invoice_email(mock_generate_pdf, mock_send_email, mock_invoice, mock_organization):
    # Configure mocks
    mock_send_email.return_value = (True, None)
    
    # Call function
    success, error = send_invoice_email(
        invoice_id=1,
        recipient_email="test@example.com",
        organization=mock_organization,
        invoice=mock_invoice,
        line_items=[],
        payment_link="https://example.com/pay",
        include_pdf=True,
        custom_message="Test message"
    )
    
    # Assert results
    assert success is True
    assert error is None
    
    # Check if PDF was generated
    mock_generate_pdf.assert_called_once()
    
    # Check that send_email was called with correct parameters
    mock_send_email.assert_called_once()
    _, kwargs = mock_send_email.call_args
    assert kwargs["to_email"] == "test@example.com"
    assert "Invoice INV-001" in kwargs["subject"]
    assert isinstance(kwargs["body_html"], str)
    assert isinstance(kwargs["body_text"], str)
    assert isinstance(kwargs["attachments"], list)
    assert len(kwargs["attachments"]) == 1  # PDF attachment
