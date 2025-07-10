# Deep Research Agent MCP Server Integration Plan

## Overview

This document outlines the detailed plan for wrapping the existing LangGraph deep research agent as a Model Context Protocol (MCP) server using FastMCP, with Docker containerization and streamable HTTP support for remote deployment.

## Current State Analysis

### Existing Components
- **LangGraph Agent**: A sophisticated research agent that conducts multi-step web research using Google Search API and Gemini models
- **Agent Features**:
  - Multi-query web research with iterative refinement
  - Uses Google Search API with grounding metadata
  - Implements reflection loops for comprehensive coverage
  - Supports configurable research depth and query count
  - Outputs structured research reports with proper citations

### Current Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    Current LangGraph Agent                      │
├─────────────────────────────────────────────────────────────────┤
│  Input: Research Topic (string)                                 │
│  ├─ Query Generation (Gemini 2.0 Flash)                        │
│  ├─ Web Research (Google Search API + Gemini)                  │
│  ├─ Reflection & Gap Analysis (Gemini 2.5 Flash)              │
│  ├─ Iterative Research Loops                                   │
│  └─ Final Report Generation (Gemini 2.5 Pro)                  │
│  Output: Research Report with Citations                         │
└─────────────────────────────────────────────────────────────────┘
```

## Target Architecture

### MCP Server Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    MCP Server (FastMCP)                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 MCP Tool: research                          │ │
│  │  Input: topic (string), config (optional)                  │ │
│  │  ├─ Validate Input                                         │ │
│  │  ├─ Initialize LangGraph Agent                             │ │
│  │  ├─ Execute Research Workflow                              │ │
│  │  ├─ Stream Progress Updates                                │ │
│  │  └─ Return Structured Report                               │ │
│  │  Output: Research Report with Metadata                     │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Deployment Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    Docker Container                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │               FastMCP Server                                │ │
│  │  Transport: Streamable HTTP                                │ │
│  │  Port: 8000                                                │ │
│  │  Health Check: /health                                     │ │
│  │  MCP Endpoint: /mcp/                                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │               LangGraph Agent                               │ │
│  │  Research Engine + Google Search + Gemini Models           │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Implementation Plan

### Phase 1: MCP Server Core Implementation

#### 1.1 Create FastMCP Server Wrapper
**File**: `src/mcp_server/server.py`
- Implement FastMCP server initialization
- Create `research` tool that wraps the LangGraph agent
- Add input validation and error handling
- Implement progress streaming using MCP logging
- Add configuration options for research parameters

#### 1.2 Tool Interface Design
```python
@mcp.tool
async def research(
    topic: str,
    max_research_loops: int = 2,
    initial_search_query_count: int = 3,
    reasoning_model: str = "gemini-2.5-pro",
    ctx: Context = None
) -> dict:
    """
    Conduct comprehensive web research on a given topic.
    
    Args:
        topic: The research topic or question
        max_research_loops: Maximum number of research iterations (default: 2)
        initial_search_query_count: Number of initial search queries (default: 3)  
        reasoning_model: Model for final answer generation (default: gemini-2.5-pro)
        
    Returns:
        {
            "report": "Full research report with citations",
            "sources": ["list of source URLs"],
            "metadata": {
                "queries_executed": int,
                "research_loops": int,
                "total_sources": int,
                "execution_time": float
            }
        }
    """
```

#### 1.3 Progress Streaming Implementation
- Use MCP Context logging for real-time progress updates
- Stream query generation, web search, and reflection steps
- Provide detailed execution status to clients

### Phase 2: Agent Integration

#### 2.1 LangGraph Agent Adapter
**File**: `src/mcp_server/agent_adapter.py`
- Create async wrapper for the existing LangGraph agent
- Implement state management for concurrent requests
- Add progress callback system for MCP streaming
- Handle agent errors and timeouts gracefully

#### 2.2 Configuration Management
**File**: `src/mcp_server/config.py`
- Environment variable management for API keys
- Model configuration options
- Research parameters with sensible defaults
- Validation for required credentials

#### 2.3 Error Handling & Resilience
- Implement retry logic for API failures
- Add circuit breaker pattern for external services
- Graceful degradation when models are unavailable
- Comprehensive error logging and reporting

### Phase 3: Docker Containerization

#### 3.1 Dockerfile Implementation
**File**: `Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY pyproject.toml ./

# Install the application
RUN pip install -e .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run the MCP server
CMD ["python", "-m", "src.mcp_server.server"]
```

#### 3.2 Docker Compose Configuration
**File**: `docker-compose.yml`
```yaml
version: '3.8'

services:
  deep-research-mcp:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

#### 3.3 Multi-stage Build Optimization
- Use multi-stage builds for smaller production images
- Separate build dependencies from runtime dependencies
- Optimize layer caching for faster builds

### Phase 4: HTTP Transport & Deployment

#### 4.1 Streamable HTTP Implementation
**File**: `src/mcp_server/server.py`
```python
if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000,
        path="/mcp/",
        log_level="info"
    )
```

#### 4.2 Health Check Endpoint
- Add custom health check route
- Verify agent initialization and model availability
- Return service status and version information

#### 4.3 Production Deployment Features
- Configure proper logging with structured output
- Add metrics collection endpoints
- Implement graceful shutdown handling
- Add request rate limiting and timeout management

### Phase 5: Integration & Testing

#### 5.1 Client Integration Examples
**File**: `examples/client_examples.py`
- FastMCP client integration examples
- Claude Desktop configuration
- Cursor IDE integration guide
- HTTP client examples for web applications

#### 5.2 Testing Suite
**File**: `tests/`
- Unit tests for MCP tool implementation
- Integration tests with mock LangGraph responses
- Load testing for concurrent research requests
- End-to-end tests with real API calls

#### 5.3 Documentation & Examples
- API documentation for the research tool
- Docker deployment guide
- Client integration tutorials
- Troubleshooting guide

## File Structure

```
deep-research-mcp/
├── src/
│   ├── agent/                      # Existing LangGraph agent
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── configuration.py
│   │   ├── graph.py
│   │   ├── prompts.py
│   │   ├── state.py
│   │   ├── tools_and_schemas.py
│   │   └── utils.py
│   └── mcp_server/                 # New MCP server implementation
│       ├── __init__.py
│       ├── server.py               # Main FastMCP server
│       ├── agent_adapter.py        # LangGraph agent wrapper
│       ├── config.py               # Configuration management
│       └── utils.py                # Utility functions
├── tests/
│   ├── test_mcp_server.py
│   ├── test_agent_adapter.py
│   └── test_integration.py
├── examples/
│   ├── client_examples.py
│   ├── claude_desktop_config.json
│   └── cursor_config.json
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .dockerignore
├── docs/
│   ├── deployment.md
│   ├── api_reference.md
│   └── client_integration.md
├── requirements.txt                # Updated with FastMCP
├── pyproject.toml                  # Updated configuration
├── langgraph.json                  # Existing LangGraph config
└── README.md                       # This plan document
```

## Dependencies

### New Dependencies to Add
```
fastmcp>=2.3.0
uvicorn>=0.24.0
```

### Environment Variables Required
```
GEMINI_API_KEY=your_gemini_api_key_here
LOG_LEVEL=INFO
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8000
```

## Security Considerations

### 1. API Key Management
- Use environment variables for sensitive credentials
- Implement secure credential rotation
- Add API key validation on startup

### 2. Network Security
- Configure proper CORS settings
- Implement request rate limiting
- Add input sanitization and validation

### 3. Container Security
- Use non-root user in container
- Implement proper secret management
- Regular security updates for base images

## Monitoring & Observability

### 1. Logging Strategy
- Structured logging with JSON format
- Request/response logging with correlation IDs
- Performance metrics for research operations

### 2. Health Monitoring
- Health check endpoints for container orchestration
- Readiness and liveness probes
- Service dependency health checks

### 3. Metrics Collection
- Research request success/failure rates
- Average research completion time
- Resource utilization metrics

## Deployment Options

### 1. Local Development
```bash
# Clone repository
git clone <repository-url>
cd deep-research-mcp

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY=your_api_key

# Run MCP server
python -m src.mcp_server.server
```

### 2. Docker Deployment
```bash
# Build image
docker build -t deep-research-mcp .

# Run container
docker run -p 8000:8000 -e GEMINI_API_KEY=your_api_key deep-research-mcp
```

### 3. Docker Compose
```bash
# Set environment variables in .env file
echo "GEMINI_API_KEY=your_api_key" > .env

# Deploy with Docker Compose
docker-compose up -d
```

### 4. Production Deployment
- Kubernetes deployment with proper resource limits
- Load balancer configuration for high availability
- Persistent storage for logs and temporary files
- Auto-scaling based on request volume

## Client Integration Guide

### 1. FastMCP Client
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

### 2. Claude Desktop Integration
```json
{
  "mcpServers": {
    "deep-research": {
      "url": "http://localhost:8000/mcp/"
    }
  }
}
```

### 3. Cursor IDE Integration
```json
{
  "mcpServers": {
    "deep-research": {
      "url": "http://localhost:8000/mcp/"
    }
  }
}
```

## Success Metrics

### 1. Functional Requirements
- ✅ Research tool accepts topic and returns comprehensive report
- ✅ Progress streaming works with real-time updates
- ✅ Docker container runs reliably with health checks
- ✅ HTTP transport accessible from external clients

### 2. Performance Requirements
- Research completion time < 2 minutes for typical queries
- Support for 10+ concurrent research requests
- Container startup time < 30 seconds
- Memory usage < 2GB per instance

### 3. Integration Requirements
- ✅ Works with Claude Desktop (local and remote)
- ✅ Works with Cursor IDE
- ✅ Works with FastMCP client library
- ✅ Works with generic HTTP MCP clients

## Risk Mitigation

### 1. API Rate Limiting
- Implement exponential backoff for Google Search API
- Add request queuing for high-concurrency scenarios
- Monitor API usage and quotas

### 2. Model Availability
- Implement fallback models for resilience
- Add circuit breaker patterns for model failures
- Cache successful responses when appropriate

### 3. Resource Management
- Implement proper timeout handling
- Add memory limits and cleanup procedures
- Monitor resource usage and implement alerts

## Future Enhancements

### 1. Advanced Features
- Support for file upload and document analysis
- Integration with additional search engines
- Custom search filters and parameters
- Research result caching and persistence

### 2. Scalability Improvements
- Redis-based caching for research results
- Distributed task queue for research operations
- Horizontal scaling with load balancing
- Database integration for persistent storage

### 3. Enhanced Client Support
- WebSocket support for real-time streaming
- GraphQL API for flexible queries
- REST API endpoints for non-MCP clients
- SDK libraries for popular programming languages

## Conclusion

This comprehensive plan provides a roadmap for transforming the existing LangGraph deep research agent into a production-ready MCP server. The implementation will provide a powerful research tool that can be integrated into various AI applications and workflows while maintaining the sophistication and reliability of the original agent.

The phased approach ensures systematic development and testing, while the containerization strategy enables flexible deployment options from local development to production environments. The focus on observability, security, and client integration ensures the solution will be robust and user-friendly. 