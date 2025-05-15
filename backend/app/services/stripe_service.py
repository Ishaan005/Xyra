import stripe
from typing import Optional

from app.core import config

stripe.api_key = config.settings.STRIPE_API_KEY


def create_checkout_session(
    amount: float,
    currency: str,
    invoice_number: str,
    description: str,
    success_url: str,
    cancel_url: str,
) -> Optional[dict]:
    """
    Create a Stripe Checkout Session for an invoice.
    Returns a dict with session_id and payment_link (url), or None on failure.
    """
    try:
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
        )
        return {
            "session_id": session.id,
            "payment_link": session.url
        }
    except Exception as e:
        # Optionally log the error
        return None
