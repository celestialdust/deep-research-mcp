"""
FastMCP server for the Deep Research Agent.

This module implements the main MCP server that exposes the LangGraph
deep research agent as an MCP tool with progress streaming and health monitoring.
"""

import os
import logging
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastmcp import FastMCP, Context
from fastmcp.server import MCP

from .config import Config
from .agent_adapter import AgentAdapter
from .utils import setup_logging, validate_research_params

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

# Load configuration
config = Config()

# Initialize agent adapter
agent_adapter = AgentAdapter(config)

@asynccontextmanager
async def lifespan(app: FastMCP):
    """Startup and shutdown events for the MCP server."""
    logger.info("🚀 Starting Deep Research MCP Server...")
    logger.info(f"📊 Server configuration: {config.get_server_info()}")
    
    # Initialize the agent adapter
    await agent_adapter.initialize()
    
    yield
    
    # Cleanup
    await agent_adapter.cleanup()
    logger.info("✅ Deep Research MCP Server shutdown complete")

# Create FastMCP server - Updated for Render compatibility
mcp = FastMCP("Deep Research Agent")

# Add the lifespan context manager
mcp.app.router.lifespan_context = lifespan

@mcp.tool()
async def research(
    topic: str,
    max_research_loops: int = 2,
    initial_search_query_count: int = 3,
    reasoning_model: str = "gemini-2.5-pro",
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Conduct comprehensive web research on a given topic using LangGraph agent.
    
    Args:
        topic: The research topic or question (required)
        max_research_loops: Maximum number of research iterations (default: 2)
        initial_search_query_count: Number of initial search queries (default: 3)
        reasoning_model: Model for final answer generation (default: gemini-2.5-pro)
        
    Returns:
        Dictionary containing:
        - report: Full research report with citations
        - sources: List of source URLs
        - metadata: Execution statistics and information
    """
    if ctx:
        ctx.info(f"🔍 Starting research on topic: {topic}")
    
    # Validate parameters
    try:
        validate_research_params(
            topic=topic,
            max_research_loops=max_research_loops,
            initial_search_query_count=initial_search_query_count,
            reasoning_model=reasoning_model
        )
    except ValueError as e:
        if ctx:
            ctx.error(f"❌ Invalid parameters: {str(e)}")
        raise
    
    # Execute research
    try:
        if ctx:
            ctx.info("🚀 Initializing research agent...")
        
        result = await agent_adapter.execute_research(
            topic=topic,
            max_research_loops=max_research_loops,
            initial_search_query_count=initial_search_query_count,
            reasoning_model=reasoning_model,
            progress_callback=lambda msg: ctx.info(f"📊 {msg}") if ctx else None
        )
        
        if ctx:
            ctx.info(f"✅ Research completed successfully!")
            ctx.info(f"📄 Report length: {len(result['report'])} characters")
            ctx.info(f"🔗 Sources found: {len(result['sources'])}")
            ctx.info(f"⏱️ Execution time: {result['metadata']['execution_time']:.2f}s")
        
        return result
        
    except Exception as e:
        error_msg = f"Research failed: {str(e)}"
        if ctx:
            ctx.error(f"❌ {error_msg}")
        logger.error(error_msg, exc_info=True)
        raise

# Health check endpoint for Render
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint for monitoring."""
    from starlette.responses import JSONResponse
    
    return JSONResponse({
        "status": "healthy",
        "service": "Deep Research MCP Server",
        "version": "1.0.0",
        "agent_status": "ready" if agent_adapter.is_ready() else "initializing"
    })

# Stats endpoint
@mcp.custom_route("/stats", methods=["GET"])
async def stats(request):
    """Get server statistics."""
    from starlette.responses import JSONResponse
    
    stats = await agent_adapter.get_stats()
    return JSONResponse({
        "server_stats": stats,
        "config": config.get_server_info()
    })

# Main execution for Render deployment
if __name__ == "__main__":
    # Use environment variables for Render deployment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"🌐 Starting server on {host}:{port}")
    logger.info(f"🔑 Using model: {config.reasoning_model}")
    
    # Run with streamable HTTP transport for Render
    mcp.run(
        transport="http",
        host=host,
        port=port,
        path="/mcp/",
        log_level="info"
    ) 