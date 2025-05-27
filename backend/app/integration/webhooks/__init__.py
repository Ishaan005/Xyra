"""
Webhook receiver system for real-time data collection.
"""
from fastapi import APIRouter, Request, HTTPException, status, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta
from app.api import deps
from app.core.config import settings
import asyncio
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)

router = APIRouter()

class WebhookRegistry:
    """Registry for managing webhook endpoints and configurations"""
    
    def __init__(self):
        self.registered_webhooks: Dict[str, Dict[str, Any]] = {}
        self.delivery_attempts: Dict[str, List[Dict]] = {}
    
    def register_webhook(
        self,
        endpoint_id: str,
        url: str,
        secret: str,
        events: List[str],
        retry_config: Optional[Dict] = None
    ):
        """Register a new webhook endpoint"""
        self.registered_webhooks[endpoint_id] = {
            "url": url,
            "secret": secret,
            "events": events,
            "retry_config": retry_config or {
                "max_attempts": 3,
                "retry_delays": [60, 300, 900]  # 1min, 5min, 15min
            },
            "created_at": datetime.utcnow(),
            "active": True
        }
        logger.info(f"Registered webhook endpoint: {endpoint_id}")
    
    def get_webhook(self, endpoint_id: str) -> Optional[Dict[str, Any]]:
        """Get webhook configuration"""
        return self.registered_webhooks.get(endpoint_id)
    
    def deactivate_webhook(self, endpoint_id: str):
        """Deactivate a webhook endpoint"""
        if endpoint_id in self.registered_webhooks:
            self.registered_webhooks[endpoint_id]["active"] = False
            logger.info(f"Deactivated webhook endpoint: {endpoint_id}")

# Global webhook registry
webhook_registry = WebhookRegistry()

class WebhookValidator:
    """Handles webhook payload validation and verification"""
    
    @staticmethod
    def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
        """Verify webhook signature"""
        try:
            # Support different signature formats
            if signature.startswith("sha256="):
                signature = signature[7:]
                expected = hmac.new(
                    secret.encode("utf-8"),
                    payload,
                    hashlib.sha256
                ).hexdigest()
            elif signature.startswith("sha1="):
                signature = signature[6:]
                expected = hmac.new(
                    secret.encode("utf-8"),
                    payload,
                    hashlib.sha1
                ).hexdigest()
            else:
                expected = hmac.new(
                    secret.encode("utf-8"),
                    payload,
                    hashlib.sha256
                ).hexdigest()
            
            return hmac.compare_digest(signature, expected)
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    @staticmethod
    def validate_payload(payload: Dict[str, Any], required_fields: List[str]) -> bool:
        """Validate that payload contains required fields"""
        try:
            for field in required_fields:
                if field not in payload:
                    return False
            return True
        except Exception:
            return False

class WebhookProcessor:
    """Processes webhook payloads and handles retries"""
    
    def __init__(self):
        self.processing_queue = asyncio.Queue()
        self.retry_queue = asyncio.Queue()
    
    async def process_webhook(
        self,
        endpoint_id: str,
        payload: Dict[str, Any],
        headers: Dict[str, str]
    ):
        """Process a webhook payload"""
        try:
            # Add to processing queue
            await self.processing_queue.put({
                "endpoint_id": endpoint_id,
                "payload": payload,
                "headers": headers,
                "timestamp": datetime.utcnow(),
                "attempt": 1
            })
            
            logger.info(f"Queued webhook for processing: {endpoint_id}")
            
        except Exception as e:
            logger.error(f"Failed to queue webhook {endpoint_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process webhook"
            )
    
    async def handle_failed_delivery(
        self,
        endpoint_id: str,
        payload: Dict[str, Any],
        attempt: int,
        error: str
    ):
        """Handle failed webhook delivery with retry logic"""
        webhook_config = webhook_registry.get_webhook(endpoint_id)
        if not webhook_config:
            return
        
        retry_config = webhook_config["retry_config"]
        max_attempts = retry_config["max_attempts"]
        
        if attempt < max_attempts:
            # Schedule retry
            retry_delay = retry_config["retry_delays"][attempt - 1]
            await asyncio.sleep(retry_delay)
            
            await self.retry_queue.put({
                "endpoint_id": endpoint_id,
                "payload": payload,
                "attempt": attempt + 1,
                "retry_at": datetime.utcnow() + timedelta(seconds=retry_delay)
            })
            
            logger.info(f"Scheduled retry {attempt + 1} for webhook {endpoint_id}")
        else:
            logger.error(
                f"Max retry attempts reached for webhook {endpoint_id}. "
                f"Final error: {error}"
            )

# Global webhook processor
webhook_processor = WebhookProcessor()

@router.post("/webhooks/register")
async def register_webhook_endpoint(
    webhook_data: Dict[str, Any],
    db: Session = Depends(deps.get_db)
):
    """Register a new webhook endpoint"""
    required_fields = ["endpoint_id", "url", "secret", "events"]
    
    if not WebhookValidator.validate_payload(webhook_data, required_fields):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required fields"
        )
    
    webhook_registry.register_webhook(
        endpoint_id=webhook_data["endpoint_id"],
        url=webhook_data["url"],
        secret=webhook_data["secret"],
        events=webhook_data["events"],
        retry_config=webhook_data.get("retry_config")
    )
    
    return {"status": "success", "message": "Webhook endpoint registered"}

@router.post("/webhooks/{endpoint_id}")
async def receive_webhook(
    endpoint_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db)
):
    """Receive and process webhook payload"""
    # Get webhook configuration
    webhook_config = webhook_registry.get_webhook(endpoint_id)
    if not webhook_config or not webhook_config["active"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook endpoint not found or inactive"
        )
    
    # Get payload and headers
    payload_bytes = await request.body()
    headers = dict(request.headers)
    
    # Verify signature if provided
    signature = headers.get("x-signature") or headers.get("x-hub-signature-256")
    if signature:
        if not WebhookValidator.verify_signature(
            payload_bytes, signature, webhook_config["secret"]
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature"
            )
    
    # Parse payload
    try:
        payload = json.loads(payload_bytes.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    
    # Process webhook in background
    background_tasks.add_task(
        webhook_processor.process_webhook,
        endpoint_id,
        payload,
        headers
    )
    
    return {"status": "received"}

@router.get("/webhooks/{endpoint_id}/status")
async def get_webhook_status(
    endpoint_id: str,
    db: Session = Depends(deps.get_db)
):
    """Get webhook endpoint status and metrics"""
    webhook_config = webhook_registry.get_webhook(endpoint_id)
    if not webhook_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook endpoint not found"
        )
    
    delivery_attempts = webhook_registry.delivery_attempts.get(endpoint_id, [])
    
    return {
        "endpoint_id": endpoint_id,
        "active": webhook_config["active"],
        "events": webhook_config["events"],
        "created_at": webhook_config["created_at"],
        "delivery_stats": {
            "total_attempts": len(delivery_attempts),
            "successful": len([a for a in delivery_attempts if a["success"]]),
            "failed": len([a for a in delivery_attempts if not a["success"]])
        }
    }

@router.delete("/webhooks/{endpoint_id}")
async def deactivate_webhook(
    endpoint_id: str,
    db: Session = Depends(deps.get_db)
):
    """Deactivate a webhook endpoint"""
    webhook_registry.deactivate_webhook(endpoint_id)
    return {"status": "success", "message": "Webhook endpoint deactivated"}

@router.post("/webhooks/test/{endpoint_id}")
async def test_webhook_endpoint(
    endpoint_id: str,
    test_payload: Dict[str, Any],
    db: Session = Depends(deps.get_db)
):
    """Test a webhook endpoint with sample payload"""
    webhook_config = webhook_registry.get_webhook(endpoint_id)
    if not webhook_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook endpoint not found"
        )
    
    # Process test webhook
    await webhook_processor.process_webhook(
        endpoint_id,
        test_payload,
        {"x-test": "true"}
    )
    
    return {"status": "success", "message": "Test webhook sent"}
