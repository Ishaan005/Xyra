from fastapi import APIRouter, Request, HTTPException, status, Depends, BackgroundTasks
from app.services import invoice_service, organization_service
from app.core import config
import stripe
import logging
from datetime import datetime
from app.api import deps

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

stripe.api_key = config.settings.STRIPE_API_KEY
endpoint_secret = config.settings.STRIPE_WEBHOOK_SECRET

# Background task for sending payment confirmation
def send_payment_confirmation(invoice_id, org_id, payment_method, payment_amount):
    """Send a payment confirmation email (background task)"""
    try:
        from app.services import email_service
        from app.services.organization_service import get_organization
        
        # Get the invoice and organization details
        db = deps.get_db_instance()
        invoice = invoice_service.get_invoice(db, invoice_id)
        organization = organization_service.get_organization(db, org_id)
        
        if not invoice or not organization:
            logger.error(f"Failed to send payment confirmation: invoice or organization not found")
            return
            
        # Get organization admin emails
        admin_emails = organization_service.get_organization_admin_emails(db, org_id)
        if not admin_emails:
            logger.warning(f"No admin emails found for organization {org_id}")
            return
            
        # Prepare email content
        subject = f"Payment Confirmation - Invoice {invoice.invoice_number}"
        
        # HTML content with payment details
        html_content = f"""
        <h2>Payment Confirmation</h2>
        <p>Your payment for invoice {invoice.invoice_number} has been successfully processed.</p>
        <p><strong>Details:</strong></p>
        <ul>
            <li>Invoice Number: {invoice.invoice_number}</li>
            <li>Amount: {invoice.currency} {invoice.total_amount:.2f}</li>
            <li>Payment Method: {payment_method}</li>
            <li>Payment Date: {invoice.payment_date.strftime('%Y-%m-%d %H:%M:%S UTC')}</li>
        </ul>
        <p>Thank you for your business!</p>
        """
        
        # Plain text version
        text_content = f"""
        Payment Confirmation
        
        Your payment for invoice {invoice.invoice_number} has been successfully processed.
        
        Details:
        - Invoice Number: {invoice.invoice_number}
        - Amount: {invoice.currency} {invoice.total_amount:.2f}
        - Payment Method: {payment_method}
        - Payment Date: {invoice.payment_date.strftime('%Y-%m-%d %H:%M:%S UTC')}
        
        Thank you for your business!
        """
        
        # Send the email to all organization admins
        for email in admin_emails:
            email_service.send_email(
                to_email=email,
                subject=subject,
                body_html=html_content,
                body_text=text_content,
                from_email=None,  # Use default from email
                from_name="Xyra Billing"
            )
            
        logger.info(f"Payment confirmation email sent for invoice {invoice_id} to org {org_id}")
        
    except Exception as e:
        logger.error(f"Error sending payment confirmation email: {e}")
        # Don't raise an exception here - just log the error


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, background_tasks: BackgroundTasks, db=Depends(deps.get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    event = None
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    # Log the event type for debugging
    logger.info(f"Received Stripe event: {event['type']}")
    
    try:
        # Handle the event
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            session_id = session["id"]
            payment_status = session.get("payment_status")
            
            # Find invoice by stripe_checkout_session_id
            invoice = invoice_service.get_invoice_by_stripe_session_id(db, session_id)
            
            if not invoice:
                logger.error(f"No invoice found for session ID {session_id}")
                return {"status": "error", "message": "Invoice not found"}
                
            if invoice.status == "paid":
                logger.info(f"Invoice {invoice.id} already marked as paid")
                return {"status": "success", "message": "Invoice already paid"}
            
            # Only mark as paid if payment status is actually paid
            if payment_status == "paid":
                # Update invoice with payment details
                payment_date = datetime.now()
                payment_details = {
                    "payment_method": "stripe",
                    "stripe_invoice_id": session.get("invoice"),
                    # Store any additional metadata we want to keep
                    "invoice_metadata": {
                        "stripe_payment_intent": session.get("payment_intent"),
                        "stripe_customer": session.get("customer"),
                        "payment_status": payment_status,
                    }
                }
                
                invoice = invoice_service.mark_invoice_as_paid(
                    db, 
                    invoice_id=invoice.id, 
                    payment_method="stripe", 
                    payment_date=payment_date,
                    payment_details=payment_details
                )
                
                # Schedule confirmation email
                background_tasks.add_task(
                    send_payment_confirmation, 
                    invoice.id, 
                    invoice.organization_id,
                    "stripe", 
                    invoice.total_amount
                )
                
                logger.info(f"Invoice {invoice.id} marked as paid via Stripe")
                
        elif event["type"] == "checkout.session.expired":
            session = event["data"]["object"]
            session_id = session["id"]
            
            # Handle expired checkout sessions
            invoice = invoice_service.get_invoice_by_stripe_session_id(db, session_id)
            if invoice and invoice.status == "pending":
                # Optionally regenerate the payment link here
                logger.info(f"Checkout session expired for invoice {invoice.id}")
                
        # Add more event types as needed
            
    except Exception as e:
        logger.error(f"Error processing Stripe event: {e}")
        # Don't raise an exception here - Stripe expects a 200 response
        # even if we have internal errors processing the webhook
        return {"status": "error", "message": str(e)}

    return {"status": "success"}
