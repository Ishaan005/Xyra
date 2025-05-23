#!/usr/bin/env python
"""
Email configuration test utility.

This script tests the email configuration by sending a test email.
It's a useful tool for verifying that your SMTP settings are correct.

Usage:
    python test_email_config.py [recipient_email]
"""

import sys
import os
from pathlib import Path
import argparse
import logging

# Add the parent directory to the path so we can import the app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.email_service import send_email
from app.core.config import settings


def setup_logging():
    """Configure logging for the script"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Test email configuration by sending a test email")
    parser.add_argument(
        "recipient", 
        nargs="?", 
        help="Email address to send the test email to"
    )
    parser.add_argument(
        "--from", 
        dest="from_email", 
        help="Sender email address (uses EMAILS_FROM_EMAIL from config if not provided)"
    )
    return parser.parse_args()


def main():
    """Main function to send a test email"""
    setup_logging()
    logger = logging.getLogger("test_email")
    
    args = parse_args()
    
    # Get recipient email
    recipient = args.recipient
    if not recipient:
        recipient = input("Enter recipient email address: ")
    
    logger.info("Testing email configuration...")
    logger.info(f"SMTP Server: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
    logger.info(f"TLS Enabled: {settings.SMTP_TLS}")
    logger.info(f"From: {settings.EMAILS_FROM_EMAIL}")
    logger.info(f"To: {recipient}")
    
    # Send test email
    html_content = """
    <html>
        <body>
            <h2>Email Configuration Test</h2>
            <p>This is a test email from the Xyra invoicing system.</p>
            <p>If you received this email, your email configuration is working correctly!</p>
            <p style="color: #4CAF50;"><strong>✓ Success!</strong></p>
        </body>
    </html>
    """
    
    text_content = """
    Email Configuration Test
    
    This is a test email from the Xyra invoicing system.
    
    If you received this email, your email configuration is working correctly!
    
    ✓ Success!
    """
    
    success, error = send_email(
        to_email=recipient,
        subject="Xyra Email Configuration Test",
        body_html=html_content,
        body_text=text_content,
        from_email=args.from_email
    )
    
    if success:
        logger.info("✓ Test email sent successfully!")
        logger.info(f"  Please check {recipient} inbox to confirm receipt.")
    else:
        logger.error(f"✗ Failed to send test email: {error}")
        logger.error("  Please check your email configuration.")
        sys.exit(1)


if __name__ == "__main__":
    main()
