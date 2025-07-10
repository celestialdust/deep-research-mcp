"""
FastMCP server for the Deep Research Agent.

This module implements the main MCP server that exposes the LangGraph
deep research agent as an MCP tool with progress streaming and health monitoring.
"""

import asyncio
import logging
import sys
from typing import Dict, Any, Optional
from starlette.requests import Request
from starlette.responses import JSONResponse

from fastmcp import FastMCP, Context
from fastmcp.server.server import HealthCheckResult

from .config import get_config, validate_config, MCPServerConfig
from .agent_adapter import LangGraphAgentAdapter, ProgressCallback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
config: Optional[MCPServerConfig] = None
agent_adapter: Optional[LangGraphAgentAdapter] = None
mcp: Optional[FastMCP] = None


def create_mcp_server() -> FastMCP:
    """Create and configure the FastMCP server."""
    global config, agent_adapter, mcp
    
    # Load and validate configuration
    try:
        config = get_config()
        validate_config()
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise
    
    # Create agent adapter
    agent_adapter = LangGraphAgentAdapter(config)
    
    # Create FastMCP server
    mcp = FastMCP(
        name="Deep Research Agent",
        description="A sophisticated research agent that conducts comprehensive web research using LangGraph and Google Search API"
    )
    
    @mcp.tool
    async def research(
        topic: str,
        max_research_loops: int = None,
        initial_search_query_count: int = None,
        reasoning_model: str = None,
        ctx: Context = None
    ) -> Dict[str, Any]:
        """
        Conduct comprehensive web research on a given topic.
        
        This tool uses a sophisticated LangGraph agent to perform multi-step research:
        1. Generates diverse search queries based on the topic
        2. Conducts web research using Google Search API
        3. Analyzes results and identifies knowledge gaps
        4. Performs additional research loops if needed
        5. Synthesizes findings into a comprehensive report
        
        Args:
            topic: The research topic or question to investigate
            max_research_loops: Maximum number of research iterations (default: 2)
            initial_search_query_count: Number of initial search queries (default: 3)
            reasoning_model: Model for final answer generation (default: gemini-2.5-pro)
            
        Returns:
            Dictionary containing:
            - report: Full research report with citations
            - sources: List of source URLs used
            - metadata: Execution statistics and configuration
            
        Raises:
            ValueError: If input validation fails
            RuntimeError: If research execution fails
        """
        if not agent_adapter:
            raise RuntimeError("Agent adapter not initialized")
        
        # Create progress callback for MCP context logging
        progress_callback = None
        if ctx:
            progress_callback = ProgressCallback(
                callback_fn=lambda msg: asyncio.create_task(ctx.info(msg))
            )
        
        try:
            # Use config defaults if not provided
            max_research_loops = max_research_loops or config.default_max_research_loops
            initial_search_query_count = initial_search_query_count or config.default_initial_search_query_count  
            reasoning_model = reasoning_model or config.default_reasoning_model
            
            if ctx:
                await ctx.info(f"🔍 Starting research on: {topic[:100]}...")
                await ctx.debug(f"Configuration: loops={max_research_loops}, queries={initial_search_query_count}, model={reasoning_model}")
            
            # Execute research
            result = await agent_adapter.research(
                topic=topic,
                max_research_loops=max_research_loops,
                initial_search_query_count=initial_search_query_count,
                reasoning_model=reasoning_model,
                progress_callback=progress_callback
            )
            
            if ctx:
                await ctx.info(f"✅ Research completed successfully!")
                await ctx.info(f"📊 Generated {result.metadata['total_sources']} sources in {result.metadata['execution_time']}s")
            
            return result.to_dict()
            
        except ValueError as e:
            if ctx:
                await ctx.error(f"❌ Input validation failed: {str(e)}")
            raise
        except Exception as e:
            if ctx:
                await ctx.error(f"❌ Research failed: {str(e)}")
            raise RuntimeError(f"Research execution failed: {str(e)}") from e
    
    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request: Request) -> JSONResponse:
        """Health check endpoint for the MCP server."""
        try:
            if not agent_adapter:
                return JSONResponse(
                    status_code=503,
                    content={
                        "status": "unhealthy",
                        "error": "Agent adapter not initialized",
                        "service": "Deep Research Agent MCP Server"
                    }
                )
            
            # Check agent health
            agent_health = await agent_adapter.health_check()
            
            # Overall health status
            overall_health = {
                "status": "healthy" if agent_health["status"] == "healthy" else "unhealthy",
                "service": "Deep Research Agent MCP Server",
                "version": "0.1.0",
                "agent": agent_health,
                "config": {
                    "max_research_loops": config.default_max_research_loops,
                    "initial_search_query_count": config.default_initial_search_query_count,
                    "reasoning_model": config.default_reasoning_model,
                    "max_concurrent_requests": config.max_concurrent_requests
                }
            }
            
            status_code = 200 if overall_health["status"] == "healthy" else 503
            return JSONResponse(status_code=status_code, content=overall_health)
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "error": str(e),
                    "service": "Deep Research Agent MCP Server"
                }
            )
    
    @mcp.custom_route("/stats", methods=["GET"])
    async def get_stats(request: Request) -> JSONResponse:
        """Get server statistics."""
        try:
            if not agent_adapter:
                return JSONResponse(
                    status_code=503,
                    content={"error": "Agent adapter not initialized"}
                )
            
            stats = agent_adapter.get_stats()
            return JSONResponse(content=stats)
            
        except Exception as e:
            logger.error(f"Stats request failed: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": str(e)}
            )
    
    return mcp


def main():
    """Main entry point for the MCP server."""
    logger.info("🚀 Starting Deep Research Agent MCP Server...")
    
    try:
        # Create and configure server
        server = create_mcp_server()
        
        # Start server
        logger.info(f"🌐 Server starting on {config.host}:{config.port}")
        logger.info(f"📋 Log level: {config.log_level}")
        logger.info(f"🔧 Max concurrent requests: {config.max_concurrent_requests}")
        
        server.run(
            transport="http",
            host=config.host,
            port=config.port,
            path="/mcp/",
            log_level=config.log_level.lower()
        )
        
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
    except Exception as e:
        logger.error(f"💥 Server failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 