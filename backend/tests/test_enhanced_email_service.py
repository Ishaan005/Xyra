import unittest
from unittest.mock import patch, MagicMock, call
import pytest
import smtplib
from datetime import datetime
from app.services.email_service import (
    send_email,
    _send_email_sync,
    send_invoice_email,
    send_bulk_emails,
    verify_email_address,
    verify_bulk_email_addresses,
    track_email_open,
    track_email_click,
    get_email_status,
    EmailStatus,
    EmailDeliveryStatus
)


class TestEmailService(unittest.TestCase):
    """Tests for the enhanced email service"""
    
    @patch('app.services.email_service.smtplib.SMTP')
    @patch('app.services.email_service.settings')
    def test_send_email_success(self, mock_settings, mock_smtp):
        """Test successful email sending"""
        # Configure mock settings
        mock_settings.SMTP_HOST = 'smtp.example.com'
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USER = 'user'
        mock_settings.SMTP_PASSWORD = 'password'
        mock_settings.SMTP_TLS = True
        mock_settings.EMAILS_FROM_EMAIL = 'from@example.com'
        mock_settings.EMAILS_FROM_NAME = 'Test Sender'
        
        # Setup mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Call the function
        success, error_msg, email_id = send_email(
            to_email='recipient@example.com',
            subject='Test Subject',
            body_html='<p>Test HTML</p>',
            body_text='Test Text',
            cc=['cc@example.com'],
            bcc=['bcc@example.com'],
            reply_to='reply@example.com'
        )
        
        # Check results
        self.assertTrue(success)
        self.assertIsNone(error_msg)
        self.assertIsNotNone(email_id)
        
        # Check SMTP interactions
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('user', 'password')
        mock_server.sendmail.assert_called_once()
        self.assertEqual(mock_server.sendmail.call_args[0][0], 'from@example.com')
        self.assertEqual(sorted(mock_server.sendmail.call_args[0][1]), 
                         sorted(['recipient@example.com', 'cc@example.com', 'bcc@example.com']))
    
    @patch('app.services.email_service.smtplib.SMTP')
    @patch('app.services.email_service.settings')
    def test_send_email_retry_logic(self, mock_settings, mock_smtp):
        """Test email retry logic on failure"""
        # Configure mock settings
        mock_settings.SMTP_HOST = 'smtp.example.com'
        mock_settings.SMTP_PORT = 587
        mock_settings.EMAILS_FROM_EMAIL = 'from@example.com'
        mock_settings.EMAILS_FROM_NAME = 'Test Sender'
        
        # Setup mock SMTP server to fail twice then succeed
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_server.sendmail.side_effect = [
            smtplib.SMTPException("First failure"),
            smtplib.SMTPException("Second failure"),
            None  # Success on third try
        ]
        
        # Call the function with 3 retries
        success, error_msg, email_id = send_email(
            to_email='recipient@example.com',
            subject='Test Subject',
            body_html='<p>Test HTML</p>',
            body_text='Test Text',
            max_retries=3,
            retry_delay=0  # No delay for test speed
        )
        
        # Check results
        self.assertTrue(success)
        self.assertIsNone(error_msg)
        self.assertIsNotNone(email_id)
        
        # Check SMTP interaction count (should be 3 attempts)
        self.assertEqual(mock_server.sendmail.call_count, 3)
    
    @patch('app.services.email_service.smtplib.SMTP')
    @patch('app.services.email_service.settings')
    def test_send_email_all_retries_fail(self, mock_settings, mock_smtp):
        """Test email when all retries fail"""
        # Configure mock settings
        mock_settings.SMTP_HOST = 'smtp.example.com'
        mock_settings.SMTP_PORT = 587
        mock_settings.EMAILS_FROM_EMAIL = 'from@example.com'
        mock_settings.EMAILS_FROM_NAME = 'Test Sender'
        
        # Setup mock SMTP server to fail all attempts
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_server.sendmail.side_effect = smtplib.SMTPException("Persistent failure")
        
        # Call the function with 2 retries
        success, error_msg, email_id = send_email(
            to_email='recipient@example.com',
            subject='Test Subject',
            body_html='<p>Test HTML</p>',
            body_text='Test Text',
            max_retries=2,
            retry_delay=0  # No delay for test speed
        )
        
        # Check results
        self.assertFalse(success)
        self.assertIn("Failed to send email after 2 attempts", error_msg)
        self.assertIsNotNone(email_id)
        
        # Check SMTP interaction count (should be 2 attempts)
        self.assertEqual(mock_server.sendmail.call_count, 2)
    
    @patch('app.services.email_service.settings')
    def test_send_email_missing_config(self, mock_settings):
        """Test sending email with missing SMTP configuration"""
        # Configure mock settings with missing SMTP host
        mock_settings.SMTP_HOST = None
        mock_settings.SMTP_PORT = 587
        
        # Call the function
        success, error_msg, email_id = send_email(
            to_email='recipient@example.com',
            subject='Test Subject',
            body_html='<p>Test HTML</p>',
            body_text='Test Text'
        )
        
        # Check results
        self.assertFalse(success)
        self.assertIn("Email service not configured", error_msg)
        self.assertIsNone(email_id)
    
    def test_email_delivery_status(self):
        """Test EmailDeliveryStatus class"""
        # Create a status object
        status = EmailDeliveryStatus(
            email_id="test-id",
            recipient="test@example.com",
            subject="Test Subject"
        )
        
        # Initial state should be QUEUED
        self.assertEqual(status.status, EmailStatus.QUEUED)
        self.assertEqual(status.delivery_attempts, 0)
        self.assertIsNone(status.last_error)
        
        # Update to SENDING
        status.update_status(EmailStatus.SENDING)
        self.assertEqual(status.status, EmailStatus.SENDING)
        self.assertEqual(status.delivery_attempts, 1)
        
        # Update to FAILED with error
        status.update_status(EmailStatus.FAILED, "Test error")
        self.assertEqual(status.status, EmailStatus.FAILED)
        self.assertEqual(status.delivery_attempts, 1)
        self.assertEqual(status.last_error, "Test error")
        
        # Update to DELIVERED
        status.update_status(EmailStatus.DELIVERED)
        self.assertEqual(status.status, EmailStatus.DELIVERED)
        self.assertIsNotNone(status.sent_at)
    
    @patch('app.services.email_service.send_email')
    def test_send_bulk_emails(self, mock_send_email):
        """Test bulk email sending"""
        # Setup mock return values for send_email
        mock_send_email.side_effect = [
            (True, None, "email-id-1"),
            (False, "Failed to deliver", "email-id-2"),
            (True, None, "email-id-3")
        ]
        
        # Call the function
        results = send_bulk_emails(
            recipients=['test1@example.com', 'test2@example.com', 'test3@example.com'],
            subject='Test Subject',
            body_html_template='<p>Hello {name}</p>',
            body_text_template='Hello {name}',
            template_vars={
                'test1@example.com': {'name': 'User 1'},
                'test3@example.com': {'name': 'User 3'}
            },
            batch_size=10,
            verify_emails=False  # Skip verification for test
        )
        
        # Check results
        self.assertEqual(len(results), 3)
        self.assertTrue(results['test1@example.com']['success'])
        self.assertFalse(results['test2@example.com']['success'])
        self.assertTrue(results['test3@example.com']['success'])
        
        # Check email personalization
        # First email should use User 1 in template
        self.assertEqual(mock_send_email.call_args_list[0][1]['body_html'], '<p>Hello User 1</p>')
        # Second email has no personalization data so should use the template as-is
        self.assertEqual(mock_send_email.call_args_list[1][1]['body_html'], '<p>Hello {name}</p>')
        # Third email should use User 3 in template
        self.assertEqual(mock_send_email.call_args_list[2][1]['body_html'], '<p>Hello User 3</p>')
    
    def test_verify_email_address(self):
        """Test email address verification"""
        # Valid email
        valid, error = verify_email_address('user@example.com')
        self.assertTrue(valid)
        self.assertIsNone(error)
        
        # Invalid email formats
        invalid_cases = [
            '',                  # Empty
            'userexample.com',   # Missing @
            'user@',             # Missing domain
            'user@invalid',      # Invalid TLD
            '@example.com',      # Missing username
            'user@.com'          # Missing domain name
        ]
        
        for email in invalid_cases:
            valid, error = verify_email_address(email)
            self.assertFalse(valid)
            self.assertIsNotNone(error)
    
    def test_verify_bulk_email_addresses(self):
        """Test bulk email verification"""
        emails = [
            'valid@example.com',
            'invalid@',
            'another.valid@example.org'
        ]
        
        results = verify_bulk_email_addresses(emails)
        
        self.assertEqual(len(results), 3)
        self.assertTrue(results['valid@example.com']['valid'])
        self.assertFalse(results['invalid@']['valid'])
        self.assertTrue(results['another.valid@example.org']['valid'])
    
    @patch('app.services.email_service.email_statuses')
    @patch('app.services.email_service.queue_lock')
    def test_track_email_open(self, mock_lock, mock_email_statuses):
        """Test tracking email opens"""
        # Setup mock
        mock_email_statuses.__contains__.return_value = True
        mock_email_status = MagicMock()
        mock_email_statuses.__getitem__.return_value = mock_email_status
        mock_email_status.metadata = {}
        
        # Call function
        result = track_email_open('test-email-id', '192.168.1.1')
        
        # Check results
        self.assertTrue(result)
        self.assertEqual(mock_email_status.status, EmailStatus.OPENED)
        self.assertEqual(len(mock_email_status.metadata.get('opens')), 1)
        self.assertEqual(mock_email_status.metadata['opens'][0]['ip_address'], '192.168.1.1')
    
    @patch('app.services.email_service.email_statuses')
    @patch('app.services.email_service.queue_lock')
    def test_track_email_click(self, mock_lock, mock_email_statuses):
        """Test tracking email link clicks"""
        # Setup mock
        mock_email_statuses.__contains__.return_value = True
        mock_email_status = MagicMock()
        mock_email_statuses.__getitem__.return_value = mock_email_status
        mock_email_status.metadata = {}
        
        # Call function
        result = track_email_click('test-email-id', 'https://example.com', '192.168.1.1')
        
        # Check results
        self.assertTrue(result)
        self.assertEqual(mock_email_status.status, EmailStatus.CLICKED)
        self.assertEqual(len(mock_email_status.metadata.get('clicks')), 1)
        self.assertEqual(mock_email_status.metadata['clicks'][0]['url'], 'https://example.com')
        self.assertEqual(mock_email_status.metadata['clicks'][0]['ip_address'], '192.168.1.1')
    
    @patch('app.services.email_service.email_statuses')
    @patch('app.services.email_service.queue_lock')
    def test_get_email_status(self, mock_lock, mock_email_statuses):
        """Test retrieving email status"""
        # Setup mock for existing email
        mock_email_statuses.__contains__.return_value = True
        mock_email_status = MagicMock()
        mock_email_statuses.__getitem__.return_value = mock_email_status
        mock_email_status.email_id = 'test-email-id'
        mock_email_status.recipient = 'test@example.com'
        mock_email_status.subject = 'Test Subject'
        mock_email_status.status = EmailStatus.DELIVERED
        mock_email_status.queued_at = datetime(2023, 1, 1, 12, 0, 0)
        mock_email_status.sent_at = datetime(2023, 1, 1, 12, 0, 5)
        mock_email_status.delivery_attempts = 1
        mock_email_status.last_error = None
        mock_email_status.metadata = {'test': 'data'}
        
        # Call function
        result = get_email_status('test-email-id')
        
        # Check results
        self.assertIsNotNone(result)
        self.assertEqual(result['email_id'], 'test-email-id')
        self.assertEqual(result['recipient'], 'test@example.com')
        self.assertEqual(result['status'], EmailStatus.DELIVERED)
        self.assertEqual(result['metadata'], {'test': 'data'})
        
        # Test non-existent email
        mock_email_statuses.__contains__.return_value = False
        result = get_email_status('non-existent-id')
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
