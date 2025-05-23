# Email Service Configuration Guide

This guide explains how to set up and configure the email service for the Xyra invoicing system.

## 1. Environment Variables

The following environment variables must be set in your `.env` file:

```
# Email Configuration
SMTP_HOST=your-smtp-server.com
SMTP_PORT=587
SMTP_USER=your-username
SMTP_PASSWORD=your-secure-password
SMTP_TLS=True
EMAILS_FROM_EMAIL=noreply@yourcompany.com
EMAILS_FROM_NAME=Xyra
```

## 2. SMTP Server Options

### Gmail SMTP
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_TLS=True
```

### Microsoft 365 / Office 365
```
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_TLS=True
```

### Amazon SES (US East)
```
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_TLS=True
```

### SendGrid
```
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_TLS=True
```

## 3. Security Considerations

1. **Password Security**: Never commit your SMTP password to version control. Use environment variables or a secure vault.

2. **TLS Encryption**: Always enable TLS by setting `SMTP_TLS=True` to ensure emails are sent securely.

3. **API Keys**: For services like SendGrid, Mailgun, etc., use API keys instead of your account password when possible.

4. **IP Allowlisting**: Some SMTP services require you to allowlist the IPs that will connect to them. Make sure to configure this for your production servers.

## 4. Testing Email Configuration

You can test your email configuration by running:

```python
from app.services.email_service import send_email

success, error = send_email(
    to_email="test@example.com",
    subject="Test Email",
    body_html="<p>This is a test email.</p>",
    body_text="This is a test email."
)

print(f"Email sent: {success}")
if not success:
    print(f"Error: {error}")
```

## 5. Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if SMTP_HOST and SMTP_PORT are correct
   - Ensure firewall is not blocking outgoing connections to the SMTP port

2. **Authentication Failed**
   - Verify SMTP_USER and SMTP_PASSWORD are correct
   - Some services require an app-specific password instead of your account password

3. **TLS/SSL Issues**
   - Try different port (465 for SSL, 587 for TLS)
   - Ensure your Python environment has proper SSL support

4. **Rate Limiting**
   - Many SMTP providers have sending limits; check if you've exceeded them

### Logging

Email sending failures are logged. Check the application logs for detailed error messages.
