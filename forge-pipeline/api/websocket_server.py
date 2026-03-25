#!/usr/bin/env python3
"""
FP-094: WebSocket server for real-time updates.
Runs on port 4182 alongside the HTTP API on 4181.
"""

import asyncio
import json
import os
import time
from datetime import datetime, timezone

try:
    import websockets
    from websockets.server import serve
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    serve = None

# Redis for pub/sub
try:
    from redis import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    Redis = None

WS_PORT = int(os.environ.get("FORGE_PIPELINE_WS_PORT", 4182))
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

# Connected clients
clients = set()

# Redis connection
_redis = None

def get_redis():
    global _redis
    if not REDIS_AVAILABLE:
        return None
    if _redis is None:
        try:
            _redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_connect_timeout=2)
            _redis.ping()
        except Exception:
            _redis = None
    return _redis


async def handler(websocket, path=None):
    """Handle WebSocket connection."""
    clients.add(websocket)
    client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}" if websocket.remote_address else "unknown"
    print(f"[WS] Client connected: {client_id} (total: {len(clients)})")
    
    try:
        # Send initial connection message
        await websocket.send(json.dumps({
            "type": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }))
        
        # Listen for client messages (ping/pong, subscription preferences)
        async for message in websocket:
            try:
                data = json.loads(message)
                if data.get("type") == "ping":
                    await websocket.send(json.dumps({"type": "pong", "timestamp": datetime.now(timezone.utc).isoformat()}))
            except json.JSONDecodeError:
                pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients.discard(websocket)
        print(f"[WS] Client disconnected: {client_id} (total: {len(clients)})")


async def broadcast(event_type, payload):
    """Broadcast an event to all connected clients."""
    if not clients:
        return
    
    message = json.dumps({
        "type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    })
    
    # Send to all clients
    disconnected = set()
    for client in clients:
        try:
            await client.send(message)
        except Exception:
            disconnected.add(client)
    
    # Clean up disconnected clients
    clients.difference_update(disconnected)


async def redis_listener():
    """Listen to Redis pub/sub for events from the HTTP API."""
    redis = get_redis()
    if not redis:
        print("[WS] Redis not available, skipping pub/sub listener")
        return
    
    pubsub = redis.pubsub()
    pubsub.subscribe("forge-pipeline:events")
    
    print(f"[WS] Listening to Redis pub/sub on forge-pipeline:events")
    
    async def process_message():
        """Process Redis messages."""
        # Run in executor since redis pubsub is blocking
        loop = asyncio.get_event_loop()
        try:
            while True:
                message = await loop.run_in_executor(None, pubsub.get_message, True, 1)
                if message and message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        await broadcast(data.get("event", "update"), data.get("payload", {}))
                    except json.JSONDecodeError:
                        pass
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass
        finally:
            pubsub.unsubscribe("forge-pipeline:events")
    
    await process_message()


def publish_event(event_type, payload):
    """Publish an event to Redis for WebSocket broadcast."""
    redis = get_redis()
    if redis:
        redis.publish("forge-pipeline:events", json.dumps({
            "event": event_type,
            "payload": payload,
        }))


async def main():
    """Start the WebSocket server."""
    if not WEBSOCKETS_AVAILABLE:
        print("[WS] websockets library not installed, WebSocket server disabled")
        return
    
    print(f"[WS] Starting WebSocket server on port {WS_PORT}")
    
    # Start Redis listener in background
    listener_task = asyncio.create_task(redis_listener())
    
    # Start WebSocket server
    async with serve(handler, "0.0.0.0", WS_PORT):
        print(f"[WS] WebSocket server running on ws://0.0.0.0:{WS_PORT}")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())