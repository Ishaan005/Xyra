# Invoice Email Functionality

## Overview

This document describes the email functionality implemented in the Xyra invoicing system.

## Frontend Implementation

The frontend implements an `InvoicePaymentEmailDialog` component that allows users to:

- Enter a recipient email address
- Add a custom message to the email
- Include a payment link (optional)
- Include a PDF attachment of the invoice (optional)

## Backend Implementation

The backend provides the following functionality:

### Email Service (`email_service.py`)

1. **Generic Email Sending**: `send_email()` function provides a generic way to send emails with:
   - HTML and plain text content
   - Optional file attachments
   - Proper error handling and logging

2. **Invoice Email**: `send_invoice_email()` function provides a specialized way to send invoices with:
   - HTML email template with professional formatting
   - Payment link as a button (if provided)
   - PDF attachment (optional)
   - Custom message (optional)

### Email Templates (`templates/email_templates.py`) 

Contains reusable email templates and components for:
- Invoice HTML template
- Invoice plain text template
- Payment button HTML
- Custom message formatting

### API Endpoint (`/api/v1/invoices/send-email`)

- Validates the request data
- Retrieves the invoice information
- Checks user permissions
- Sends the email using the email service
- Records the email in the invoice metadata, including:
  - Timestamp when the email was sent
  - Recipient email address
  - Who sent the email (user email)
  - Whether a PDF attachment was included
  - Whether a payment link was included

## Configuration

Email functionality requires proper configuration of SMTP settings and other environment variables.

For detailed configuration instructions, see:
- [Email Service Configuration Guide](./email_service_configuration.md)

For usage examples and best practices, see:
- [Email Service Usage Guide](./email_service_usage.md)

Basic environment variables required:

```
SMTP_HOST=your-smtp-server.com
SMTP_PORT=587
SMTP_USER=your-username
SMTP_PASSWORD=your-password
SMTP_TLS=True
EMAILS_FROM_EMAIL=noreply@yourcompany.com
EMAILS_FROM_NAME=Xyra
```

## Error Handling and Reliability

The system includes proper error handling for:
- Email configuration issues (returns 503 Service Unavailable)
- SMTP connection errors
- Invalid email addresses (client-side validation)
- Missing invoice data
- Permission issues

Specific HTTP status codes are used:
- 400: Bad Request - Missing required fields or invalid data
- 403: Forbidden - User doesn't have permissions for the invoice
- 404: Not Found - Invoice or organization not found
- 503: Service Unavailable - Email service not properly configured
- 500: Internal Server Error - Other email sending issues

Retry logic has been implemented to improve email sending reliability:
- Automatic retries on transient SMTP errors
- Configurable number of retries (default: 3)
- Configurable delay between retry attempts (default: 1 second)
- Detailed error logging for failed attempts

## Future Enhancements

Potential future enhancements:

### Templates and Personalization
- Email templates for different types of invoices (regular, reminder, final notice)
- Localization support for email templates (multiple languages)
- Dynamic content personalization based on customer data and invoice history
- Custom branding options for different organizations

### Automation and Scheduling
- Scheduled follow-up emails for overdue invoices
- Automatic payment reminder sequences
- Batch sending capabilities for high-volume use cases
- Email queuing system for handling sending during peak loads

### Analytics and Tracking
- Email open and click tracking
- Payment link click conversion analytics
- Delivery status monitoring and reporting
- A/B testing for different email formats and content

### Integration
- Integration with popular CRM systems
- Calendar invites for payment discussion meetings
- SMS fallback for critical notifications
- Support for digital signature requests within emails
