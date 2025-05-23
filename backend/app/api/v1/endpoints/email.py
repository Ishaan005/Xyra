from fastapi import APIRouter, Request, Depends, Response, Query
from typing import Optional, Dict, Any
from app.services import email_service
from app.api import deps
from starlette.responses import RedirectResponse

router = APIRouter()


@router.get("/track-open/{email_id}")
async def track_email_open(
    email_id: str,
    request: Request
):
    """
    Track when an email is opened using a tracking pixel.
    
    This endpoint returns a 1x1 transparent pixel and records the email open.
    """
    # Get client IP address for tracking
    client_host = request.client.host if request.client else None
    
    # Record the open event
    email_service.track_email_open(email_id, ip_address=client_host)
    
    # Return a 1x1 transparent pixel
    pixel = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
    
    return Response(content=pixel, media_type="image/gif")


@router.get("/track-click/{email_id}")
async def track_email_click(
    email_id: str,
    request: Request,
    url: str = Query(...)
):
    """
    Track when a link in an email is clicked.
    
    This endpoint records the click event and redirects to the original URL.
    """
    # Get client IP address for tracking
    client_host = request.client.host if request.client else None
    
    # Record the click event
    email_service.track_email_click(email_id, url=url, ip_address=client_host)
    
    # Redirect to the target URL
    return RedirectResponse(url=url)


@router.get("/status/{email_id}")
async def get_email_status(
    email_id: str,
    current_user = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """
    Get the current status of a sent email.
    
    Returns detailed information about the email delivery status, opens, clicks, etc.
    """
    status = email_service.get_email_status(email_id)
    
    if not status:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Email not found")
        
    return status
