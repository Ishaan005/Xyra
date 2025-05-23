import os
import time
import logging
import smtplib
import uuid
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formataddr, formatdate, make_msgid
from typing import List, Optional, Tuple, Dict, Any, Union, Set
from datetime import datetime
from collections import deque
from threading import Thread, Lock
from dataclasses import dataclass, field

# For DKIM support
try:
    import dkim
    DKIM_AVAILABLE = True
except ImportError:
    DKIM_AVAILABLE = False

from fastapi import BackgroundTasks

from app.core.config import settings
from app.models.invoice import Invoice
from app.models.organization import Organization
from app.services.pdf_service import generate_invoice_pdf
from app.templates.email_templates import (
    get_invoice_email_html_template,
    get_invoice_email_text_template,
    get_payment_button_html,
    get_custom_message_html
)

# Configure logging
logger = logging.getLogger(__name__)

# Email delivery status constants
class EmailStatus:
    QUEUED = "queued"
    SENDING = "sending"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    OPENED = "opened"
    CLICKED = "clicked"

@dataclass
class EmailDeliveryStatus:
    """Track the delivery status of an email"""
    email_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    recipient: str = ""
    subject: str = ""
    status: str = EmailStatus.QUEUED
    queued_at: datetime = field(default_factory=datetime.now)
    sent_at: Optional[datetime] = None
    delivery_attempts: int = 0
    last_error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_status(self, status: str, error: Optional[str] = None):
        """Update the status of this email"""
        self.status = status
        if status == EmailStatus.SENDING:
            self.delivery_attempts += 1
        elif status == EmailStatus.DELIVERED:
            self.sent_at = datetime.now()
        if error:
            self.last_error = error
        return self

# Simple in-memory email queue (in a production environment, use Redis or similar)
email_queue = deque()
email_statuses: Dict[str, EmailDeliveryStatus] = {}
queue_lock = Lock()  # For thread safety

def send_email(
    to_email: str,
    subject: str,
    body_html: str,
    body_text: str,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None,
    cc: Optional[Union[str, List[str]]] = None,
    bcc: Optional[Union[str, List[str]]] = None,
    reply_to: Optional[str] = None,
    attachments: Optional[List[tuple]] = None,  # List of (filename, data)
    max_retries: int = 3,
    retry_delay: int = 1,
    priority: str = "normal",  # normal, high, low
    track_opens: bool = False,
    track_clicks: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
    add_dkim_signature: bool = False,
    background_task: Optional[BackgroundTasks] = None
) -> tuple[bool, Optional[str], Optional[str]]:
    """
    Send an email with optional attachments and tracking
    
    Args:
        to_email: Recipient email address or list of addresses
        subject: Email subject
        body_html: HTML version of email body
        body_text: Plain text version of email body
        from_email: Sender email address (uses default if not provided)
        from_name: Sender name (uses default if not provided)
        cc: Carbon copy recipients as string or list
        bcc: Blind carbon copy recipients as string or list
        reply_to: Reply-to email address
        attachments: List of tuples (filename, file_data) to attach
        max_retries: Maximum number of retries if sending fails
        retry_delay: Delay in seconds between retries
        priority: Email priority (normal, high, low)
        track_opens: Add tracking pixel for open tracking
        track_clicks: Enable click tracking for links
        metadata: Additional metadata to store with email status
        add_dkim_signature: Whether to add DKIM signature (requires dkim package)
        background_task: Optional BackgroundTasks for async sending
        
    Returns:
        tuple: (success: bool, error_message: Optional[str], email_id: Optional[str])
    """
    if not settings.SMTP_HOST or not settings.SMTP_PORT:
        error_msg = "Email service not configured. Please set SMTP_HOST and SMTP_PORT environment variables."
        logger.error(error_msg)
        return False, error_msg, None
    
    # Create email tracking ID and status
    email_tracking_id = str(uuid.uuid4())
    
    # Initialize email delivery status tracking
    email_status = EmailDeliveryStatus(
        email_id=email_tracking_id,
        recipient=to_email if isinstance(to_email, str) else ", ".join(to_email),
        subject=subject,
        metadata=metadata or {}
    )
    
    # Store in tracking dictionary
    with queue_lock:
        email_statuses[email_tracking_id] = email_status
    
    # Use background task if provided
    if background_task:
        background_task.add_task(
            _send_email_async, 
            email_tracking_id,
            to_email, subject, body_html, body_text,
            from_email, from_name, cc, bcc, reply_to,
            attachments, max_retries, retry_delay, 
            priority, track_opens, track_clicks,
            add_dkim_signature
        )
        return True, None, email_tracking_id
    
    # Otherwise, send synchronously
    return _send_email_sync(
        email_tracking_id,
        to_email, subject, body_html, body_text,
        from_email, from_name, cc, bcc, reply_to,
        attachments, max_retries, retry_delay, 
        priority, track_opens, track_clicks,
        add_dkim_signature
    )


async def _send_email_async(
    email_tracking_id: str,
    to_email: Union[str, List[str]],
    subject: str,
    body_html: str,
    body_text: str,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None,
    cc: Optional[Union[str, List[str]]] = None,
    bcc: Optional[Union[str, List[str]]] = None,
    reply_to: Optional[str] = None,
    attachments: Optional[List[tuple]] = None,
    max_retries: int = 3,
    retry_delay: int = 1,
    priority: str = "normal",
    track_opens: bool = False,
    track_clicks: bool = False,
    add_dkim_signature: bool = False
):
    """Asynchronous version of send_email for background tasks"""
    # This function enables us to call the synchronous send_email function
    # from an async context (e.g., from a FastAPI background task)
    _send_email_sync(
        email_tracking_id,
        to_email, subject, body_html, body_text,
        from_email, from_name, cc, bcc, reply_to,
        attachments, max_retries, retry_delay, 
        priority, track_opens, track_clicks,
        add_dkim_signature
    )
    

def _send_email_sync(
    email_tracking_id: str,
    to_email: Union[str, List[str]],
    subject: str,
    body_html: str,
    body_text: str,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None,
    cc: Optional[Union[str, List[str]]] = None,
    bcc: Optional[Union[str, List[str]]] = None,
    reply_to: Optional[str] = None,
    attachments: Optional[List[tuple]] = None,
    max_retries: int = 3,
    retry_delay: int = 1,
    priority: str = "normal",
    track_opens: bool = False,
    track_clicks: bool = False,
    add_dkim_signature: bool = False
) -> tuple[bool, Optional[str], Optional[str]]:
    """
    Synchronous implementation of email sending with tracking
    """
    # Update email status to sending
    with queue_lock:
        if email_tracking_id in email_statuses:
            email_statuses[email_tracking_id].update_status(EmailStatus.SENDING)
    
    try:
        # Prepare email
        from_email = from_email or settings.EMAILS_FROM_EMAIL
        from_name = from_name or settings.EMAILS_FROM_NAME
        
        # Convert string to list for consistency
        recipients = [to_email] if isinstance(to_email, str) else to_email
        cc_list = _convert_to_list(cc)
        bcc_list = _convert_to_list(bcc)
        
        # All recipients for SMTP sending
        all_recipients = list(recipients)
        if cc_list:
            all_recipients.extend(cc_list)
        if bcc_list:
            all_recipients.extend(bcc_list)
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = formataddr((from_name, from_email))
        message["To"] = ", ".join(recipients)
        message["Date"] = formatdate(localtime=True)
        message["Message-ID"] = make_msgid(domain=from_email.split("@")[-1])
        
        # Add CC if provided (visible to recipients)
        if cc_list:
            message["Cc"] = ", ".join(cc_list)
        
        # Add Reply-To if provided
        if reply_to:
            message["Reply-To"] = reply_to
            
        # Set priority headers if needed
        if priority == "high":
            message["X-Priority"] = "1"
            message["X-MSMail-Priority"] = "High"
            message["Importance"] = "High"
        elif priority == "low":
            message["X-Priority"] = "5"
            message["X-MSMail-Priority"] = "Low"
            message["Importance"] = "Low"
            
        # Add tracking pixel for open tracking
        if track_opens:
            tracking_pixel = f'<img src="{settings.FRONTEND_BASE_URL}/api/v1/email/track-open/{email_tracking_id}" width="1" height="1" alt="">'
            body_html = body_html + tracking_pixel
            
        # Add click tracking
        if track_clicks:
            # This is a simplified implementation. In production, you would
            # replace all links with tracking links that redirect through your server
            body_html = body_html.replace(
                'href="http', 
                f'href="{settings.FRONTEND_BASE_URL}/api/v1/email/track-click/{email_tracking_id}?url=http'
            )
        
        # Add HTML and text parts
        part1 = MIMEText(body_text, "plain")
        part2 = MIMEText(body_html, "html")
        message.attach(part1)
        message.attach(part2)
        
        # Add attachments if provided
        if attachments:
            for filename, file_data in attachments:
                part = MIMEApplication(file_data, Name=filename)
                part['Content-Disposition'] = f'attachment; filename="{filename}"'
                message.attach(part)
        
        # Add custom headers for tracking
        message["X-Xyra-Email-ID"] = email_tracking_id
        
        # Convert message to string
        message_str = message.as_string()
        
        # Add DKIM signature if available and requested
        if add_dkim_signature and DKIM_AVAILABLE and settings.DKIM_PRIVATE_KEY and settings.DKIM_SELECTOR:
            try:
                domain = from_email.split('@')[-1]
                with open(settings.DKIM_PRIVATE_KEY, 'rb') as f:
                    private_key = f.read()
                headers = [b"From", b"To", b"Subject"]
                sig = dkim.sign(
                    message=message_str.encode(),
                    selector=settings.DKIM_SELECTOR.encode(),
                    domain=domain.encode(),
                    privkey=private_key,
                    include_headers=headers
                )
                message_str = (sig + message_str.encode()).decode()
            except Exception as e:
                logger.warning(f"Failed to add DKIM signature: {str(e)}")
                
        # Implement retry logic
        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                # Connect to SMTP server and send email
                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                    if settings.SMTP_TLS:
                        server.starttls()
                        
                    if settings.SMTP_USER and settings.SMTP_PASSWORD:
                        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    
                    server.sendmail(from_email, all_recipients, message_str)
                
                # If we get here, message was sent successfully
                logger.info(f"Email sent successfully to {to_email}")
                
                # Update email status to delivered
                with queue_lock:
                    if email_tracking_id in email_statuses:
                        email_statuses[email_tracking_id].update_status(EmailStatus.DELIVERED)
                
                return True, None, email_tracking_id
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempt}/{max_retries} failed: {last_error}")
                
                # Update email status with error
                with queue_lock:
                    if email_tracking_id in email_statuses:
                        email_statuses[email_tracking_id].update_status(
                            EmailStatus.FAILED, 
                            error=last_error
                        )
                
                # Don't sleep if this was the last attempt
                if attempt < max_retries:
                    time.sleep(retry_delay)
        
        # If we get here, all attempts failed
        error_msg = f"Failed to send email after {max_retries} attempts. Last error: {last_error}"
        logger.error(error_msg)
        
        return False, error_msg, email_tracking_id
        
    except Exception as e:
        # This catches any errors outside the retry logic (e.g., during message preparation)
        error_msg = f"Failed to prepare email: {str(e)}"
        logger.error(error_msg)
        
        # Update email status
        with queue_lock:
            if email_tracking_id in email_statuses:
                email_statuses[email_tracking_id].update_status(EmailStatus.FAILED, error=error_msg)
                
        return False, error_msg, email_tracking_id


def _convert_to_list(value: Optional[Union[str, List[str]]]) -> List[str]:
    """Helper to convert string or list of strings to list"""
    if not value:
        return []
    if isinstance(value, str):
        return [value]
    return value


def send_invoice_email(
    invoice_id: int,
    recipient_email: str,
    organization: Organization,
    invoice: Invoice,
    line_items: list,
    payment_link: Optional[str] = None,
    include_pdf: bool = True,
    custom_message: Optional[str] = None,
    cc: Optional[Union[str, List[str]]] = None,
    bcc: Optional[Union[str, List[str]]] = None,
    reply_to: Optional[str] = None,
    background_task: Optional[BackgroundTasks] = None,
    track_opens: bool = True,
    track_clicks: bool = True,
) -> tuple[bool, Optional[str], Optional[str]]:
    """
    Send an invoice email with optional PDF attachment and tracking
    
    Args:
        invoice_id: ID of the invoice
        recipient_email: Email address to send the invoice to
        organization: Organization object
        invoice: Invoice object
        line_items: List of invoice line items
        payment_link: Optional payment link to include
        include_pdf: Whether to include the invoice PDF
        custom_message: Optional custom message to include
        cc: Carbon copy recipients
        bcc: Blind carbon copy recipients
        reply_to: Reply-to email address
        background_task: Optional BackgroundTasks for async sending
        track_opens: Whether to track email opens
        track_clicks: Whether to track link clicks
        
    Returns:
        tuple: (success: bool, error_message: Optional[str], email_tracking_id: Optional[str])
    """    
    try:
        # First, verify the recipient email address
        valid, error = verify_email_address(recipient_email)
        if not valid:
            return False, f"Invalid recipient email: {error}", None
        
        # Verify CC/BCC emails if provided
        if cc:
            cc_list = _convert_to_list(cc)
            for email in cc_list:
                valid, error = verify_email_address(email)
                if not valid:
                    return False, f"Invalid CC email ({email}): {error}", None
                    
        if bcc:
            bcc_list = _convert_to_list(bcc)
            for email in bcc_list:
                valid, error = verify_email_address(email)
                if not valid:
                    return False, f"Invalid BCC email ({email}): {error}", None
            
        # Validate required inputs
        if not invoice:
            return False, "Invoice data is required", None
        if not organization:
            return False, "Organization data is required", None
            
        # Prepare email subject
        subject = f"Invoice {invoice.invoice_number} from {organization.name}"
          
        # Prepare payment info
        payment_info = ""
        payment_link_text = ""
        if payment_link:
            payment_info = get_payment_button_html(payment_link)
            payment_link_text = f"Payment link: {payment_link}"
        
        # Add custom message if provided
        custom_message_html = get_custom_message_html(custom_message)
            
        # Prepare PDF message
        pdf_message = "A PDF copy of this invoice is attached to this email for your records." if include_pdf else "If you need a PDF copy of this invoice, please contact us."
        
        # Get the HTML template
        html_template = get_invoice_email_html_template()
        
        # Fill in the template variables
        html_content = html_template.format(
            invoice_number=invoice.invoice_number,
            organization_name=organization.name,
            issue_date=invoice.issue_date.strftime('%Y-%m-%d'),
            due_date=invoice.due_date.strftime('%Y-%m-%d'),
            currency=invoice.currency,
            total_amount=f"{invoice.total_amount:.2f}",
            custom_message_html=custom_message_html,
            payment_info=payment_info,
            pdf_message=pdf_message
        )
          
        # Get the text template
        text_template = get_invoice_email_text_template()
        
        # Fill in the template variables
        plain_text = text_template.format(
            invoice_number=invoice.invoice_number,
            organization_name=organization.name,
            issue_date=invoice.issue_date.strftime('%Y-%m-%d'),
            due_date=invoice.due_date.strftime('%Y-%m-%d'),
            currency=invoice.currency,
            total_amount=f"{invoice.total_amount:.2f}",
            custom_message=custom_message if custom_message else '',
            pdf_message=pdf_message,
            payment_link_text=payment_link_text
        )
        
        # Prepare attachments
        attachments = []
        if include_pdf:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
                generate_invoice_pdf(invoice, organization, line_items, tmpfile.name)
                with open(tmpfile.name, 'rb') as f:
                    pdf_data = f.read()
                    attachments.append((f"Invoice_{invoice.invoice_number}.pdf", pdf_data))
                # Clean up temp file
                os.unlink(tmpfile.name)
        
        # Prepare additional metadata for tracking
        metadata = {
            "invoice_id": invoice_id,
            "invoice_number": invoice.invoice_number,
            "organization_id": organization.id,
            "organization_name": organization.name,
            "payment_link_included": payment_link is not None,
            "pdf_included": include_pdf
        }
          
        # Send the email with tracking
        success, error_msg, email_id = send_email(
            to_email=recipient_email, 
            subject=subject,
            body_html=html_content,
            body_text=plain_text,
            cc=cc,
            bcc=bcc,
            reply_to=reply_to or organization.contact_email,
            attachments=attachments,
            background_task=background_task,
            track_opens=track_opens,
            track_clicks=track_clicks,
            metadata=metadata,
            priority="high",  # Invoices are important business documents
            add_dkim_signature=True  # Improve deliverability
        )
        
        return success, error_msg, email_id
    
    except Exception as e:
        error_msg = f"Error sending invoice email: {str(e)}"
        logger.error(error_msg)
        return False, error_msg, None

# Email queue worker functions
def start_email_queue_worker(max_workers: int = 1):
    """
    Start the email queue worker threads
    
    In a production environment, this would be a separate process or service
    using a persistent queue like Redis or RabbitMQ
    """
    for i in range(max_workers):
        worker = Thread(target=_email_queue_worker, daemon=True)
        worker.start()
    logger.info(f"Started {max_workers} email queue worker threads")

def _email_queue_worker():
    """
    Worker thread that processes emails from the queue
    """
    while True:
        try:
            # Attempt to get an email from the queue
            email_data = None
            with queue_lock:
                if email_queue:
                    email_data = email_queue.popleft()
                    
            if email_data:
                # Process the email
                _send_email_sync(**email_data)
            else:
                # No emails in queue, sleep briefly
                time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error in email queue worker: {str(e)}")
            time.sleep(1)  # Prevent tight loop if there's an error


def queue_email(**kwargs) -> str:
    """
    Add an email to the sending queue
    
    Returns the email tracking ID
    """
    email_tracking_id = str(uuid.uuid4())
    
    # Add tracking ID to kwargs
    kwargs["email_tracking_id"] = email_tracking_id
    
    # Initialize email status tracking
    recipient = kwargs.get("to_email", "unknown")
    subject = kwargs.get("subject", "No subject")
    metadata = kwargs.get("metadata", {})
    
    email_status = EmailDeliveryStatus(
        email_id=email_tracking_id,
        recipient=recipient if isinstance(recipient, str) else ", ".join(recipient),
        subject=subject,
        metadata=metadata or {}
    )
    
    # Store in tracking dictionary and add to queue
    with queue_lock:
        email_statuses[email_tracking_id] = email_status
        email_queue.append(kwargs)
        
    logger.info(f"Email queued: {subject} to {recipient} (ID: {email_tracking_id})")
    return email_tracking_id


def get_email_status(email_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the current status of an email
    
    Returns None if the email ID is not found
    """
    with queue_lock:
        if email_id in email_statuses:
            status = email_statuses[email_id]
            return {
                "email_id": status.email_id,
                "recipient": status.recipient,
                "subject": status.subject,
                "status": status.status,
                "queued_at": status.queued_at.isoformat(),
                "sent_at": status.sent_at.isoformat() if status.sent_at else None,
                "delivery_attempts": status.delivery_attempts,
                "last_error": status.last_error,
                "metadata": status.metadata
            }
    return None


# Email verification functions
def verify_email_address(email: str) -> tuple[bool, Optional[str]]:
    """
    Basic email address verification
    
    This is a simple implementation that checks for basic email format.
    For production, consider using a third-party API like Mailgun or Kickbox
    for more reliable email verification.
    
    Args:
        email: Email address to verify
        
    Returns:
        tuple: (is_valid: bool, error_message: Optional[str])
    """
    import re
    
    # Check for empty email
    if not email:
        return False, "Email address cannot be empty"
    
    # Basic format check using regex
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    if not email_pattern.match(email):
        return False, "Invalid email format"
    
    # Check domain has MX record (optional - requires DNS lookup)
    try:
        import dns.resolver
        domain = email.split('@')[-1]
        mx_records = dns.resolver.resolve(domain, 'MX')
        if not mx_records:
            return False, f"Domain {domain} has no mail server (MX record)"
    except ImportError:
        logger.warning("dns.resolver not available, skipping MX record check")
    except Exception as e:
        logger.warning(f"MX record check failed: {str(e)}")
    
    return True, None


def verify_bulk_email_addresses(emails: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Verify multiple email addresses at once
    
    Args:
        emails: List of email addresses to verify
        
    Returns:
        Dict mapping email addresses to verification results
    """
    results = {}
    for email in emails:
        is_valid, error = verify_email_address(email)
        results[email] = {
            "valid": is_valid,
            "error": error
        }
    return results


# Email tracking endpoint handlers
def track_email_open(email_id: str, ip_address: Optional[str] = None):
    """
    Record when an email is opened via tracking pixel
    """
    with queue_lock:
        if email_id in email_statuses:
            email_statuses[email_id].status = EmailStatus.OPENED
            email_statuses[email_id].metadata.setdefault("opens", []).append({
                "timestamp": datetime.now().isoformat(),
                "ip_address": ip_address
            })
            logger.info(f"Email {email_id} was opened")
            return True
    return False


def track_email_click(email_id: str, url: str, ip_address: Optional[str] = None):
    """
    Record when a link in an email is clicked
    """
    with queue_lock:
        if email_id in email_statuses:
            email_statuses[email_id].status = EmailStatus.CLICKED
            email_statuses[email_id].metadata.setdefault("clicks", []).append({
                "timestamp": datetime.now().isoformat(),
                "url": url,
                "ip_address": ip_address
            })
            logger.info(f"Link in email {email_id} was clicked: {url}")
            return True
    return False


def send_bulk_emails(
    recipients: List[str],
    subject: str,
    body_html_template: str,
    body_text_template: str,
    template_vars: Optional[Dict[str, Dict[str, Any]]] = None,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None,
    cc: Optional[Union[str, List[str]]] = None,
    bcc: Optional[Union[str, List[str]]] = None,
    reply_to: Optional[str] = None,
    attachments: Optional[Dict[str, List[tuple]]] = None,
    max_retries: int = 3,
    retry_delay: int = 1,
    priority: str = "normal",
    track_opens: bool = False,
    track_clicks: bool = False,
    add_dkim_signature: bool = False,
    batch_size: int = 20,
    pause_between_batches: int = 2,
    verify_emails: bool = True
) -> Dict[str, Dict[str, Any]]:
    """
    Send bulk emails to multiple recipients with personalization, batching, and tracking
    
    Args:
        recipients: List of recipient email addresses
        subject: Email subject (can include template vars like {name})
        body_html_template: HTML email template with variables like {variable_name}
        body_text_template: Plain text email template with variables like {variable_name}
        template_vars: Dictionary mapping email addresses to their template variables
        from_email: Sender email address (uses default if not provided)
        from_name: Sender name (uses default if not provided)
        cc: Carbon copy recipients as string or list
        bcc: Blind carbon copy recipients as string or list
        reply_to: Reply-to email address
        attachments: Dictionary mapping email addresses to their attachments
        max_retries: Maximum number of retries if sending fails
        retry_delay: Delay in seconds between retries
        priority: Email priority (normal, high, low)
        track_opens: Add tracking pixel for open tracking
        track_clicks: Enable click tracking for links
        add_dkim_signature: Whether to add DKIM signature (requires dkim package)
        batch_size: Number of emails to send in each batch
        pause_between_batches: Seconds to pause between batches
        verify_emails: Whether to verify email addresses before sending
        
    Returns:
        Dictionary mapping email addresses to their sending results
    """
    logger.info(f"Starting bulk email send to {len(recipients)} recipients")
    results = {}
    tracking_ids = {}
    
    # Verify email addresses if requested
    if verify_emails:
        verification_results = verify_bulk_email_addresses(recipients)
        invalid_emails = [email for email, result in verification_results.items() if not result['valid']]
        
        # Log and remove invalid emails
        if invalid_emails:
            logger.warning(f"Skipping {len(invalid_emails)} invalid email addresses: {invalid_emails}")
            recipients = [r for r in recipients if r not in invalid_emails]
            
            # Add invalid emails to results
            for email in invalid_emails:
                results[email] = {
                    'success': False, 
                    'error': f"Invalid email: {verification_results[email]['error']}",
                    'email_id': None
                }
    
    # Process emails in batches
    batches = [recipients[i:i+batch_size] for i in range(0, len(recipients), batch_size)]
    
    for batch_index, batch in enumerate(batches):
        logger.info(f"Processing email batch {batch_index+1}/{len(batches)} ({len(batch)} recipients)")
        
        for recipient in batch:
            try:
                # Get template variables for this recipient
                recipient_vars = {}
                if template_vars and recipient in template_vars:
                    recipient_vars = template_vars[recipient]
                
                # Format subject and body for this recipient
                personalized_subject = subject
                personalized_html = body_html_template
                personalized_text = body_text_template
                
                try:
                    # Format with recipient-specific variables
                    if recipient_vars:
                        personalized_subject = subject.format(**recipient_vars)
                        personalized_html = body_html_template.format(**recipient_vars)
                        personalized_text = body_text_template.format(**recipient_vars)
                except KeyError as e:
                    logger.warning(f"Missing template variable {e} for recipient {recipient}")
                    # Continue with unformatted template rather than failing
                
                # Get recipient-specific attachments
                recipient_attachments = None
                if attachments and recipient in attachments:
                    recipient_attachments = attachments[recipient]
                
                # Send the personalized email
                success, error_msg, email_id = send_email(
                    to_email=recipient,
                    subject=personalized_subject,
                    body_html=personalized_html,
                    body_text=personalized_text,
                    from_email=from_email,
                    from_name=from_name,
                    cc=cc,
                    bcc=bcc,
                    reply_to=reply_to,
                    attachments=recipient_attachments,
                    max_retries=max_retries,
                    retry_delay=retry_delay,
                    priority=priority,
                    track_opens=track_opens,
                    track_clicks=track_clicks,
                    add_dkim_signature=add_dkim_signature,
                    metadata={"bulk_email_batch": batch_index + 1}
                )
                
                # Store result
                results[recipient] = {
                    'success': success,
                    'error': error_msg,
                    'email_id': email_id
                }
                
                if email_id:
                    tracking_ids[recipient] = email_id
            
            except Exception as e:
                error_msg = f"Exception sending email to {recipient}: {str(e)}"
                logger.error(error_msg)
                results[recipient] = {
                    'success': False,
                    'error': error_msg,
                    'email_id': None
                }
        
        # Pause between batches to avoid rate limiting, but not after the last batch
        if batch_index < len(batches) - 1 and pause_between_batches > 0:
            logger.debug(f"Pausing for {pause_between_batches}s before next batch")
            time.sleep(pause_between_batches)
    
    # Summarize results
    success_count = sum(1 for r in results.values() if r['success'])
    logger.info(f"Bulk email send completed: {success_count}/{len(recipients)} succeeded")
    
    return results


def send_bulk_emails(
    recipients: List[str],
    subject: str,
    body_html_template: str,
    body_text_template: str,
    template_vars: Optional[Dict[str, Dict[str, Any]]] = None,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None,
    cc: Optional[Union[str, List[str]]] = None,
    bcc: Optional[Union[str, List[str]]] = None,
    reply_to: Optional[str] = None,
    attachments: Optional[Dict[str, List[tuple]]] = None,
    max_retries: int = 3,
    retry_delay: int = 1,
    priority: str = "normal",
    track_opens: bool = False,
    track_clicks: bool = False,
    add_dkim_signature: bool = False,
    batch_size: int = 20,
    pause_between_batches: int = 2,
    verify_emails: bool = True
) -> Dict[str, Dict[str, Any]]:
    """
    Send bulk emails to multiple recipients with personalization, batching, and tracking
    
    Args:
        recipients: List of recipient email addresses
        subject: Email subject (can include template vars like {name})
        body_html_template: HTML email template with variables like {variable_name}
        body_text_template: Plain text email template with variables like {variable_name}
        template_vars: Dictionary mapping email addresses to their template variables
        from_email: Sender email address (uses default if not provided)
        from_name: Sender name (uses default if not provided)
        cc: Carbon copy recipients as string or list
        bcc: Blind carbon copy recipients as string or list
        reply_to: Reply-to email address
        attachments: Dictionary mapping email addresses to their attachments
        max_retries: Maximum number of retries if sending fails
        retry_delay: Delay in seconds between retries
        priority: Email priority (normal, high, low)
        track_opens: Add tracking pixel for open tracking
        track_clicks: Enable click tracking for links
        add_dkim_signature: Whether to add DKIM signature (requires dkim package)
        batch_size: Number of emails to send in each batch
        pause_between_batches: Seconds to pause between batches
        verify_emails: Whether to verify email addresses before sending
        
    Returns:
        Dictionary mapping email addresses to their sending results
    """
    logger.info(f"Starting bulk email send to {len(recipients)} recipients")
    results = {}
    tracking_ids = {}
    
    # Verify email addresses if requested
    if verify_emails:
        verification_results = verify_bulk_email_addresses(recipients)
        invalid_emails = [email for email, result in verification_results.items() if not result['valid']]
        
        # Log and remove invalid emails
        if invalid_emails:
            logger.warning(f"Skipping {len(invalid_emails)} invalid email addresses: {invalid_emails}")
            recipients = [r for r in recipients if r not in invalid_emails]
            
            # Add invalid emails to results
            for email in invalid_emails:
                results[email] = {
                    'success': False, 
                    'error': f"Invalid email: {verification_results[email]['error']}",
                    'email_id': None
                }
    
    # Process emails in batches
    batches = [recipients[i:i+batch_size] for i in range(0, len(recipients), batch_size)]
    
    for batch_index, batch in enumerate(batches):
        logger.info(f"Processing email batch {batch_index+1}/{len(batches)} ({len(batch)} recipients)")
        
        for recipient in batch:
            try:
                # Get template variables for this recipient
                recipient_vars = {}
                if template_vars and recipient in template_vars:
                    recipient_vars = template_vars[recipient]
                
                # Format subject and body for this recipient
                personalized_subject = subject
                personalized_html = body_html_template
                personalized_text = body_text_template
                
                try:
                    # Format with recipient-specific variables
                    if recipient_vars:
                        personalized_subject = subject.format(**recipient_vars)
                        personalized_html = body_html_template.format(**recipient_vars)
                        personalized_text = body_text_template.format(**recipient_vars)
                except KeyError as e:
                    logger.warning(f"Missing template variable {e} for recipient {recipient}")
                    # Continue with unformatted template rather than failing
                
                # Get recipient-specific attachments
                recipient_attachments = None
                if attachments and recipient in attachments:
                    recipient_attachments = attachments[recipient]
                
                # Send the personalized email
                success, error_msg, email_id = send_email(
                    to_email=recipient,
                    subject=personalized_subject,
                    body_html=personalized_html,
                    body_text=personalized_text,
                    from_email=from_email,
                    from_name=from_name,
                    cc=cc,
                    bcc=bcc,
                    reply_to=reply_to,
                    attachments=recipient_attachments,
                    max_retries=max_retries,
                    retry_delay=retry_delay,
                    priority=priority,
                    track_opens=track_opens,
                    track_clicks=track_clicks,
                    add_dkim_signature=add_dkim_signature,
                    metadata={"bulk_email_batch": batch_index + 1}
                )
                
                # Store result
                results[recipient] = {
                    'success': success,
                    'error': error_msg,
                    'email_id': email_id
                }
                
                if email_id:
                    tracking_ids[recipient] = email_id
                    
            except Exception as e:
                error_msg = f"Exception sending email to {recipient}: {str(e)}"
                logger.error(error_msg)
                results[recipient] = {
                    'success': False,
                    'error': error_msg,
                    'email_id': None
                }
        
        # Pause between batches to avoid rate limiting, but not after the last batch
        if batch_index < len(batches) - 1 and pause_between_batches > 0:
            logger.debug(f"Pausing for {pause_between_batches}s before next batch")
            time.sleep(pause_between_batches)
    
    # Summarize results
    success_count = sum(1 for r in results.values() if r['success'])
    logger.info(f"Bulk email send completed: {success_count}/{len(recipients)} succeeded")
    
    return results

# Start the email queue worker when the module is imported
start_email_queue_worker()
