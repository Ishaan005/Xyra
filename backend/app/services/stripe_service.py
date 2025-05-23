import stripe
from typing import Optional, Dict, Any, List
import logging
import datetime

from app.core import config

# Configure logging
logger = logging.getLogger(__name__)

# Configure Stripe API
stripe.api_key = config.settings.STRIPE_API_KEY


def create_checkout_session(
    amount: float,
    currency: str,
    invoice_number: str,
    description: str,
    success_url: str,
    cancel_url: str,
    customer_email: str = None,
    expires_in_days: int = 30,
    metadata: dict = None
) -> Optional[dict]:
    """
    Create a Stripe Checkout Session for an invoice.
    
    Args:
        amount: The invoice amount
        currency: The currency code (e.g., 'USD')
        invoice_number: The invoice number
        description: A description of the invoice
        success_url: URL to redirect to after successful payment
        cancel_url: URL to redirect to if payment is cancelled
        customer_email: (Optional) Pre-fill customer email in checkout
        expires_in_days: Number of days until the payment link expires
        metadata: Additional metadata to store with the session
        
    Returns:
        A dict with session_id, payment_link, expiration_date, and status or None on failure.
    """
    try:
        import datetime
        
        # Calculate expiration date
        expires_at = int((datetime.datetime.now() + datetime.timedelta(days=expires_in_days)).timestamp())
        
        # Build metadata dictionary
        session_metadata = {
            "invoice_number": invoice_number,
        }
        
        # Add any additional metadata
        if metadata:
            session_metadata.update(metadata)
            
        # Create checkout session
        session = stripe.checkout.Session.create(
            line_items=[{
                "price_data": {
                    "currency": currency,
                    "product_data": {
                        "name": f"Invoice {invoice_number}",
                        "description": description,
                    },
                    "unit_amount": int(amount * 100),  # Stripe expects cents
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=customer_email,
            expires_at=expires_at,
            metadata=session_metadata,
            payment_intent_data={
                "metadata": session_metadata
            }
        )
        
        # Format expiration date for response
        expiration_date = datetime.datetime.fromtimestamp(expires_at)
        
        return {
            "session_id": session.id,
            "payment_link": session.url,
            "expiration_date": expiration_date.isoformat(),
            "status": session.status
        }
    except Exception as e:
        # Log the error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating Stripe checkout session: {str(e)}")
        return None


def get_checkout_session(session_id: str) -> Optional[Dict]:
    """
    Retrieve a Stripe Checkout Session by ID
    
    Args:
        session_id: The Stripe Checkout Session ID
        
    Returns:
        The session information or None on failure
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return {
            "id": session.id,
            "status": session.status,
            "payment_status": session.payment_status,
            "amount_total": session.amount_total / 100,  # Convert from cents
            "currency": session.currency,
            "customer_email": session.customer_details.email if session.get("customer_details") else None,
            "payment_intent": session.payment_intent,
            "expires_at": datetime.datetime.fromtimestamp(session.expires_at).isoformat() if session.get("expires_at") else None,
            "url": session.url
        }
    except Exception as e:
        logger.error(f"Error retrieving Stripe checkout session: {str(e)}")
        return None


def refresh_checkout_session(session_id: str, new_expiration_days: int = 30) -> Optional[Dict]:
    """
    Refresh an expired Stripe Checkout Session with a new expiration date
    
    Args:
        session_id: The expired session ID
        new_expiration_days: Number of days from now until the new session expires
        
    Returns:
        The new session information or None on failure
    """
    try:
        # First get the old session to copy its data
        old_session = stripe.checkout.Session.retrieve(session_id)
        
        if old_session.status != "expired":
            logger.warning(f"Attempted to refresh non-expired session: {session_id}")
            return {"error": "Session is not expired"}
        
        # Calculate new expiration date
        expires_at = int((datetime.datetime.now() + datetime.timedelta(days=new_expiration_days)).timestamp())
        
        # Create a new session with the same parameters
        new_session = stripe.checkout.Session.create(
            line_items=[{
                "price_data": {
                    "currency": old_session.currency,
                    "product_data": {
                        "name": old_session.metadata.get("invoice_number", "Invoice"),
                        "description": old_session.metadata.get("description", ""),
                    },
                    "unit_amount": old_session.amount_total,  # Already in cents
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=old_session.success_url,
            cancel_url=old_session.cancel_url,
            customer_email=old_session.customer_email,
            expires_at=expires_at,
            metadata=old_session.metadata,
            payment_intent_data={
                "metadata": old_session.metadata
            }
        )
        
        return {
            "session_id": new_session.id,
            "payment_link": new_session.url,
            "expiration_date": datetime.datetime.fromtimestamp(expires_at).isoformat(),
            "status": new_session.status,
            "previous_session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Error refreshing Stripe checkout session: {str(e)}")
        return None


def get_payment_intent(payment_intent_id: str) -> Optional[Dict]:
    """
    Retrieve a Stripe Payment Intent by ID
    
    Args:
        payment_intent_id: The Stripe Payment Intent ID
        
    Returns:
        The payment intent information or None on failure
    """
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return {
            "id": payment_intent.id,
            "amount": payment_intent.amount / 100,  # Convert from cents
            "currency": payment_intent.currency,
            "status": payment_intent.status,
            "payment_method_types": payment_intent.payment_method_types,
            "created": datetime.datetime.fromtimestamp(payment_intent.created).isoformat(),
            "metadata": payment_intent.metadata
        }
    except Exception as e:
        logger.error(f"Error retrieving Stripe payment intent: {str(e)}")
        return None


def get_payment_method_details(payment_method_id: str) -> Optional[Dict]:
    """
    Retrieve details about a payment method for receipts and notifications
    
    Args:
        payment_method_id: The Stripe Payment Method ID
        
    Returns:
        Payment method details or None on failure
    """
    try:
        payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
        
        # Build a normalized response that's easier to use
        result = {
            "id": payment_method.id,
            "type": payment_method.type,
            "created": datetime.datetime.fromtimestamp(payment_method.created).isoformat()
        }
        
        # Add type-specific details
        if payment_method.type == "card":
            result["card"] = {
                "brand": payment_method.card.brand,
                "last4": payment_method.card.last4,
                "exp_month": payment_method.card.exp_month,
                "exp_year": payment_method.card.exp_year,
                "funding": payment_method.card.funding,
                "country": payment_method.card.country
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving Stripe payment method: {str(e)}")
        return None


def create_refund(payment_intent_id: str, amount: Optional[float] = None, reason: str = "requested_by_customer") -> Optional[Dict]:
    """
    Create a refund for a payment
    
    Args:
        payment_intent_id: The Stripe Payment Intent ID to refund
        amount: Optional amount to refund (in dollars, not cents). If None, refunds the full amount.
        reason: Reason for the refund (default: requested_by_customer)
        
    Returns:
        Refund details or None on failure
    """
    try:
        refund_params = {
            "payment_intent": payment_intent_id,
            "reason": reason
        }
        
        # If amount provided, convert to cents and add to params
        if amount is not None:
            refund_params["amount"] = int(amount * 100)
            
        refund = stripe.Refund.create(**refund_params)
        
        return {
            "id": refund.id,
            "amount": refund.amount / 100,  # Convert to dollars
            "currency": refund.currency,
            "status": refund.status,
            "created": datetime.datetime.fromtimestamp(refund.created).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating Stripe refund: {str(e)}")
        return None
