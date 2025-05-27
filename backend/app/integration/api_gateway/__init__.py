"""
Enhanced API Gateway with rate limiting, authentication, and monitoring.
"""
from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import time
import logging
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import asyncio
from datetime import datetime, timedelta, UTC

logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

async def rate_limit_handler(request: Request, exc: Exception) -> JSONResponse:
    """Custom rate limit exception handler for FastAPI"""
    if isinstance(exc, RateLimitExceeded):
        response = JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "detail": f"Rate limit exceeded: {exc.detail}",
                "type": "rate_limit_exceeded"
            }
        )
        return response
    
    # Fallback for other exceptions
    response = JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )
    return response

class APIGatewayMiddleware:
    """Custom middleware for API gateway functionality"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.request_metrics: Dict[str, Any] = {}
        
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    # Log request metrics
                    process_time = time.time() - start_time
                    self._log_request_metrics(scope, process_time, message["status"])
                await send(message)
                
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)
    
    def _log_request_metrics(self, scope, process_time: float, status_code: int):
        """Log request metrics for monitoring"""
        path = scope["path"]
        method = scope["method"]
        
        logger.info(
            f"API Request - Method: {method}, Path: {path}, "
            f"Status: {status_code}, Duration: {process_time:.4f}s"
        )
        
        # Store metrics for monitoring
        if path not in self.request_metrics:
            self.request_metrics[path] = {
                "count": 0,
                "total_time": 0,
                "avg_time": 0,
                "status_codes": {}
            }
        
        metrics = self.request_metrics[path]
        metrics["count"] += 1
        metrics["total_time"] += process_time
        metrics["avg_time"] = metrics["total_time"] / metrics["count"]
        
        if status_code not in metrics["status_codes"]:
            metrics["status_codes"][status_code] = 0
        metrics["status_codes"][status_code] += 1

class CircuitBreaker:
    """Circuit breaker for external service calls"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Service temporarily unavailable"
                )
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.timeout
    
    def _on_success(self):
        """Reset circuit breaker on successful call"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Handle failure in circuit breaker"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

def setup_api_gateway(app: FastAPI) -> FastAPI:
    """Setup enhanced API gateway features"""
    
    # Add rate limiting middleware
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
    app.add_middleware(SlowAPIMiddleware)
    
    # Add custom gateway middleware
    gateway_middleware = APIGatewayMiddleware(app)
    
    # Add health check endpoint
    @app.get("/health")
    @limiter.limit("10/minute")
    async def health_check(request: Request):
        """Health check endpoint for monitoring"""
        return {
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "1.0.0"
        }
    
    # Add metrics endpoint
    @app.get("/metrics")
    @limiter.limit("5/minute")
    async def get_metrics(request: Request):
        """Get API metrics for monitoring"""
        return {
            "request_metrics": gateway_middleware.request_metrics,
            "timestamp": datetime.now(UTC).isoformat()
        }
    
    return app

# Global circuit breaker instance
circuit_breaker = CircuitBreaker()
