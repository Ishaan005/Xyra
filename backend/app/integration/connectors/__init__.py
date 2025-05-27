"""
Custom connectors for specialized system integrations.
"""
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import asyncio
import aiohttp
import logging
from datetime import datetime
from app.api import deps
from abc import ABC, abstractmethod
from dataclasses import dataclass
import ssl
import certifi
from urllib.parse import urljoin
import base64

import time
from enum import Enum

logger = logging.getLogger(__name__)

router = APIRouter()

class ConnectorType(str, Enum):
    REST_API = "rest_api"
    GRAPHQL = "graphql"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    CUSTOM = "custom"

class AuthType(str, Enum):
    NONE = "none"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    OAUTH2 = "oauth2"
    CUSTOM = "custom"

class ConnectorStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TESTING = "testing"

@dataclass
class ConnectionHealth:
    is_healthy: bool
    last_check: datetime
    response_time: float
    error_message: Optional[str] = None
    consecutive_failures: int = 0

@dataclass
class ConnectorMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    last_request_time: Optional[datetime] = None
    data_extracted: int = 0

class BaseConnector(ABC):
    """Base class for all connectors"""
    
    def __init__(
        self,
        connector_id: str,
        name: str,
        connector_type: ConnectorType,
        config: Dict[str, Any]
    ):
        self.connector_id = connector_id
        self.name = name
        self.connector_type = connector_type
        self.config = config
        self.status = ConnectorStatus.INACTIVE
        self.health = ConnectionHealth(
            is_healthy=False,
            last_check=datetime.utcnow(),
            response_time=0.0
        )
        self.metrics = ConnectorMetrics()
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def initialize(self):
        """Initialize the connector"""
        try:
            await self._setup_session()
            self.status = ConnectorStatus.ACTIVE
            logger.info(f"Initialized connector: {self.connector_id}")
        except Exception as e:
            self.status = ConnectorStatus.ERROR
            logger.error(f"Failed to initialize connector {self.connector_id}: {e}")
            raise
    
    async def _setup_session(self):
        """Setup HTTP session with appropriate configuration"""
        timeout = aiohttp.ClientTimeout(
            total=self.config.get("timeout", 30),
            connect=self.config.get("connect_timeout", 10)
        )
        
        # SSL configuration
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        if not self.config.get("verify_ssl", True):
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        
        # Create session with authentication headers
        headers = await self._get_auth_headers()
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers=headers,
            connector=aiohttp.TCPConnector(ssl=ssl_context)
        )
    
    async def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers based on auth type"""
        headers = {}
        auth_config = self.config.get("auth", {})
        auth_type = AuthType(auth_config.get("type", AuthType.NONE))
        
        if auth_type == AuthType.API_KEY:
            key = auth_config.get("key")
            value = auth_config.get("value")
            if key and value:
                headers[key] = value
        
        elif auth_type == AuthType.BEARER_TOKEN:
            token = auth_config.get("token")
            if token:
                headers["Authorization"] = f"Bearer {token}"
        
        elif auth_type == AuthType.BASIC_AUTH:
            username = auth_config.get("username")
            password = auth_config.get("password")
            if username and password:
                credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                headers["Authorization"] = f"Basic {credentials}"
        
        # Add custom headers
        custom_headers = self.config.get("headers", {})
        headers.update(custom_headers)
        
        return headers
    
    async def test_connection(self) -> ConnectionHealth:
        """Test the connector connection"""
        start_time = time.time()
        
        try:
            if self.session is None:
                await self._setup_session()
            
            # Perform connection test
            is_healthy = await self._perform_health_check()
            response_time = time.time() - start_time
            
            self.health = ConnectionHealth(
                is_healthy=is_healthy,
                last_check=datetime.utcnow(),
                response_time=response_time,
                consecutive_failures=0 if is_healthy else self.health.consecutive_failures + 1
            )
            
            if is_healthy:
                self.status = ConnectorStatus.ACTIVE
            else:
                self.status = ConnectorStatus.ERROR
            
        except Exception as e:
            response_time = time.time() - start_time
            self.health = ConnectionHealth(
                is_healthy=False,
                last_check=datetime.utcnow(),
                response_time=response_time,
                error_message=str(e),
                consecutive_failures=self.health.consecutive_failures + 1
            )
            self.status = ConnectorStatus.ERROR
            logger.error(f"Connection test failed for {self.connector_id}: {e}")
        
        return self.health
    
    @abstractmethod
    async def _perform_health_check(self) -> bool:
        """Perform connector-specific health check"""
        pass
    
    @abstractmethod
    async def extract_data(
        self,
        extraction_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract data from the external system"""
        pass
    
    async def cleanup(self):
        """Cleanup connector resources"""
        if self.session:
            await self.session.close()
        self.status = ConnectorStatus.INACTIVE

class RestApiConnector(BaseConnector):
    """REST API connector for HTTP-based integrations"""
    
    def __init__(self, connector_id: str, name: str, config: Dict[str, Any]):
        super().__init__(connector_id, name, ConnectorType.REST_API, config)
        self.base_url = config.get("base_url", "")
        
    async def _perform_health_check(self) -> bool:
        """Perform health check via HTTP request"""
        if self.session is None:
            await self._setup_session()
            
        assert self.session is not None, "Session should be initialized"
        
        health_endpoint = self.config.get("health_endpoint", "/health")
        url = urljoin(self.base_url, health_endpoint)
        
        try:
            async with self.session.get(url) as response:
                return response.status < 400
        except Exception:
            return False
    
    async def extract_data(
        self,
        extraction_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract data via REST API calls"""
        if self.session is None:
            await self._setup_session()
            
        assert self.session is not None, "Session should be initialized"
        
        endpoint = extraction_config.get("endpoint", "")
        method = extraction_config.get("method", "GET").upper()
        params = extraction_config.get("params", {})
        payload = extraction_config.get("payload", {})
        
        url = urljoin(self.base_url, endpoint)
        
        start_time = time.time()
        self.metrics.total_requests += 1
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                params=params,
                json=payload if method in ["POST", "PUT", "PATCH"] else None
            ) as response:
                
                response_time = time.time() - start_time
                self.metrics.avg_response_time = (
                    (self.metrics.avg_response_time * (self.metrics.total_requests - 1) + response_time) 
                    / self.metrics.total_requests
                )
                
                if response.status < 400:
                    self.metrics.successful_requests += 1
                    data = await response.json()
                    
                    # Extract data based on configuration
                    extracted_data = self._extract_from_response(data, extraction_config)
                    self.metrics.data_extracted += len(extracted_data)
                    
                    return extracted_data
                else:
                    self.metrics.failed_requests += 1
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"API request failed: {await response.text()}"
                    )
                    
        except Exception as e:
            self.metrics.failed_requests += 1
            logger.error(f"Data extraction failed for {self.connector_id}: {e}")
            raise
        finally:
            self.metrics.last_request_time = datetime.utcnow()
    
    def _extract_from_response(
        self,
        response_data: Dict[str, Any],
        extraction_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract specific data from API response"""
        data_path = extraction_config.get("data_path", "")
        field_mapping = extraction_config.get("field_mapping", {})
        
        # Navigate to data using path
        current_data = response_data
        if data_path:
            for key in data_path.split("."):
                if key in current_data:
                    current_data = current_data[key]
                else:
                    return []
        
        # Ensure we have a list
        if not isinstance(current_data, list):
            current_data = [current_data]
        
        # Apply field mapping
        extracted_data = []
        for item in current_data:
            if field_mapping:
                mapped_item = {}
                for source_field, target_field in field_mapping.items():
                    if source_field in item:
                        mapped_item[target_field] = item[source_field]
                extracted_data.append(mapped_item)
            else:
                extracted_data.append(item)
        
        return extracted_data

class GraphQLConnector(BaseConnector):
    """GraphQL connector for GraphQL API integrations"""
    
    def __init__(self, connector_id: str, name: str, config: Dict[str, Any]):
        super().__init__(connector_id, name, ConnectorType.GRAPHQL, config)
        self.endpoint = config.get("endpoint", "")
    
    async def _perform_health_check(self) -> bool:
        """Perform health check with introspection query"""
        if self.session is None:
            await self._setup_session()
            
        assert self.session is not None, "Session should be initialized"
        
        introspection_query = """
        query IntrospectionQuery {
            __schema {
                queryType {
                    name
                }
            }
        }
        """
        
        try:
            payload = {"query": introspection_query}
            async with self.session.post(self.endpoint, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return "errors" not in data
                return False
        except Exception:
            return False
    
    async def extract_data(
        self,
        extraction_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract data via GraphQL query"""
        if self.session is None:
            await self._setup_session()
            
        assert self.session is not None, "Session should be initialized"
        
        query = extraction_config.get("query", "")
        variables = extraction_config.get("variables", {})
        
        if not query:
            raise ValueError("GraphQL query is required")
        
        payload = {
            "query": query,
            "variables": variables
        }
        
        start_time = time.time()
        self.metrics.total_requests += 1
        
        try:
            async with self.session.post(self.endpoint, json=payload) as response:
                response_time = time.time() - start_time
                self.metrics.avg_response_time = (
                    (self.metrics.avg_response_time * (self.metrics.total_requests - 1) + response_time) 
                    / self.metrics.total_requests
                )
                
                if response.status == 200:
                    data = await response.json()
                    
                    if "errors" in data:
                        self.metrics.failed_requests += 1
                        raise ValueError(f"GraphQL errors: {data['errors']}")
                    
                    self.metrics.successful_requests += 1
                    
                    # Extract data from GraphQL response
                    extracted_data = self._extract_from_graphql_response(
                        data.get("data", {}),
                        extraction_config
                    )
                    self.metrics.data_extracted += len(extracted_data)
                    
                    return extracted_data
                else:
                    self.metrics.failed_requests += 1
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"GraphQL request failed: {await response.text()}"
                    )
                    
        except Exception as e:
            self.metrics.failed_requests += 1
            logger.error(f"GraphQL data extraction failed for {self.connector_id}: {e}")
            raise
        finally:
            self.metrics.last_request_time = datetime.utcnow()
    
    def _extract_from_graphql_response(
        self,
        response_data: Dict[str, Any],
        extraction_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract data from GraphQL response"""
        data_path = extraction_config.get("data_path", "")
        
        # Navigate to data using path
        current_data = response_data
        if data_path:
            for key in data_path.split("."):
                if key in current_data:
                    current_data = current_data[key]
                else:
                    return []
        
        # Ensure we have a list
        if not isinstance(current_data, list):
            current_data = [current_data]
        
        return current_data

class ConnectorManager:
    """Manages all custom connectors"""
    
    def __init__(self):
        self.connectors: Dict[str, BaseConnector] = {}
        self.health_check_task: Optional[asyncio.Task] = None
        self._started = False
        
    async def start_health_monitoring(self):
        """Start background health monitoring"""
        if not self._started:
            self.health_check_task = asyncio.create_task(self._monitor_health())
            self._started = True
    
    async def stop_health_monitoring(self):
        """Stop background health monitoring"""
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        self._started = False
    
    async def create_connector(
        self,
        connector_id: str,
        name: str,
        connector_type: ConnectorType,
        config: Dict[str, Any]
    ) -> BaseConnector:
        """Create a new connector"""
        # Start health monitoring if not already started
        if not self._started:
            await self.start_health_monitoring()
            
        if connector_id in self.connectors:
            raise ValueError(f"Connector {connector_id} already exists")
        
        if connector_type == ConnectorType.REST_API:
            connector = RestApiConnector(connector_id, name, config)
        elif connector_type == ConnectorType.GRAPHQL:
            connector = GraphQLConnector(connector_id, name, config)
        else:
            raise ValueError(f"Unsupported connector type: {connector_type}")
        
        await connector.initialize()
        self.connectors[connector_id] = connector
        
        logger.info(f"Created connector: {connector_id}")
        return connector
    
    async def delete_connector(self, connector_id: str):
        """Delete a connector"""
        connector = self.connectors.get(connector_id)
        if connector:
            await connector.cleanup()
            del self.connectors[connector_id]
            logger.info(f"Deleted connector: {connector_id}")
    
    async def test_connector(self, connector_id: str) -> ConnectionHealth:
        """Test a connector connection"""
        connector = self.connectors.get(connector_id)
        if not connector:
            raise ValueError(f"Connector {connector_id} not found")
        
        return await connector.test_connection()
    
    async def extract_data(
        self,
        connector_id: str,
        extraction_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract data using a connector"""
        connector = self.connectors.get(connector_id)
        if not connector:
            raise ValueError(f"Connector {connector_id} not found")
        
        return await connector.extract_data(extraction_config)
    
    async def _monitor_health(self):
        """Monitor connector health in background"""
        while True:
            try:
                for connector in self.connectors.values():
                    if connector.status == ConnectorStatus.ACTIVE:
                        await connector.test_connection()
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(60)

# Global connector manager
connector_manager = ConnectorManager()

@router.post("/connectors")
async def create_connector(
    connector_config: Dict[str, Any],
    db: Session = Depends(deps.get_db)
):
    """Create a new custom connector"""
    required_fields = ["connector_id", "name", "connector_type", "config"]
    
    for field in required_fields:
        if field not in connector_config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}"
            )
    
    try:
        connector = await connector_manager.create_connector(
            connector_id=connector_config["connector_id"],
            name=connector_config["name"],
            connector_type=ConnectorType(connector_config["connector_type"]),
            config=connector_config["config"]
        )
        
        return {
            "connector_id": connector.connector_id,
            "name": connector.name,
            "connector_type": connector.connector_type,
            "status": connector.status,
            "created_at": datetime.utcnow().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/connectors")
async def list_connectors(db: Session = Depends(deps.get_db)):
    """List all connectors"""
    return {
        "connectors": [
            {
                "connector_id": connector.connector_id,
                "name": connector.name,
                "connector_type": connector.connector_type,
                "status": connector.status,
                "health": {
                    "is_healthy": connector.health.is_healthy,
                    "last_check": connector.health.last_check,
                    "response_time": connector.health.response_time
                },
                "metrics": {
                    "total_requests": connector.metrics.total_requests,
                    "successful_requests": connector.metrics.successful_requests,
                    "failed_requests": connector.metrics.failed_requests,
                    "avg_response_time": connector.metrics.avg_response_time,
                    "data_extracted": connector.metrics.data_extracted
                }
            }
            for connector in connector_manager.connectors.values()
        ]
    }

@router.get("/connectors/{connector_id}")
async def get_connector(
    connector_id: str,
    db: Session = Depends(deps.get_db)
):
    """Get connector details"""
    connector = connector_manager.connectors.get(connector_id)
    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connector not found"
        )
    
    return {
        "connector_id": connector.connector_id,
        "name": connector.name,
        "connector_type": connector.connector_type,
        "status": connector.status,
        "config": connector.config,
        "health": {
            "is_healthy": connector.health.is_healthy,
            "last_check": connector.health.last_check,
            "response_time": connector.health.response_time,
            "error_message": connector.health.error_message,
            "consecutive_failures": connector.health.consecutive_failures
        },
        "metrics": {
            "total_requests": connector.metrics.total_requests,
            "successful_requests": connector.metrics.successful_requests,
            "failed_requests": connector.metrics.failed_requests,
            "avg_response_time": connector.metrics.avg_response_time,
            "last_request_time": connector.metrics.last_request_time,
            "data_extracted": connector.metrics.data_extracted
        }
    }

@router.post("/connectors/{connector_id}/test")
async def test_connector(
    connector_id: str,
    db: Session = Depends(deps.get_db)
):
    """Test connector connection"""
    try:
        health = await connector_manager.test_connector(connector_id)
        return {
            "connector_id": connector_id,
            "health": {
                "is_healthy": health.is_healthy,
                "last_check": health.last_check,
                "response_time": health.response_time,
                "error_message": health.error_message
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/connectors/{connector_id}/extract")
async def extract_data(
    connector_id: str,
    extraction_config: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db)
):
    """Extract data using a connector"""
    try:
        data = await connector_manager.extract_data(connector_id, extraction_config)
        return {
            "connector_id": connector_id,
            "records_extracted": len(data),
            "data": data,
            "extraction_time": datetime.utcnow().isoformat()
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.delete("/connectors/{connector_id}")
async def delete_connector(
    connector_id: str,
    db: Session = Depends(deps.get_db)
):
    """Delete a connector"""
    await connector_manager.delete_connector(connector_id)
    return {"status": "deleted"}
