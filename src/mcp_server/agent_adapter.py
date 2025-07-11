"""
Agent adapter for integrating LangGraph research agent with MCP.

This module provides an async wrapper for the existing LangGraph agent,
handling state management, progress streaming, and error handling.
"""

import asyncio
import time
from typing import Dict, List, Optional, Callable, Any
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig

from agent.graph import graph
from agent.configuration import Configuration
from .config import Config


class ProgressCallback:
    """Callback interface for progress updates."""
    
    def __init__(self, callback_fn: Optional[Callable[[str], None]] = None):
        self.callback_fn = callback_fn
    
    async def info(self, message: str):
        """Send info-level progress update."""
        if self.callback_fn:
            self.callback_fn(f"[INFO] {message}")
    
    async def debug(self, message: str):
        """Send debug-level progress update."""
        if self.callback_fn:
            self.callback_fn(f"[DEBUG] {message}")
    
    async def warning(self, message: str):
        """Send warning-level progress update."""
        if self.callback_fn:
            self.callback_fn(f"[WARNING] {message}")
    
    async def error(self, message: str):
        """Send error-level progress update."""
        if self.callback_fn:
            self.callback_fn(f"[ERROR] {message}")


class ResearchResult:
    """Structured result from the research agent."""
    
    def __init__(
        self, 
        report: str, 
        sources: List[Dict], 
        metadata: Dict[str, Any]
    ):
        self.report = report
        self.sources = sources
        self.metadata = metadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for MCP response."""
        return {
            "report": self.report,
            "sources": [source.get("value", "") for source in self.sources],
            "metadata": self.metadata
        }


class LangGraphAgentAdapter:
    """Adapter for the LangGraph research agent."""
    
    def __init__(self, config: Config):
        self.config = config
        self.agent = graph  # The compiled LangGraph agent
        self._request_count = 0
        self._active_requests = 0
        self._lock = asyncio.Lock()
    
    async def research(
        self,
        topic: str,
        max_research_loops: Optional[int] = None,
        initial_search_query_count: Optional[int] = None,
        reasoning_model: Optional[str] = None,
        progress_callback: Optional[ProgressCallback] = None
    ) -> ResearchResult:
        """
        Execute research using the LangGraph agent.
        
        Args:
            topic: The research topic or question
            max_research_loops: Maximum number of research iterations
            initial_search_query_count: Number of initial search queries
            reasoning_model: Model for final answer generation
            progress_callback: Callback for progress updates
            
        Returns:
            ResearchResult with the research report and metadata
            
        Raises:
            ValueError: If input validation fails
            RuntimeError: If agent execution fails
            asyncio.TimeoutError: If request times out
        """
        start_time = time.time()
        
        # Validate input
        if not topic or not topic.strip():
            raise ValueError("Research topic cannot be empty")
        
        if len(topic) > 5000:
            raise ValueError("Research topic too long (max 5000 characters)")
        
        # Use defaults from config if not provided
        max_research_loops = max_research_loops or self.config.default_max_research_loops
        initial_search_query_count = initial_search_query_count or self.config.default_initial_search_query_count
        reasoning_model = reasoning_model or self.config.default_reasoning_model
        
        # Check rate limiting
        async with self._lock:
            if self._active_requests >= self.config.max_concurrent_requests:
                raise RuntimeError(f"Too many concurrent requests (max: {self.config.max_concurrent_requests})")
            self._active_requests += 1
            self._request_count += 1
        
        try:
            if progress_callback:
                await progress_callback.info(f"Starting research on: {topic[:100]}...")
                await progress_callback.debug(f"Config: loops={max_research_loops}, queries={initial_search_query_count}, model={reasoning_model}")
            
            # Prepare the state for the LangGraph agent
            initial_state = {
                "messages": [HumanMessage(content=topic)],
                "max_research_loops": max_research_loops,
                "initial_search_query_count": initial_search_query_count,
                "reasoning_model": reasoning_model,
            }
            
            # Create configuration for the agent
            agent_config = RunnableConfig(
                configurable={
                    "max_research_loops": max_research_loops,
                    "number_of_initial_queries": initial_search_query_count,
                    "query_generator_model": self.config.query_generator_model,
                    "reflection_model": self.config.reflection_model,
                    "answer_model": reasoning_model,
                }
            )
            
            if progress_callback:
                await progress_callback.info("Executing research agent...")
            
            # Execute the agent with timeout
            try:
                result = await asyncio.wait_for(
                    self._run_agent_async(initial_state, agent_config),
                    timeout=self.config.request_timeout
                )
            except asyncio.TimeoutError:
                if progress_callback:
                    await progress_callback.error(f"Research timed out after {self.config.request_timeout} seconds")
                raise
            
            # Extract results
            messages = result.get("messages", [])
            sources = result.get("sources_gathered", [])
            
            if not messages:
                raise RuntimeError("No research results generated")
            
            # Get the final research report
            final_message = messages[-1]
            if isinstance(final_message, AIMessage):
                report = final_message.content
            else:
                report = str(final_message)
            
            # Calculate metadata
            execution_time = time.time() - start_time
            metadata = {
                "queries_executed": len(result.get("search_query", [])),
                "research_loops": result.get("research_loop_count", 0),
                "total_sources": len(sources),
                "execution_time": round(execution_time, 2),
                "reasoning_model": reasoning_model,
                "request_id": self._request_count
            }
            
            if progress_callback:
                await progress_callback.info(f"Research completed in {execution_time:.1f}s")
                await progress_callback.debug(f"Generated {len(sources)} sources, {metadata['queries_executed']} queries")
            
            return ResearchResult(
                report=report,
                sources=sources,
                metadata=metadata
            )
            
        except Exception as e:
            if progress_callback:
                await progress_callback.error(f"Research failed: {str(e)}")
            raise RuntimeError(f"Research execution failed: {str(e)}") from e
        
        finally:
            async with self._lock:
                self._active_requests -= 1
    
    async def _run_agent_async(self, initial_state: Dict, config: RunnableConfig) -> Dict:
        """Run the LangGraph agent in an async context."""
        # Since the LangGraph agent is synchronous, we need to run it in a thread
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.agent.invoke(initial_state, config)
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the agent and its dependencies."""
        try:
            # Simple test to verify the agent is working
            test_state = {
                "messages": [HumanMessage(content="test")],
                "max_research_loops": 1,
                "initial_search_query_count": 1,
            }
            
            # This is a minimal test - in a real scenario you might want to mock the API calls
            return {
                "status": "healthy",
                "active_requests": self._active_requests,
                "total_requests": self._request_count,
                "max_concurrent_requests": self.config.max_concurrent_requests,
                "agent_available": True
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "agent_available": False
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics."""
        return {
            "total_requests": self._request_count,
            "active_requests": self._active_requests,
            "max_concurrent_requests": self.config.max_concurrent_requests,
            "request_timeout": self.config.request_timeout
        } 