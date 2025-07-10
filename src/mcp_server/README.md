# Deep Research MCP Server

## Overview

This is a FastMCP server implementation that wraps the LangGraph deep research agent as an MCP tool. The server provides a `research` tool that conducts comprehensive web research using Google Search API and Gemini models.

## Phase 1 Implementation Status ✅

### Completed Components

#### 1. FastMCP Server Core (`server.py`)
- ✅ FastMCP server initialization with proper configuration
- ✅ `research` tool implementation with comprehensive documentation
- ✅ Input validation and error handling
- ✅ Progress streaming using MCP Context logging
- ✅ Health check endpoint (`/health`)
- ✅ Statistics endpoint (`/stats`)
- ✅ Proper async/await support

#### 2. Configuration Management (`config.py`)
- ✅ Environment variable management
- ✅ Pydantic-based configuration validation
- ✅ API key validation
- ✅ Configurable model settings
- ✅ Request timeout and concurrency limits

#### 3. Agent Adapter (`agent_adapter.py`)
- ✅ Async wrapper for the LangGraph agent
- ✅ Progress callback system for MCP streaming
- ✅ State management for concurrent requests
- ✅ Proper error handling and timeouts
- ✅ Health check functionality
- ✅ Statistics collection

#### 4. Utility Functions (`utils.py`)
- ✅ Input validation and sanitization
- ✅ Error response formatting
- ✅ Execution time formatting
- ✅ Progress tracking utilities
- ✅ Logging helpers

## Tool Interface

### `research` Tool

```python
async def research(
    topic: str,
    max_research_loops: int = 2,
    initial_search_query_count: int = 3,
    reasoning_model: str = "gemini-2.5-pro",
    ctx: Context = None
) -> Dict[str, Any]
```

**Input Parameters:**
- `topic`: The research topic or question to investigate
- `max_research_loops`: Maximum number of research iterations (default: 2)
- `initial_search_query_count`: Number of initial search queries (default: 3)
- `reasoning_model`: Model for final answer generation (default: gemini-2.5-pro)

**Output:**
```json
{
  "report": "Full research report with citations",
  "sources": ["list of source URLs"],
  "metadata": {
    "queries_executed": 5,
    "research_loops": 2,
    "total_sources": 12,
    "execution_time": 45.2,
    "reasoning_model": "gemini-2.5-pro",
    "request_id": 1
  }
}
```

## Configuration

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional (with defaults)
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8000
LOG_LEVEL=INFO
DEFAULT_MAX_RESEARCH_LOOPS=2
DEFAULT_INITIAL_SEARCH_QUERY_COUNT=3
DEFAULT_REASONING_MODEL=gemini-2.5-pro
REQUEST_TIMEOUT=300
MAX_CONCURRENT_REQUESTS=10
```

## Usage

### Starting the Server

```bash
# Set environment variables
export GEMINI_API_KEY=your_api_key_here

# Start the server
python -m src.mcp_server
```

The server will start on `http://0.0.0.0:8000` with the MCP endpoint at `/mcp/`.

### Health Check

```bash
curl http://localhost:8000/health
```

### Using FastMCP Client

```python
from fastmcp import Client

async def use_research_tool():
    client = Client("http://localhost:8000/mcp/")
    async with client:
        result = await client.call_tool("research", {
            "topic": "Latest developments in AI research",
            "max_research_loops": 3
        })
        print(result)
```

### Using HTTP Client

```python
import aiohttp

async def call_research_via_http():
    async with aiohttp.ClientSession() as session:
        payload = {
            "method": "tools/call",
            "params": {
                "name": "research",
                "arguments": {
                    "topic": "What is quantum computing?",
                    "max_research_loops": 2
                }
            }
        }
        async with session.post("http://localhost:8000/mcp/", json=payload) as response:
            result = await response.json()
            print(result)
```

## Testing

### Run Unit Tests

```bash
python test_mcp_server.py
```

### Run Client Examples

```bash
# Start the server first
python -m src.mcp_server

# In another terminal
python example_client.py
```

## Progress Streaming

The server provides real-time progress updates through MCP Context logging:

```
🔍 Starting research on: What is quantum computing?
Configuration: loops=2, queries=3, model=gemini-2.5-pro
Executing research agent...
✅ Research completed successfully!
📊 Generated 8 sources in 34.2s
```

## Error Handling

The server includes comprehensive error handling:

- **Input Validation**: Validates all parameters before processing
- **Rate Limiting**: Prevents server overload with concurrent request limits
- **Timeout Management**: Prevents long-running requests from hanging
- **Graceful Degradation**: Handles API failures and model unavailability
- **Structured Error Responses**: Provides detailed error information

## Monitoring

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

Returns:
```json
{
  "status": "healthy",
  "service": "Deep Research Agent MCP Server",
  "version": "0.1.0",
  "agent": {
    "status": "healthy",
    "active_requests": 0,
    "total_requests": 5
  },
  "config": {
    "max_research_loops": 2,
    "initial_search_query_count": 3,
    "reasoning_model": "gemini-2.5-pro"
  }
}
```

### Statistics Endpoint

```bash
curl http://localhost:8000/stats
```

Returns:
```json
{
  "total_requests": 10,
  "active_requests": 2,
  "max_concurrent_requests": 10,
  "request_timeout": 300
}
```

## Security Considerations

- ✅ API key validation on startup
- ✅ Input sanitization and validation
- ✅ Request rate limiting
- ✅ Timeout protection
- ✅ Error message sanitization

## Next Steps (Phase 2)

- [ ] Docker containerization
- [ ] Production deployment configuration
- [ ] Advanced error handling and retries
- [ ] Caching layer for research results
- [ ] WebSocket support for real-time streaming
- [ ] Client SDKs for different programming languages

## Troubleshooting

### Common Issues

1. **Server won't start**: Check that `GEMINI_API_KEY` is set
2. **Import errors**: Install dependencies with `pip install -r requirements.txt`
3. **Connection refused**: Ensure server is running on correct host/port
4. **Research fails**: Verify Google Search API access and quotas

### Debug Mode

Set `LOG_LEVEL=DEBUG` for detailed logging:

```bash
export LOG_LEVEL=DEBUG
python -m src.mcp_server
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FastMCP Server                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 Research Tool                               │ │
│  │  ├─ Input Validation                                       │ │
│  │  ├─ Progress Streaming                                     │ │
│  │  ├─ LangGraph Agent Adapter                               │ │
│  │  └─ Result Formatting                                     │ │
│  └─────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 Health & Stats                              │ │
│  │  ├─ Health Check Endpoint                                 │ │
│  │  ├─ Statistics Endpoint                                   │ │
│  │  └─ Monitoring                                            │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Files Structure

```
src/mcp_server/
├── __init__.py          # Package initialization
├── __main__.py          # Module entry point
├── server.py            # Main FastMCP server
├── config.py            # Configuration management
├── agent_adapter.py     # LangGraph agent wrapper
├── utils.py             # Utility functions
└── README.md           # This file
```

## Contributing

1. Ensure all tests pass: `python test_mcp_server.py`
2. Follow the existing code style
3. Add tests for new functionality
4. Update documentation as needed 