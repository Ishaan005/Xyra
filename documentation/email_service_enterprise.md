# Enterprise Email Functionality

This document outlines the enterprise-grade email functionality implemented in the Xyra application.

## Key Features

1. **Email Delivery Status Tracking**
   - Real-time tracking of email status (queued, sent, delivered, failed, bounced)
   - Open and click tracking for engagement metrics
   - Comprehensive error handling and logging

2. **Bulk Email Processing**
   - Efficient sending of emails to multiple recipients
   - Batching to prevent rate limiting
   - Personalization of content per recipient
   - Parallel processing with customizable worker count

3. **Email Verification**
   - Basic syntax validation
   - MX record checking (when DNS resolver is available)
   - Bulk verification capabilities

4. **Advanced Email Security**
   - DKIM signature support for improved deliverability
   - SPF compatibility
   - TLS encryption for all connections

5. **High Availability and Reliability**
   - Retry logic with configurable attempts and delays
   - Background task processing for asynchronous operations
   - Queue system for managing email workloads

6. **Rich Template Support**
   - HTML and plain text email templates
   - Variable substitution for personalization
   - Custom styling and branding options

## API Endpoints

### Single Email Sending

```
POST /api/v1/invoices/send-email
```

Send a single invoice to a recipient via email.

**Request Body**:
```json
{
  "invoice_id": 123,  // Either invoice_id or invoice_number is required
  "invoice_number": "INV-001",
  "recipient_email": "client@example.com",
  "include_pdf": true,
  "message": "Custom message to include in the email",
  "payment_link": "https://payment.url/checkout",
  "cc": ["manager@example.com"],
  "bcc": ["records@example.com"],
  "reply_to": "billing@yourcompany.com"
}
```

### Bulk Email Sending

```
POST /api/v1/invoices/send-bulk-email
```

Send an invoice to multiple recipients efficiently.

**Request Body**:
```json
{
  "invoice_id": 123,
  "recipient_emails": ["client1@example.com", "client2@example.com"],
  "include_pdf": true,
  "message": "Custom message to include in the email",
  "payment_link": "https://payment.url/checkout",
  "cc": ["manager@example.com"],
  "bcc": ["records@example.com"],
  "reply_to": "billing@yourcompany.com",
  "personalize_content": true,
  "recipient_variables": {
    "client1@example.com": {
      "name": "John Doe",
      "company": "ABC Corp"
    },
    "client2@example.com": {
      "name": "Jane Smith",
      "company": "XYZ LLC"
    }
  }
}
```

### Email Status Tracking

```
GET /api/v1/invoices/{invoice_id}/email-status
```

Get detailed email delivery status information for an invoice.

**Response**:
```json
{
  "invoice_id": 123,
  "invoice_number": "INV-001",
  "email_history": [...],
  "email_statuses": {...},
  "total_emails_sent": 5,
  "total_opens": 3,
  "total_clicks": 2,
  "total_delivered": 5,
  "total_failed": 0
}
```

### Tracking Endpoints

The following endpoints are used internally for tracking email interactions:

- `GET /api/v1/email/track-open/{email_id}` - Records email opens
- `GET /api/v1/email/track-click/{email_id}` - Records link clicks
- `GET /api/v1/email/status/{email_id}` - Gets the status of a specific email

## Configuration

Configure email settings in your environment variables:

```
# SMTP Configuration
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=username
SMTP_PASSWORD=password
SMTP_TLS=True

# Sender Information
EMAILS_FROM_EMAIL=noreply@example.com
EMAILS_FROM_NAME=Xyra

# DKIM Configuration (Optional)
DKIM_PRIVATE_KEY=/path/to/private.key
DKIM_SELECTOR=selector1
```

## Usage Examples

### Basic Invoice Email

```python
from app.services import email_service

success, error_msg, email_id = email_service.send_invoice_email(
    invoice_id=invoice.id,
    recipient_email="client@example.com",
    organization=organization,
    invoice=invoice,
    line_items=invoice.line_items,
    include_pdf=True
)

if success:
    print(f"Email sent successfully with ID: {email_id}")
else:
    print(f"Failed to send email: {error_msg}")
```

### Bulk Emails with Personalization

```python
from app.services import email_service

results = email_service.send_bulk_emails(
    recipients=["client1@example.com", "client2@example.com"],
    subject="Your Invoice {invoice_number}",
    body_html_template="<p>Hello {name}, your invoice is ready.</p>",
    body_text_template="Hello {name}, your invoice is ready.",
    template_vars={
        "client1@example.com": {"name": "John", "invoice_number": "INV-001"},
        "client2@example.com": {"name": "Jane", "invoice_number": "INV-002"}
    },
    batch_size=10,
    track_opens=True,
    track_clicks=True
)
```

## Best Practices

1. **Use Background Tasks**: For non-urgent emails, use the background task option to prevent blocking API responses.
   
2. **Verify Recipient Emails**: Always validate email addresses before sending to reduce bounces.

3. **Implement Exponential Backoff**: For retries, consider using exponential backoff to avoid overloading mail servers.

4. **Monitor Email Statuses**: Regularly check email delivery statuses, especially for important communications.

5. **Use DKIM Signatures**: Enable DKIM signing to improve deliverability and prevent spoofing.

6. **Batch Large Sends**: For very large email campaigns, break them into multiple batches with pauses between.

7. **Handle Bounce Notifications**: Set up a system to process bounce notifications from your email provider.

8. **Regular Queue Maintenance**: If using the built-in queue system, monitor queue length and worker performance.

## Troubleshooting

### Common Issues

1. **Emails not being delivered**: 
   - Check SMTP settings
   - Verify recipient email address is valid
   - Check if DKIM is properly configured
   - Look for error messages in logs

2. **High bounce rate**:
   - Implement email verification
   - Clean your recipient lists regularly
   - Reduce sending frequency

3. **Slow performance when sending many emails**:
   - Increase worker count
   - Use larger batch sizes
   - Ensure your SMTP provider can handle the volume

### Log Analysis

For email-related issues, check the application logs with:

```
grep "email_service" /path/to/application.log
```

Look for entries with the following log levels:
- ERROR: Failed deliveries, configuration issues
- WARNING: Retry attempts, temporary failures
- INFO: Successful sends, status changes

## Security Considerations

1. **Protect Email Credentials**: Always store SMTP credentials securely using environment variables or a secrets manager.

2. **Use TLS**: Ensure TLS is enabled for all SMTP connections.

3. **Rate Limiting**: Implement rate limiting to prevent abuse of the email sending endpoints.

4. **Validate Recipients**: Only allow sending to validated email addresses.

5. **Anti-Spoofing**: Configure SPF and DKIM correctly to prevent email spoofing.

## Performance Metrics

Monitor the following metrics for email performance:

- **Delivery Rate**: Percentage of emails successfully delivered
- **Open Rate**: Percentage of delivered emails that were opened
- **Click Rate**: Percentage of opened emails with clicked links
- **Bounce Rate**: Percentage of emails that bounced
- **Delivery Time**: Average time from sending to delivery
