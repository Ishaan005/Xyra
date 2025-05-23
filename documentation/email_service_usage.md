# Email Service Usage Guide

This guide provides examples of how to use the email service in the Xyra application.

## Basic Email Sending

```python
from app.services.email_service import send_email

success, error = send_email(
    to_email="customer@example.com",
    subject="Welcome to Xyra",
    body_html="<h1>Welcome!</h1><p>Thank you for choosing Xyra.</p>",
    body_text="Welcome! Thank you for choosing Xyra.",
)

if not success:
    print(f"Failed to send email: {error}")
```

## Sending an Email with Attachments

```python
from app.services.email_service import send_email

# Prepare attachments as list of tuples (filename, data)
with open("document.pdf", "rb") as f:
    pdf_data = f.read()
    
attachments = [
    ("document.pdf", pdf_data),
]

success, error = send_email(
    to_email="customer@example.com",
    subject="Your Document",
    body_html="<p>Please find the requested document attached.</p>",
    body_text="Please find the requested document attached.",
    attachments=attachments
)
```

## Sending an Invoice Email

```python
from app.services.email_service import send_invoice_email

success, error = send_invoice_email(
    invoice_id=invoice.id,
    recipient_email="customer@example.com",
    organization=organization,
    invoice=invoice,
    line_items=line_items,
    payment_link="https://payment-url.com/invoice123",
    include_pdf=True,
    custom_message="Thank you for your business. Please let us know if you have any questions."
)

if not success:
    print(f"Failed to send invoice email: {error}")
```

## Customizing Retry Logic

```python
from app.services.email_service import send_email

success, error = send_email(
    to_email="customer@example.com",
    subject="Important Notification",
    body_html="<p>This is an important notification.</p>",
    body_text="This is an important notification.",
    max_retries=5,  # Increase from default of 3
    retry_delay=2   # Wait 2 seconds between retries
)
```

## Common Email Use Cases

### Welcome Email

```python
def send_welcome_email(user_email, user_name):
    subject = "Welcome to Xyra"
    html = f"""
    <h1>Welcome to Xyra, {user_name}!</h1>
    <p>Thank you for signing up. We're excited to have you on board.</p>
    <p>If you have any questions, please don't hesitate to contact our support team.</p>
    """
    text = f"""
    Welcome to Xyra, {user_name}!
    
    Thank you for signing up. We're excited to have you on board.
    
    If you have any questions, please don't hesitate to contact our support team.
    """
    
    return send_email(to_email=user_email, subject=subject, body_html=html, body_text=text)
```

### Password Reset Email

```python
def send_password_reset_email(user_email, reset_link):
    subject = "Reset Your Xyra Password"
    html = f"""
    <h1>Password Reset Request</h1>
    <p>We received a request to reset your password.</p>
    <p>Click the link below to reset your password:</p>
    <p><a href="{reset_link}">Reset Password</a></p>
    <p>If you didn't request this, you can safely ignore this email.</p>
    """
    text = f"""
    Password Reset Request
    
    We received a request to reset your password.
    
    Click the link below to reset your password:
    {reset_link}
    
    If you didn't request this, you can safely ignore this email.
    """
    
    return send_email(to_email=user_email, subject=subject, body_html=html, body_text=text)
```

## Best Practices

1. **Always provide both HTML and text versions** of your email to ensure it displays properly in all email clients.

2. **Use descriptive subject lines** that clearly indicate the purpose of the email.

3. **Keep emails concise and focused** on a single topic or action.

4. **Handle email sending errors gracefully** by checking the success status and providing appropriate feedback to users.

5. **Use proper error logging** to capture and troubleshoot email sending issues.

6. **Consider rate limiting** for bulk email operations to avoid triggering spam filters or hitting provider limits.

7. **Test emails thoroughly** before sending them to customers, especially when using templates with variables.

## Troubleshooting

If emails are not being sent, check:

1. Email configuration settings in your `.env` file
2. SMTP server connection (see `documentation/email_service_configuration.md`)
3. Application logs for detailed error messages
