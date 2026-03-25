#!/usr/bin/env python3
"""
Entrypoint that runs both HTTP API and WebSocket server.
"""

import os
import sys
import threading
import time

def run_http_server():
    """Run the HTTP API server."""
    from server import HTTPServer, ForgePipelineHandler
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 4181))
    server = HTTPServer((host, port), ForgePipelineHandler)
    print(f"[HTTP] Server starting on http://{host}:{port}")
    server.serve_forever()

def run_websocket_server():
    """Run the WebSocket server in a separate thread."""
    try:
        import asyncio
        from websocket_server import main as ws_main
        asyncio.run(ws_main())
    except ImportError as e:
        print(f"[WS] WebSocket server not available: {e}")
        print("[WS] Continuing with HTTP-only mode")

def main():
    """Start both servers."""
    ws_enabled = os.environ.get("FORGE_PIPELINE_WS_ENABLED", "true").lower() == "true"
    
    if ws_enabled:
        # Try to import websockets
        try:
            import websockets
            # Start WebSocket server in a separate thread
            ws_thread = threading.Thread(target=run_websocket_server, daemon=True)
            ws_thread.start()
            print("[MAIN] WebSocket server thread started")
        except ImportError:
            print("[MAIN] websockets not installed, running HTTP-only mode")
    
    # Run HTTP server in main thread
    run_http_server()

if __name__ == "__main__":
    main()