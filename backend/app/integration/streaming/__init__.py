"""
Streaming consumers for real-time data processing.
"""
from fastapi import APIRouter, HTTPException, status, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional, Callable, Union
import asyncio
import json
import logging
from datetime import datetime
from app.api import deps
from kafka import KafkaConsumer, KafkaProducer
import redis.asyncio as redis
from dataclasses import dataclass
from enum import Enum
import uuid
import time

logger = logging.getLogger(__name__)

router = APIRouter()

class StreamProtocol(str, Enum):
    KAFKA = "kafka"
    REDIS_STREAMS = "redis_streams"
    WEBSOCKET = "websocket"
    SSE = "sse"

class StreamStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"

@dataclass
class StreamMetrics:
    messages_processed: int = 0
    messages_failed: int = 0
    last_message_time: Optional[datetime] = None
    processing_lag: float = 0.0
    throughput_per_second: float = 0.0
    _last_metrics_time: Optional[float] = None
    _last_msg_count: int = 0

class StreamProcessor:
    """Base class for stream processors"""
    
    def __init__(self, stream_id: str, config: Dict[str, Any]):
        self.stream_id = stream_id
        self.config = config
        self.status = StreamStatus.ACTIVE
        self.metrics = StreamMetrics()
        self.message_handlers: List[Callable] = []
        self.error_handlers: List[Callable] = []
        self.dead_letter_queue: List[Dict[str, Any]] = []
        
        # Metrics tracking attributes
        self._last_metrics_time: Optional[float] = None
        self._last_msg_count: int = 0
        
    async def start(self):
        """Start the stream processor"""
        raise NotImplementedError
    
    async def stop(self):
        """Stop the stream processor"""
        self.status = StreamStatus.STOPPED
    
    async def pause(self):
        """Pause the stream processor"""
        self.status = StreamStatus.PAUSED
    
    async def resume(self):
        """Resume the stream processor"""
        self.status = StreamStatus.ACTIVE
    
    def add_message_handler(self, handler: Callable):
        """Add a message handler"""
        self.message_handlers.append(handler)
    
    def add_error_handler(self, handler: Callable):
        """Add an error handler"""
        self.error_handlers.append(handler)
    
    async def process_message(self, message: Dict[str, Any]):
        """Process a single message"""
        try:
            if self.status != StreamStatus.ACTIVE:
                return
            
            # Update metrics
            self.metrics.messages_processed += 1
            self.metrics.last_message_time = datetime.utcnow()
            
            # Process with handlers
            for handler in self.message_handlers:
                await handler(message)
                
        except Exception as e:
            self.metrics.messages_failed += 1
            await self._handle_error(message, e)
    
    async def _handle_error(self, message: Dict[str, Any], error: Exception):
        """Handle processing errors"""
        error_data = {
            "message": message,
            "error": str(error),
            "timestamp": datetime.utcnow(),
            "stream_id": self.stream_id
        }
        
        # Add to dead letter queue
        self.dead_letter_queue.append(error_data)
        
        # Call error handlers
        for handler in self.error_handlers:
            try:
                await handler(error_data)
            except Exception as handler_error:
                logger.error(f"Error handler failed: {handler_error}")
        
        logger.error(f"Stream processing error in {self.stream_id}: {error}")

class KafkaStreamProcessor(StreamProcessor):
    """Kafka stream processor"""
    
    def __init__(self, stream_id: str, config: Dict[str, Any]):
        super().__init__(stream_id, config)
        self.consumer: Optional[KafkaConsumer] = None
        self.producer: Optional[KafkaProducer] = None
        self._running = False
    
    async def start(self):
        """Start Kafka consumer"""
        try:
            # Create consumer
            self.consumer = KafkaConsumer(
                *self.config.get("topics", []),
                bootstrap_servers=self.config.get("bootstrap_servers", ["localhost:9092"]),
                group_id=self.config.get("group_id", f"xyra_{self.stream_id}"),
                value_deserializer=lambda x: json.loads(x.decode("utf-8")),
                auto_offset_reset=self.config.get("auto_offset_reset", "latest"),
                enable_auto_commit=self.config.get("enable_auto_commit", True)
            )
            
            # Create producer for dead letter queue
            self.producer = KafkaProducer(
                bootstrap_servers=self.config.get("bootstrap_servers", ["localhost:9092"]),
                value_serializer=lambda x: json.dumps(x).encode("utf-8")
            )
            
            self._running = True
            logger.info(f"Started Kafka stream processor: {self.stream_id}")
            
            # Start consuming
            await self._consume_messages()
            
        except Exception as e:
            self.status = StreamStatus.ERROR
            logger.error(f"Failed to start Kafka stream processor {self.stream_id}: {e}")
            raise
    
    async def _consume_messages(self):
        """Consume messages from Kafka"""
        while self._running and self.status != StreamStatus.STOPPED:
            try:
                if self.status == StreamStatus.PAUSED:
                    await asyncio.sleep(1)
                    continue
                
                if self.consumer is None:
                    logger.error("Kafka consumer is not initialized")
                    await asyncio.sleep(5)
                    continue
                
                # Poll for messages
                message_pack = self.consumer.poll(timeout_ms=1000)
                
                for topic_partition, messages in message_pack.items():
                    for message in messages:
                        await self.process_message({
                            "topic": message.topic,
                            "partition": message.partition,
                            "offset": message.offset,
                            "key": message.key.decode("utf-8") if message.key else None,
                            "value": message.value,
                            "timestamp": message.timestamp
                        })
                
            except Exception as e:
                self.status = StreamStatus.ERROR
                logger.error(f"Kafka consumer error: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def stop(self):
        """Stop Kafka consumer"""
        self._running = False
        if self.consumer:
            self.consumer.close()
        if self.producer:
            self.producer.close()
        await super().stop()

class RedisStreamProcessor(StreamProcessor):
    """Redis streams processor"""
    
    def __init__(self, stream_id: str, config: Dict[str, Any]):
        super().__init__(stream_id, config)
        self.redis_client: Optional[redis.Redis] = None
        self._running = False
    
    async def start(self):
        """Start Redis stream consumer"""
        try:
            # Create async Redis client
            self.redis_client = redis.Redis(
                host=self.config.get("host", "localhost"),
                port=self.config.get("port", 6379),
                db=self.config.get("db", 0),
                decode_responses=True
            )
            
            self._running = True
            logger.info(f"Started Redis stream processor: {self.stream_id}")
            
            # Start consuming
            await self._consume_messages()
            
        except Exception as e:
            self.status = StreamStatus.ERROR
            logger.error(f"Failed to start Redis stream processor {self.stream_id}: {e}")
            raise
    
    async def _consume_messages(self):
        """Consume messages from Redis streams"""
        streams = self.config.get("streams", [])
        consumer_group = self.config.get("consumer_group", f"xyra_{self.stream_id}")
        consumer_name = self.config.get("consumer_name", f"consumer_{uuid.uuid4()}")
        
        while self._running and self.status != StreamStatus.STOPPED:
            try:
                if self.status == StreamStatus.PAUSED:
                    await asyncio.sleep(1)
                    continue
                
                if self.redis_client is None:
                    logger.error("Redis client is not initialized")
                    await asyncio.sleep(5)
                    continue
                
                assert self.redis_client is not None, "Redis client should be initialized"
                
                # Read from streams using async Redis client
                try:
                    messages = await self.redis_client.xreadgroup(
                        consumer_group,
                        consumer_name,
                        streams,
                        count=10,
                        block=1000
                    )
                except Exception as redis_error:
                    logger.warning(f"Redis read error: {redis_error}")
                    await asyncio.sleep(1)
                    continue
                
                # Process messages if any were received
                if messages:
                    for stream_name, stream_messages in messages:
                        for msg_id, fields in stream_messages:
                            await self.process_message({
                                "stream": stream_name,
                                "id": msg_id,
                                "fields": fields,
                                "timestamp": datetime.utcnow()
                            })
                            
                            # Acknowledge message
                            try:
                                await self.redis_client.xack(stream_name, consumer_group, msg_id)
                            except Exception as ack_error:
                                logger.warning(f"Failed to acknowledge message {msg_id}: {ack_error}")
                
            except Exception as e:
                self.status = StreamStatus.ERROR
                logger.error(f"Redis stream consumer error: {e}")
                await asyncio.sleep(5)
    
    async def stop(self):
        """Stop Redis stream consumer"""
        self._running = False
        if self.redis_client:
            await self.redis_client.close()
        await super().stop()

class WebSocketStreamProcessor(StreamProcessor):
    """WebSocket stream processor"""
    
    def __init__(self, stream_id: str, config: Dict[str, Any]):
        super().__init__(stream_id, config)
        self.connections: List[WebSocket] = []
        self._running = False
    
    async def add_connection(self, websocket: WebSocket):
        """Add a WebSocket connection"""
        await websocket.accept()
        self.connections.append(websocket)
        logger.info(f"Added WebSocket connection to stream {self.stream_id}")
    
    async def remove_connection(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.connections:
            self.connections.remove(websocket)
            logger.info(f"Removed WebSocket connection from stream {self.stream_id}")
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.connections:
            return
        
        disconnected = []
        for connection in self.connections:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                disconnected.append(connection)
            except Exception as e:
                logger.error(f"WebSocket broadcast error: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            await self.remove_connection(conn)

class StreamManager:
    """Manages all stream processors"""
    
    def __init__(self):
        self.processors: Dict[str, StreamProcessor] = {}
        self.metrics_collector: Optional[asyncio.Task] = None
        self._started = False
    
    async def start(self):
        """Start the stream manager and its metrics collection"""
        if not self._started:
            self.metrics_collector = asyncio.create_task(self._collect_metrics())
            self._started = True
    
    async def stop(self):
        """Stop the stream manager and all processors"""
        if self.metrics_collector:
            self.metrics_collector.cancel()
            try:
                await self.metrics_collector
            except asyncio.CancelledError:
                pass
        
        # Stop all processors
        for processor in list(self.processors.values()):
            await processor.stop()
        
        self.processors.clear()
        self._started = False
    
    async def create_stream_processor(
        self,
        stream_id: str,
        protocol: StreamProtocol,
        config: Dict[str, Any]
    ) -> StreamProcessor:
        """Create a new stream processor"""
        # Ensure manager is started
        if not self._started:
            await self.start()
            
        if stream_id in self.processors:
            raise ValueError(f"Stream processor {stream_id} already exists")
        
        if protocol == StreamProtocol.KAFKA:
            processor = KafkaStreamProcessor(stream_id, config)
        elif protocol == StreamProtocol.REDIS_STREAMS:
            processor = RedisStreamProcessor(stream_id, config)
        elif protocol == StreamProtocol.WEBSOCKET:
            processor = WebSocketStreamProcessor(stream_id, config)
        else:
            raise ValueError(f"Unsupported stream protocol: {protocol}")
        
        self.processors[stream_id] = processor
        logger.info(f"Created stream processor: {stream_id}")
        
        return processor
    
    async def start_stream(self, stream_id: str):
        """Start a stream processor"""
        processor = self.processors.get(stream_id)
        if not processor:
            raise ValueError(f"Stream processor {stream_id} not found")
        
        await processor.start()
    
    async def stop_stream(self, stream_id: str):
        """Stop a stream processor"""
        processor = self.processors.get(stream_id)
        if processor:
            await processor.stop()
            del self.processors[stream_id]
    
    async def pause_stream(self, stream_id: str):
        """Pause a stream processor"""
        processor = self.processors.get(stream_id)
        if processor:
            await processor.pause()
    
    async def resume_stream(self, stream_id: str):
        """Resume a stream processor"""
        processor = self.processors.get(stream_id)
        if processor:
            await processor.resume()
    
    def get_stream_metrics(self, stream_id: str) -> Optional[StreamMetrics]:
        """Get metrics for a stream processor"""
        processor = self.processors.get(stream_id)
        return processor.metrics if processor else None
    
    async def _collect_metrics(self):
        """Collect metrics from all stream processors"""
        while True:
            try:
                current_time = time.time()
                
                for processor in self.processors.values():
                    # Calculate throughput
                    if processor._last_metrics_time is not None:
                        time_diff = current_time - processor._last_metrics_time
                        msg_diff = processor.metrics.messages_processed - processor._last_msg_count
                        processor.metrics.throughput_per_second = msg_diff / time_diff if time_diff > 0 else 0
                    
                    processor._last_metrics_time = current_time
                    processor._last_msg_count = processor.metrics.messages_processed
                
                await asyncio.sleep(60)  # Collect metrics every minute
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(60)

# Global stream manager
stream_manager = StreamManager()

@router.post("/streams")
async def create_stream_processor(
    stream_config: Dict[str, Any],
    db: Session = Depends(deps.get_db)
):
    """Create a new stream processor"""
    required_fields = ["stream_id", "protocol", "config"]
    
    for field in required_fields:
        if field not in stream_config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}"
            )
    
    try:
        processor = await stream_manager.create_stream_processor(
            stream_id=stream_config["stream_id"],
            protocol=StreamProtocol(stream_config["protocol"]),
            config=stream_config["config"]
        )
        
        return {
            "stream_id": stream_config["stream_id"],
            "protocol": stream_config["protocol"],
            "status": processor.status,
            "created_at": datetime.utcnow().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/streams/{stream_id}/start")
async def start_stream(
    stream_id: str,
    db: Session = Depends(deps.get_db)
):
    """Start a stream processor"""
    try:
        await stream_manager.start_stream(stream_id)
        return {"status": "started"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/streams/{stream_id}/stop")
async def stop_stream(
    stream_id: str,
    db: Session = Depends(deps.get_db)
):
    """Stop a stream processor"""
    await stream_manager.stop_stream(stream_id)
    return {"status": "stopped"}

@router.post("/streams/{stream_id}/pause")
async def pause_stream(
    stream_id: str,
    db: Session = Depends(deps.get_db)
):
    """Pause a stream processor"""
    try:
        await stream_manager.pause_stream(stream_id)
        return {"status": "paused"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/streams/{stream_id}/resume")
async def resume_stream(
    stream_id: str,
    db: Session = Depends(deps.get_db)
):
    """Resume a stream processor"""
    try:
        await stream_manager.resume_stream(stream_id)
        return {"status": "resumed"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/streams/{stream_id}/metrics")
async def get_stream_metrics(
    stream_id: str,
    db: Session = Depends(deps.get_db)
):
    """Get stream processor metrics"""
    metrics = stream_manager.get_stream_metrics(stream_id)
    if not metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream processor not found"
        )
    
    return {
        "stream_id": stream_id,
        "messages_processed": metrics.messages_processed,
        "messages_failed": metrics.messages_failed,
        "last_message_time": metrics.last_message_time,
        "processing_lag": metrics.processing_lag,
        "throughput_per_second": metrics.throughput_per_second
    }

@router.get("/streams")
async def list_streams(db: Session = Depends(deps.get_db)):
    """List all stream processors"""
    return {
        "streams": [
            {
                "stream_id": stream_id,
                "status": processor.status,
                "protocol": type(processor).__name__,
                "metrics": {
                    "messages_processed": processor.metrics.messages_processed,
                    "messages_failed": processor.metrics.messages_failed,
                    "throughput_per_second": processor.metrics.throughput_per_second
                }
            }
            for stream_id, processor in stream_manager.processors.items()
        ]
    }

@router.websocket("/streams/{stream_id}/ws")
async def websocket_stream_endpoint(websocket: WebSocket, stream_id: str):
    """WebSocket endpoint for real-time streaming"""
    processor = stream_manager.processors.get(stream_id)
    
    if not processor or not isinstance(processor, WebSocketStreamProcessor):
        await websocket.close(code=4004, reason="Stream not found or not a WebSocket stream")
        return
    
    await processor.add_connection(websocket)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_json()
            
            # Process received message
            await processor.process_message({
                "source": "websocket",
                "data": data,
                "timestamp": datetime.utcnow()
            })
            
    except WebSocketDisconnect:
        await processor.remove_connection(websocket)
