from fastapi import APIRouter, Request, HTTPException, status, Depends
from app.services import invoice_service
from app.core import config
import stripe
from app.api import deps

router = APIRouter()

stripe.api_key = config.settings.STRIPE_API_KEY
endpoint_secret = config.settings.STRIPE_WEBHOOK_SECRET

@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, db=Depends(deps.get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        session_id = session["id"]
        # Find invoice by stripe_checkout_session_id and mark as paid
        invoice = invoice_service.get_invoice_by_stripe_session_id(db, session_id)
        if invoice and invoice.status != "paid":
            invoice_service.mark_invoice_as_paid(db, invoice_id=invoice.id, payment_method="stripe", payment_date=None)
    elif event["type"] == "invoice.paid":
        # Optionally handle other Stripe events
        pass
    # ... handle other event types as needed

    return {"status": "success"}
