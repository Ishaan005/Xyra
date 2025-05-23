#!/usr/bin/env python
"""
Script to test email configuration and features

This utility helps verify that your email configuration is working correctly
and demonstrates how to use the various email features.

Usage:
    python test_email_features.py [options]

Options:
    -h, --help              Show this help message
    -t, --test-config       Only test the email configuration
    -s, --send-test-email   Send a test email
    -b, --bulk-test         Test bulk email capabilities
    -v, --verify-email      Verify an email address
    --recipient EMAIL       Email recipient (required for send tests)
    --count N               Number of test emails for bulk testing (default: 5)
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from app.services import email_service


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_email_features')


def check_email_config():
    """Check if email configuration is set correctly"""
    logger.info("Checking email configuration...")
    
    config_ok = True
    missing = []
    
    # Check required settings
    if not settings.SMTP_HOST:
        missing.append("SMTP_HOST")
        config_ok = False
    
    if not settings.SMTP_PORT:
        missing.append("SMTP_PORT")
        config_ok = False
    
    if not settings.EMAILS_FROM_EMAIL:
        missing.append("EMAILS_FROM_EMAIL")
        config_ok = False
    
    # Check optional settings
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP_USER or SMTP_PASSWORD not set - anonymous SMTP will be used")
    
    # Check DKIM settings
    dkim_available = email_service.DKIM_AVAILABLE
    if not dkim_available:
        logger.warning("DKIM package not installed - DKIM signatures will not be available")
    
    if dkim_available and not (settings.DKIM_PRIVATE_KEY and settings.DKIM_SELECTOR):
        logger.warning("DKIM_PRIVATE_KEY or DKIM_SELECTOR not set - DKIM signing will be disabled")
    
    # Report results
    if config_ok:
        logger.info("✅ Email configuration looks good")
        logger.info(f"SMTP Server: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
        logger.info(f"From Address: {settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>")
        logger.info(f"TLS Enabled: {settings.SMTP_TLS}")
        return True
    else:
        logger.error(f"❌ Email configuration incomplete. Missing: {', '.join(missing)}")
        return False


def test_smtp_connection():
    """Test connectivity to the SMTP server"""
    logger.info("Testing SMTP server connection...")
    
    import smtplib
    
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
                logger.info("✅ TLS connection established")
            
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                logger.info("✅ SMTP authentication successful")
            
            logger.info("✅ SMTP connection test successful")
            return True
    except Exception as e:
        logger.error(f"❌ SMTP connection failed: {str(e)}")
        return False


def send_test_email(recipient: str):
    """Send a test email to verify configuration"""
    logger.info(f"Sending test email to {recipient}...")
    
    # Create simple HTML and text content
    html_content = """
    <html>
    <body>
        <h1>Email Test Successful!</h1>
        <p>This is a test email from the Xyra system.</p>
        <p>If you're seeing this, your email configuration is working correctly.</p>
        <hr>
        <p style="color: gray; font-size: small;">Sent at: {timestamp}</p>
    </body>
    </html>
    """.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    text_content = """
    Email Test Successful!
    
    This is a test email from the Xyra system.
    If you're seeing this, your email configuration is working correctly.
    
    Sent at: {timestamp}
    """.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Send the email with tracking
    success, error_msg, email_id = email_service.send_email(
        to_email=recipient,
        subject="Xyra Email Test",
        body_html=html_content,
        body_text=text_content,
        track_opens=True,
        track_clicks=True,
        add_dkim_signature=True,
        metadata={"test": True, "timestamp": datetime.now().isoformat()}
    )
    
    if success:
        logger.info(f"✅ Test email sent successfully. Email ID: {email_id}")
        return True
    else:
        logger.error(f"❌ Failed to send test email: {error_msg}")
        return False


def test_bulk_emails(recipient: str, count: int = 5):
    """Test bulk email sending capabilities"""
    logger.info(f"Testing bulk email sending ({count} emails)...")
    
    # Create a recipient list with the same address repeated
    recipients = [recipient] * count
    
    # Create template with personalization
    html_template = """
    <html>
    <body>
        <h1>Bulk Email Test: Email #{email_num}</h1>
        <p>This is test email {email_num} of {total_count}.</p>
        <p>The current time is {timestamp}.</p>
        <hr>
        <p style="color: gray; font-size: small;">Batch ID: {batch_id}</p>
    </body>
    </html>
    """
    
    text_template = """
    Bulk Email Test: Email #{email_num}
    
    This is test email {email_num} of {total_count}.
    The current time is {timestamp}.
    
    Batch ID: {batch_id}
    """
    
    # Create unique variables for each email
    import uuid
    batch_id = str(uuid.uuid4())
    template_vars = {}
    
    for i in range(count):
        template_vars[recipient] = {
            "email_num": i + 1,
            "total_count": count,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "batch_id": batch_id
        }
    
    # Send bulk emails
    results = email_service.send_bulk_emails(
        recipients=recipients,
        subject="Xyra Bulk Email Test #{email_num}",
        body_html_template=html_template,
        body_text_template=text_template,
        template_vars=template_vars,
        batch_size=2,  # Small batch size to demonstrate batching
        pause_between_batches=1,  # 1 second pause between batches
        track_opens=True,
        track_clicks=True,
        verify_emails=True
    )
    
    # Report results
    success_count = sum(1 for r in results.values() if r['success'])
    logger.info(f"✅ Bulk email test completed: {success_count}/{count} sent successfully")
    
    return success_count == count


def verify_email_test(email: str):
    """Test email verification functionality"""
    logger.info(f"Verifying email address: {email}")
    
    valid, error = email_service.verify_email_address(email)
    
    if valid:
        logger.info(f"✅ Email address '{email}' is valid")
    else:
        logger.error(f"❌ Email address '{email}' is invalid: {error}")
    
    return valid


def main():
    """Main function to parse arguments and execute tests"""
    parser = argparse.ArgumentParser(description="Test email functionality")
    parser.add_argument("-t", "--test-config", action="store_true", help="Only test the email configuration")
    parser.add_argument("-s", "--send-test-email", action="store_true", help="Send a test email")
    parser.add_argument("-b", "--bulk-test", action="store_true", help="Test bulk email capabilities")
    parser.add_argument("-v", "--verify-email", action="store_true", help="Verify an email address")
    parser.add_argument("--recipient", type=str, help="Email recipient (required for send tests)")
    parser.add_argument("--count", type=int, default=5, help="Number of test emails for bulk testing")
    
    args = parser.parse_args()
    
    # Setup script environment
    setup_ok = True
    
    # Always check the config first
    config_ok = check_email_config()
    
    # Test SMTP connection
    if config_ok and not args.test_config:
        connection_ok = test_smtp_connection()
        if not connection_ok:
            setup_ok = False
    
    # If only testing config, exit here
    if args.test_config:
        return config_ok
    
    # If setup failed, exit
    if not setup_ok:
        logger.error("Setup checks failed. Please fix configuration issues before proceeding.")
        return False
    
    # Execute requested tests
    if args.verify_email:
        if not args.recipient:
            logger.error("Email address required for verification test")
            return False
        verify_email_test(args.recipient)
    
    if args.send_test_email:
        if not args.recipient:
            logger.error("Recipient email required for send test")
            return False
        send_test_email(args.recipient)
    
    if args.bulk_test:
        if not args.recipient:
            logger.error("Recipient email required for bulk test")
            return False
        test_bulk_emails(args.recipient, args.count)
    
    # If no specific tests requested, print help
    if not (args.test_config or args.send_test_email or args.bulk_test or args.verify_email):
        parser.print_help()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
