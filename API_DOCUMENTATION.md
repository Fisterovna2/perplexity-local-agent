# Perplexity Local Agent - API Documentation

## Overview

This document describes the complete REST API for Perplexity Local Agent v2.0. All endpoints require valid JSON requests and return JSON responses.

**Base URL:** `http://localhost:5000`

**API Version:** `/api/v1`

---

## Authentication

Currently, authentication is optional (disabled by default). To enable it, modify `config.yaml`:

```yaml
security:
  require_auth: true
  api_key: "your-secret-key"
```

When enabled, include header:
```
Authorization: Bearer <api_key>
```

---

## Endpoints

### 1. POST /api/v1/execute

**Description:** Execute a command with full validation, safety checks, and optional confirmation.

**Request:**
```json
{
  "command": "string",           // Command name (required)
  "params": {"key": "value"},   // Command parameters (optional)
  "confirmed": boolean,           // User confirmation (required if safety.require_confirmation=true)
  "user_id": "string"            // User identifier for logging (optional)
}
```

**Response (Success):**
```json
{
  "success": true,
  "result": "Execution result",
  "execution_time": 2.35,
  "timestamp": "2025-12-06T21:00:00.000Z"
}
```

**Response (Requires Confirmation):**
```json
{
  "success": false,
  "requires_confirmation": true,
  "info": "Detailed description of what this command does",
  "action": "CONFIRM_REQUIRED"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Error message"
}
```

**Status Codes:**
- `200`: Command executed successfully
- `400`: Missing/invalid parameters or confirmation required
- `403`: Command not in whitelist or dangerous pattern detected
- `500`: Internal server error

---

### 2. GET /api/v1/info

**Description:** Get agent information and list of available commands.

**Response:**
```json
{
  "agent": "Perplexity Local Agent",
  "version": "2.0",
  "status": "running",
  "tools": {
    "python_exec": "Execute Python code safely",
    "file_operation": "File I/O operations",
    "open_program": "Launch programs",
    "get_system_info": "System information"
  },
  "safety_level": "MAXIMUM",
  "requires_confirmation": true,
  "timestamp": "2025-12-06T21:00:00.000Z"
}
```

---

### 3. GET /api/v1/command-info/<command>

**Description:** Get detailed information about a specific command.

**Parameters:**
- `command` (path): Command name (e.g., `python_exec`)

**Response:**
```json
{
  "name": "Python Code Executor",
  "description": "Execute Python code in a sandboxed environment",
  "warning": "Dangerous imports will be blocked",
  "params": ["code", "timeout"]
}
```

---

### 4. GET /health

**Description:** Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-06T21:00:00.000Z",
  "uptime": "running"
}
```

---

## Command Reference

### Command: `python_exec`

Execute Python code in a sandboxed environment.

**Parameters:**
```json
{
  "code": "print('Hello')",
  "timeout": 30
}
```

**Blocked patterns:**
- `os.system`, `__import__`, `eval`, `exec`, `compile`, `open`, `input`, `file`

**Example:**
```bash
curl -X POST http://localhost:5000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "python_exec",
    "params": {"code": "import math; print(math.sqrt(16))"},
    "confirmed": true
  }'
```

---

### Command: `file_operation`

Safely handle file operations (create, read, delete).

**Parameters:**
```json
{
  "action": "create|read|delete",
  "path": "/path/to/file",
  "content": "file content (for create action)"
}
```

**Example - Create:**
```bash
curl -X POST http://localhost:5000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "file_operation",
    "params": {
      "action": "create",
      "path": "test.txt",
      "content": "Hello World"
    },
    "confirmed": true
  }'
```

**Security:**
- Path traversal (`..`) is blocked
- Files are created relative to working directory

---

### Command: `open_program`

Launch whitelisted programs.

**Parameters:**
```json
{
  "program": "notepad|calc|paint|explorer|cmd",
  "args": ["arg1", "arg2"]
}
```

**Whitelisted Programs:**
- `notepad` - Text editor
- `calc` - Calculator
- `paint` - Paint application
- `explorer` - File explorer
- `cmd` - Command prompt

**Example:**
```bash
curl -X POST http://localhost:5000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "open_program",
    "params": {"program": "notepad"},
    "confirmed": true
  }'
```

---

### Command: `get_system_info`

Retrieve system and Python information.

**Parameters:** None

**Response:**
```json
{
  "success": true,
  "system": "Windows",
  "python_version": "3.11.0",
  "machine": "AMD64",
  "processor": "Intel Core i7"
}
```

---

## Error Codes

| Code | Message | Meaning |
|------|---------|----------|
| 400 | No command provided | Missing `command` field in request |
| 400 | Command not in whitelist | Command is not allowed |
| 403 | Dangerous pattern detected | Command contains blocked pattern |
| 403 | CONFIRM_REQUIRED | User must confirm before execution |
| 500 | Internal server error | Server-side error occurred |
| 404 | Endpoint not found | Invalid API route |

---

## Rate Limiting

Default rate limit: 100 requests per minute per IP address.

Configure in `config.yaml`:
```yaml
security:
  rate_limit: 100
```

---

## Logging

All API requests and executions are logged to `backend/logs/agent.log` in JSON format:

```json
{
  "timestamp": "2025-12-06T21:00:00.000000",
  "user": "user_id",
  "command": "python_exec",
  "status": "success",
  "result_preview": "Command output (first 100 chars)"
}
```

---

## Examples

### Example 1: Get Agent Info
```bash
curl http://localhost:5000/api/v1/info
```

### Example 2: Check Health
```bash
curl http://localhost:5000/health
```

### Example 3: Get Command Info Before Execution
```bash
curl http://localhost:5000/api/v1/command-info/python_exec
```

### Example 4: Execute with Safety Confirmation
```bash
# Step 1: Check if confirmation required
curl -X POST http://localhost:5000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "python_exec", "params": {"code": "print(1+1)"}}'

# Response: requires_confirmation=true

# Step 2: Re-execute with confirmation
curl -X POST http://localhost:5000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "python_exec", "params": {"code": "print(1+1)"}, "confirmed": true}'
```

---

## Best Practices

1. **Always check command info first** before execution
2. **Use meaningful user_id** for audit trail
3. **Handle confirmation flow** in your client
4. **Monitor logs** for security issues
5. **Keep agent.log** for compliance
6. **Test with /health** endpoint first
7. **Use timeouts** for long-running operations

---

**Last Updated:** 2025-12-06
**API Version:** v1.0
**Status:** Production Ready
