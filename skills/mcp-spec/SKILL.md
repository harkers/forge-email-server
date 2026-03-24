# Model Context Protocol (MCP) — Full Specification

## Purpose

Complete reference for building MCP servers and clients. Covers every message type, schema, transport, lifecycle phase, and capability in MCP 2025-03-26 (the current stable spec).

---

## 1. What Is MCP?

MCP is a JSON-RPC 2.0 protocol that lets AI hosts (Claude, IDEs, agents) talk to external tool/resource servers in a standard way. Three roles:

| Role | Description | Example |
|------|-------------|---------|
| **Host** | The AI app orchestrating everything | Claude Code, Claude.ai |
| **Client** | One connection inside the host | The MCP client per server |
| **Server** | The external process/service | Your FastAPI tool server |

---

## 2. Transports

### 2.1 stdio (Local Processes)

- Server reads JSON-RPC from **stdin**, writes to **stdout**
- Each message is one newline-terminated JSON line
- stderr is for logging only — never JSON-RPC
- Launched by the host as a subprocess

```
Host  ──stdin──▶  Server process
Host  ◀─stdout──  Server process
                  stderr → host logs
```

### 2.2 HTTP + SSE (Remote Services) — Deprecated in 2025-03-26 but still common

- **Client → Server**: `POST /message` (JSON body)
- **Server → Client**: `GET /sse` (Server-Sent Events stream)
- SSE stream sends `data: <json>\n\n` lines
- Claude Code uses `type: "sse"` in `mcpServers` config

```json
// settings.json
{
  "mcpServers": {
    "my-server": {
      "type": "sse",
      "url": "http://localhost:18099/sse"
    }
  }
}
```

### 2.3 Streamable HTTP (Current Standard — 2025-03-26)

- Single endpoint, typically `POST /mcp`
- Supports both request-response and streaming via HTTP chunked transfer
- Can upgrade to SSE stream mid-response
- Content-Type: `application/json` or `text/event-stream`

```json
// settings.json
{
  "mcpServers": {
    "my-server": {
      "type": "http",
      "url": "http://localhost:18099/mcp"
    }
  }
}
```

### 2.4 stdio Config

```json
{
  "mcpServers": {
    "my-server": {
      "type": "stdio",
      "command": "/usr/local/bin/my-mcp-server",
      "args": ["--port", "8080"],
      "env": {
        "API_KEY": "secret"
      }
    }
  }
}
```

---

## 3. JSON-RPC 2.0 Base Protocol

All MCP messages are JSON-RPC 2.0 objects.

### Request (Client → Server)

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

- `id`: string or integer; must be unique per session; used to match responses
- `params`: optional object

### Response (Server → Client)

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": { ... }
}
```

Or on error:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32600,
    "message": "Invalid request",
    "data": { "detail": "optional extra info" }
  }
}
```

### Notification (either direction, no response)

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized",
  "params": {}
}
```

- No `id` field — notifications never get a response

---

## 4. Lifecycle

Every MCP session follows this exact sequence:

```
Client                          Server
  │                               │
  │── initialize ────────────────▶│
  │                               │ (validates client capabilities)
  │◀─ InitializeResult ───────────│
  │                               │
  │── notifications/initialized ─▶│  (no response)
  │                               │
  │   [normal operation]          │
  │◀──────────────────────────────│
  │                               │
  │── (disconnect)                │
```

### 4.1 initialize Request

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "roots": { "listChanged": true },
      "sampling": {}
    },
    "clientInfo": {
      "name": "my-client",
      "version": "1.0.0"
    }
  }
}
```

**Client capability fields** (all optional):

| Field | Description |
|-------|-------------|
| `roots` | Client supports roots listing |
| `roots.listChanged` | Client sends roots/listChanged notifications |
| `sampling` | Client can handle sampling/createMessage requests from server |

### 4.2 InitializeResult

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "tools": { "listChanged": true },
      "resources": { "subscribe": true, "listChanged": true },
      "prompts": { "listChanged": true },
      "logging": {}
    },
    "serverInfo": {
      "name": "my-mcp-server",
      "version": "0.1.0"
    },
    "instructions": "Optional system prompt text the host can give to the AI"
  }
}
```

**Server capability fields** (all optional):

| Field | Description |
|-------|-------------|
| `tools` | Server has tools |
| `tools.listChanged` | Server sends tools/listChanged notifications |
| `resources` | Server has resources |
| `resources.subscribe` | Server supports resource subscriptions |
| `resources.listChanged` | Server sends resources/listChanged notifications |
| `prompts` | Server has prompts |
| `prompts.listChanged` | Server sends prompts/listChanged notifications |
| `logging` | Server supports setLevel |
| `experimental` | Free-form experimental capability map |

### 4.3 notifications/initialized

After receiving InitializeResult, client MUST send this before any other requests:

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
```

---

## 5. Tools

### 5.1 tools/list

Request:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {
    "cursor": "optional-pagination-cursor"
  }
}
```

Response:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "inputSchema": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "City name or lat/lon"
            },
            "units": {
              "type": "string",
              "enum": ["celsius", "fahrenheit"],
              "default": "celsius"
            }
          },
          "required": ["location"]
        }
      }
    ],
    "nextCursor": "page2-token"
  }
}
```

**Tool object schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✓ | Unique tool identifier |
| `description` | string | — | Human-readable description (shown to AI) |
| `inputSchema` | JSON Schema object | ✓ | Parameters the tool accepts |
| `annotations` | ToolAnnotations | — | Hints about tool behaviour |

**ToolAnnotations:**

```json
{
  "title": "Get Weather",
  "readOnlyHint": true,
  "destructiveHint": false,
  "idempotentHint": true,
  "openWorldHint": true
}
```

| Annotation | Meaning |
|------------|---------|
| `title` | Display name for UI |
| `readOnlyHint` | Does not modify environment |
| `destructiveHint` | May cause irreversible changes |
| `idempotentHint` | Same result if called multiple times |
| `openWorldHint` | Interacts with external systems |

### 5.2 tools/call

Request:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": {
      "location": "London",
      "units": "celsius"
    }
  }
}
```

Response:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "London: 12°C, partly cloudy"
      }
    ],
    "isError": false
  }
}
```

**Content types in result:**

```json
// Text content
{ "type": "text", "text": "some string" }

// Image content
{
  "type": "image",
  "data": "<base64-encoded-bytes>",
  "mimeType": "image/png"
}

// Audio content
{
  "type": "audio",
  "data": "<base64-encoded-bytes>",
  "mimeType": "audio/wav"
}

// Embedded resource
{
  "type": "resource",
  "resource": {
    "uri": "file:///path/to/file.txt",
    "text": "file contents here",
    "mimeType": "text/plain"
  }
}
```

**Error result** (tool ran but returned an error — NOT a JSON-RPC error):
```json
{
  "result": {
    "content": [{ "type": "text", "text": "Error: location not found" }],
    "isError": true
  }
}
```

### 5.3 notifications/tools/listChanged

Server → Client notification when tool list changes:
```json
{
  "jsonrpc": "2.0",
  "method": "notifications/tools/listChanged"
}
```

---

## 6. Resources

Resources expose data the AI can read (files, database rows, live feeds, etc.)

### 6.1 resources/list

Request:
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "resources/list",
  "params": { "cursor": "optional" }
}
```

Response:
```json
{
  "result": {
    "resources": [
      {
        "uri": "file:///home/stu/data.csv",
        "name": "Data CSV",
        "description": "Main dataset",
        "mimeType": "text/csv",
        "size": 204800,
        "annotations": {
          "audience": ["user", "assistant"],
          "priority": 0.8
        }
      }
    ],
    "nextCursor": "page2"
  }
}
```

**Resource object:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `uri` | string (URI) | ✓ | Unique identifier |
| `name` | string | ✓ | Human-readable name |
| `description` | string | — | Longer description |
| `mimeType` | string | — | Content type |
| `size` | number | — | Size in bytes |
| `annotations` | object | — | `audience`, `priority` |

### 6.2 resources/templates/list

Resource URI templates with parameters:

```json
{
  "result": {
    "resourceTemplates": [
      {
        "uriTemplate": "postgres:///{table}/{id}",
        "name": "Database Row",
        "description": "Fetch a single row from any table",
        "mimeType": "application/json"
      }
    ]
  }
}
```

URI templates follow RFC 6570: `{variable}` expands to actual values.

### 6.3 resources/read

Request:
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "resources/read",
  "params": {
    "uri": "file:///home/stu/data.csv"
  }
}
```

Response:
```json
{
  "result": {
    "contents": [
      {
        "uri": "file:///home/stu/data.csv",
        "mimeType": "text/csv",
        "text": "id,name,value\n1,foo,42\n"
      }
    ]
  }
}
```

Contents can be text or blob:
```json
// Text content
{ "uri": "...", "mimeType": "text/plain", "text": "content" }

// Binary content
{ "uri": "...", "mimeType": "image/png", "blob": "<base64>" }
```

### 6.4 resources/subscribe

Request subscription to live updates for a resource:
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "resources/subscribe",
  "params": { "uri": "live://sensor/temperature" }
}
```

Response: `{ "result": {} }`

Server then sends `notifications/resources/updated` when the resource changes.

### 6.5 resources/unsubscribe

```json
{
  "method": "resources/unsubscribe",
  "params": { "uri": "live://sensor/temperature" }
}
```

### 6.6 Resource Notifications

```json
// Resource content changed
{ "method": "notifications/resources/updated", "params": { "uri": "..." } }

// Resource list changed
{ "method": "notifications/resources/listChanged" }
```

---

## 7. Prompts

Prompts are reusable message templates (slash commands, workflows, etc.)

### 7.1 prompts/list

```json
{
  "result": {
    "prompts": [
      {
        "name": "code_review",
        "description": "Review code for issues and improvements",
        "arguments": [
          {
            "name": "language",
            "description": "Programming language",
            "required": false
          },
          {
            "name": "focus",
            "description": "security | performance | style",
            "required": false
          }
        ]
      }
    ]
  }
}
```

### 7.2 prompts/get

Request:
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "prompts/get",
  "params": {
    "name": "code_review",
    "arguments": {
      "language": "Python",
      "focus": "security"
    }
  }
}
```

Response:
```json
{
  "result": {
    "description": "Security-focused Python code review",
    "messages": [
      {
        "role": "user",
        "content": {
          "type": "text",
          "text": "Review the following Python code for security vulnerabilities:\n\n{{code}}"
        }
      }
    ]
  }
}
```

**Message roles:** `"user"` or `"assistant"`

**Message content types:**
```json
// Text
{ "type": "text", "text": "..." }

// Image
{ "type": "image", "data": "<base64>", "mimeType": "image/png" }

// Audio
{ "type": "audio", "data": "<base64>", "mimeType": "audio/wav" }

// Embedded resource
{
  "type": "resource",
  "resource": { "uri": "...", "text": "..." }
}
```

---

## 8. Sampling (Server → Client)

Servers can ask the CLIENT to run an LLM completion. The host decides whether to allow it.

### 8.1 sampling/createMessage

Server sends (as a request to client):
```json
{
  "jsonrpc": "2.0",
  "id": 10,
  "method": "sampling/createMessage",
  "params": {
    "messages": [
      {
        "role": "user",
        "content": { "type": "text", "text": "Summarise this document: ..." }
      }
    ],
    "modelPreferences": {
      "hints": [
        { "name": "claude-3-5-sonnet" }
      ],
      "costPriority": 0.3,
      "speedPriority": 0.5,
      "intelligencePriority": 0.8
    },
    "systemPrompt": "You are a document summariser.",
    "includeContext": "thisServer",
    "temperature": 0.7,
    "maxTokens": 1000,
    "stopSequences": ["END"],
    "metadata": { "custom": "data" }
  }
}
```

Client responds:
```json
{
  "result": {
    "role": "assistant",
    "content": { "type": "text", "text": "Summary: ..." },
    "model": "claude-3-5-sonnet-20241022",
    "stopReason": "endTurn"
  }
}
```

**`includeContext` values:**

| Value | Meaning |
|-------|---------|
| `"none"` | No MCP context injected |
| `"thisServer"` | Include context from this server only |
| `"allServers"` | Include context from all connected servers |

---

## 9. Roots

Clients expose filesystem roots to servers (working directories, project folders).

### 9.1 roots/list (Server requests from Client)

```json
// Server → Client request
{
  "jsonrpc": "2.0",
  "id": 11,
  "method": "roots/list"
}

// Client response
{
  "result": {
    "roots": [
      {
        "uri": "file:///home/stu/mcp-control-plane",
        "name": "mcp-control-plane"
      }
    ]
  }
}
```

### 9.2 notifications/roots/listChanged

Client → Server notification when roots change:
```json
{ "method": "notifications/roots/listChanged" }
```

---

## 10. Logging

Servers can send log messages to the client.

### 10.1 logging/setLevel

Client sets minimum log level the server should send:
```json
{
  "method": "logging/setLevel",
  "params": { "level": "info" }
}
```

**Log levels** (ascending severity): `debug`, `info`, `notice`, `warning`, `error`, `critical`, `alert`, `emergency`

### 10.2 notifications/message (Log notification)

Server → Client:
```json
{
  "method": "notifications/message",
  "params": {
    "level": "warning",
    "logger": "my-server.database",
    "data": "Connection pool at 90% capacity"
  }
}
```

`data` can be any JSON value (string, object, array, etc.)

---

## 11. Pagination

Any list endpoint can return a `nextCursor`. Use it to get the next page:

```json
// First request — no cursor
{ "method": "tools/list", "params": {} }

// Result with more pages
{ "result": { "tools": [...], "nextCursor": "abc123" } }

// Next page
{ "method": "tools/list", "params": { "cursor": "abc123" } }

// Last page — no nextCursor in result
{ "result": { "tools": [...] } }
```

Cursors are opaque strings — never parse or construct them.

---

## 12. Ping / Keep-Alive

Either side can ping:
```json
// Request
{ "jsonrpc": "2.0", "id": 99, "method": "ping" }

// Response
{ "jsonrpc": "2.0", "id": 99, "result": {} }
```

---

## 13. Progress Notifications

For long operations, server can send progress updates:

```json
// Server → Client progress notification
{
  "method": "notifications/progress",
  "params": {
    "progressToken": "op-123",
    "progress": 45,
    "total": 100,
    "message": "Processing file 45 of 100"
  }
}
```

Clients pass `_meta.progressToken` in requests to opt in:
```json
{
  "method": "tools/call",
  "params": {
    "name": "long_running_tool",
    "arguments": { ... },
    "_meta": { "progressToken": "op-123" }
  }
}
```

---

## 14. Cancellation

Either side can cancel an in-flight request:

```json
{
  "method": "notifications/cancelled",
  "params": {
    "requestId": 42,
    "reason": "User cancelled"
  }
}
```

Server should abandon the operation and not send a response for `id: 42`.

---

## 15. Error Codes

### Standard JSON-RPC Errors

| Code | Name | When |
|------|------|------|
| `-32700` | Parse error | Invalid JSON received |
| `-32600` | Invalid request | Not valid JSON-RPC |
| `-32601` | Method not found | Method doesn't exist |
| `-32602` | Invalid params | Wrong parameters |
| `-32603` | Internal error | Server-side failure |

### MCP-Specific Errors

| Code | Name | When |
|------|------|------|
| `-32001` | Request timeout | Operation timed out |
| `-32002` | Resource not found | URI doesn't exist |

---

## 16. Complete Server Implementation Pattern (FastAPI/Python)

### Minimal Tool Server (Streamable HTTP)

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json, uuid

app = FastAPI()

TOOLS = [
    {
        "name": "hello",
        "description": "Say hello",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Who to greet"}
            },
            "required": ["name"]
        }
    }
]

def make_response(id, result):
    return {"jsonrpc": "2.0", "id": id, "result": result}

def make_error(id, code, message):
    return {"jsonrpc": "2.0", "id": id, "error": {"code": code, "message": message}}

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    body = await request.json()
    method = body.get("method")
    id = body.get("id")
    params = body.get("params", {})

    if method == "initialize":
        return make_response(id, {
            "protocolVersion": "2025-03-26",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "my-server", "version": "1.0.0"}
        })

    if method == "notifications/initialized":
        return JSONResponse(content=None, status_code=204)

    if method == "tools/list":
        return make_response(id, {"tools": TOOLS})

    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "hello":
            return make_response(id, {
                "content": [{"type": "text", "text": f"Hello, {args['name']}!"}],
                "isError": False
            })
        return make_error(id, -32601, f"Unknown tool: {name}")

    if method == "ping":
        return make_response(id, {})

    return make_error(id, -32601, f"Method not found: {method}")
```

### stdio Server Pattern

```python
import sys, json, asyncio

async def handle(request):
    method = request.get("method")
    id = request.get("id")
    params = request.get("params", {})

    if method == "initialize":
        return {"protocolVersion": "2025-03-26", "capabilities": {"tools": {}},
                "serverInfo": {"name": "my-server", "version": "1.0.0"}}
    if method == "tools/list":
        return {"tools": TOOLS}
    if method == "tools/call":
        result = await call_tool(params["name"], params.get("arguments", {}))
        return result
    return None

async def main():
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)

    while True:
        line = await reader.readline()
        if not line:
            break
        request = json.loads(line)
        result = await handle(request)
        if result is not None and request.get("id") is not None:
            response = {"jsonrpc": "2.0", "id": request["id"], "result": result}
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
```

---

## 17. SSE Server Pattern (Legacy — still widely used)

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio, json, queue

app = FastAPI()
_queues: dict[str, asyncio.Queue] = {}

@app.get("/sse")
async def sse_stream(request: Request):
    session_id = str(uuid.uuid4())
    q = asyncio.Queue()
    _queues[session_id] = q

    async def generator():
        # Send endpoint event first
        yield f"event: endpoint\ndata: /message?session_id={session_id}\n\n"
        try:
            while True:
                msg = await q.get()
                yield f"data: {json.dumps(msg)}\n\n"
        except asyncio.CancelledError:
            del _queues[session_id]

    return StreamingResponse(generator(), media_type="text/event-stream")

@app.post("/message")
async def handle_message(request: Request, session_id: str):
    body = await request.json()
    response = await dispatch(body)
    if response:
        await _queues[session_id].put(response)
    return JSONResponse({})
```

---

## 18. Client Implementation (stdio bridge pattern)

For bridging an stdio MCP server into HTTP (as used in github-mcp):

```python
import asyncio, json

class MCPStdioClient:
    def __init__(self, cmd: list[str]):
        self.cmd = cmd
        self._proc = None
        self._req_id = 0
        self._initialized = False

    async def start(self):
        self._proc = await asyncio.create_subprocess_exec(
            *self.cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            limit=4 * 1024 * 1024  # 4MB — CRITICAL for large tool lists
        )
        await self._initialize()

    async def _initialize(self):
        await self._send({
            "jsonrpc": "2.0", "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "bridge", "version": "1.0.0"}
            }
        })
        await self._read_response()
        # Send initialized notification (no response expected)
        await self._send({
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        })
        self._initialized = True

    def _next_id(self) -> int:
        self._req_id += 1
        return self._req_id

    async def _send(self, msg: dict):
        line = json.dumps(msg) + "\n"
        self._proc.stdin.write(line.encode())
        await self._proc.stdin.drain()

    async def _read_response(self) -> dict:
        while True:
            line = await self._proc.stdout.readline()
            msg = json.loads(line)
            if "id" in msg:  # Skip notifications (no id)
                return msg

    async def list_tools(self) -> list:
        tools = []
        cursor = None
        while True:
            params = {}
            if cursor:
                params["cursor"] = cursor
            req_id = self._next_id()
            await self._send({"jsonrpc": "2.0", "id": req_id, "method": "tools/list", "params": params})
            resp = await self._read_response()
            result = resp.get("result", {})
            tools.extend(result.get("tools", []))
            cursor = result.get("nextCursor")
            if not cursor:
                break
        return tools

    async def call_tool(self, name: str, arguments: dict) -> dict:
        req_id = self._next_id()
        await self._send({
            "jsonrpc": "2.0", "id": req_id,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments}
        })
        return await self._read_response()

    async def stop(self):
        if self._proc:
            self._proc.terminate()
            await self._proc.wait()
```

---

## 19. Tool Input Schema — Full JSON Schema Support

MCP tool schemas support the full JSON Schema draft-07 subset:

```json
{
  "type": "object",
  "properties": {
    "name": { "type": "string", "minLength": 1, "maxLength": 100 },
    "count": { "type": "integer", "minimum": 1, "maximum": 1000, "default": 10 },
    "mode": { "type": "string", "enum": ["fast", "slow", "auto"] },
    "tags": {
      "type": "array",
      "items": { "type": "string" },
      "minItems": 1
    },
    "options": {
      "type": "object",
      "properties": {
        "verbose": { "type": "boolean" }
      }
    },
    "data": {
      "oneOf": [
        { "type": "string" },
        { "type": "number" }
      ]
    }
  },
  "required": ["name"],
  "additionalProperties": false
}
```

---

## 20. URI Schemes

MCP uses URIs to identify resources. Common schemes:

| Scheme | Example | Use |
|--------|---------|-----|
| `file://` | `file:///home/stu/data.csv` | Local files |
| `https://` | `https://api.example.com/resource` | Remote URLs |
| Custom | `postgres:///users/42` | Database rows |
| Custom | `github:///repo/issues/123` | GitHub objects |
| Custom | `memory:///session/abc` | In-memory state |

---

## 21. Meta Fields

All requests can include `_meta` for protocol-level hints:

```json
{
  "method": "tools/call",
  "params": {
    "name": "my_tool",
    "arguments": { ... },
    "_meta": {
      "progressToken": "token-123"
    }
  }
}
```

---

## 22. Protocol Versions

| Version | Status | Notes |
|---------|--------|-------|
| `2025-03-26` | Current | Streamable HTTP, audio support, OAuth |
| `2024-11-05` | Previous | SSE transport |
| `2024-10-07` | Deprecated | First public release |

Always negotiate: client sends preferred, server responds with what it supports. If incompatible, server returns an error.

---

## 23. Security Considerations

- **Tool confirmation**: Hosts SHOULD ask users before running destructive tools
- **Sampling**: Hosts MUST validate server sampling requests before running LLM calls
- **Resource access**: Servers SHOULD check authorization before exposing URIs
- **Injection**: Never trust tool arguments as safe for shell execution without sanitisation
- **Secrets in env**: Use `env` in stdio config, not args (args may be logged)
- **SSRF**: Validate URIs in resources/read requests to prevent server-side request forgery

---

## 24. Quick Reference — All Methods

### Client → Server

| Method | Purpose |
|--------|---------|
| `initialize` | Start session, negotiate capabilities |
| `ping` | Keep-alive check |
| `tools/list` | Get available tools |
| `tools/call` | Execute a tool |
| `resources/list` | List available resources |
| `resources/templates/list` | List URI templates |
| `resources/read` | Read a resource |
| `resources/subscribe` | Subscribe to resource updates |
| `resources/unsubscribe` | Unsubscribe from updates |
| `prompts/list` | List available prompts |
| `prompts/get` | Get a rendered prompt |
| `logging/setLevel` | Set minimum log level |
| `completion/complete` | Request argument completions |

### Server → Client

| Method | Purpose |
|--------|---------|
| `sampling/createMessage` | Ask client to run LLM inference |
| `roots/list` | Get client's workspace roots |

### Notifications (either direction)

| Method | Direction | Purpose |
|--------|-----------|---------|
| `notifications/initialized` | C→S | Session ready |
| `notifications/cancelled` | Both | Cancel in-flight request |
| `notifications/progress` | S→C | Progress update |
| `notifications/message` | S→C | Log message |
| `notifications/tools/listChanged` | S→C | Tool list updated |
| `notifications/resources/listChanged` | S→C | Resource list updated |
| `notifications/resources/updated` | S→C | Resource content changed |
| `notifications/prompts/listChanged` | S→C | Prompt list updated |
| `notifications/roots/listChanged` | C→S | Roots changed |

---

## 25. OpenClaw MCP Servers Reference

| Server | Port | Profile | Notes |
|--------|------|---------|-------|
| `openclaw` (control plane) | 18100 | always | Main orchestration |
| `deployer-mcp` | 18099 | always | Docker deploy/manage |
| `selenium-mcp` | 18098 | selenium | Selenium Grid sessions |
| `github-mcp` | 18101 | github | Bridge to github-mcp-server binary |
| `native-gateway` | 8765 | always | Claude Code SSE gateway |

All use `network_mode: host` on titan. Access via:
- SSE URL pattern: `http://127.0.0.1:<port>/sse`
- Health: `http://127.0.0.1:<port>/health`
- Tools: `GET http://127.0.0.1:<port>/tools`
- Call: `POST http://127.0.0.1:<port>/call`

---

## 26. Registering in Claude Code settings.json

```json
{
  "mcpServers": {
    "my-server": {
      "type": "sse",
      "url": "http://127.0.0.1:18099/sse"
    },
    "my-stdio-server": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "my_mcp_server"],
      "env": { "API_KEY": "..." }
    },
    "my-http-server": {
      "type": "http",
      "url": "http://127.0.0.1:18099/mcp"
    }
  }
}
```
