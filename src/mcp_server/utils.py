"""
Utility functions for the MCP server.

This module provides common utility functions used across
the MCP server implementation.
"""

import logging
import time
from typing import Any, Dict, Optional
from functools import wraps
from contextlib import asynccontextmanager


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Set up logging for the MCP server."""
    logger = logging.getLogger("mcp_server")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Create handler if it doesn't exist
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def sanitize_topic(topic: str) -> str:
    """Sanitize research topic for logging and display."""
    if not topic:
        return "Empty topic"
    
    # Truncate if too long
    max_length = 200
    if len(topic) > max_length:
        return topic[:max_length] + "..."
    
    return topic


def format_execution_time(seconds: float) -> str:
    """Format execution time in a human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{int(minutes)}m {remaining_seconds:.1f}s"
    else:
        hours = seconds // 3600
        remaining_seconds = seconds % 3600
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        return f"{int(hours)}h {int(minutes)}m {seconds:.1f}s"


def create_error_response(error: Exception, request_id: Optional[str] = None) -> Dict[str, Any]:
    """Create a standardized error response."""
    error_type = type(error).__name__
    error_message = str(error)
    
    response = {
        "error": {
            "type": error_type,
            "message": error_message,
            "timestamp": time.time()
        }
    }
    
    if request_id:
        response["error"]["request_id"] = request_id
    
    return response


def validate_research_parameters(
    topic: str,
    max_research_loops: Optional[int] = None,
    initial_search_query_count: Optional[int] = None,
    reasoning_model: Optional[str] = None
) -> Dict[str, Any]:
    """Validate research parameters and return sanitized values."""
    errors = []
    
    # Validate topic
    if not topic or not topic.strip():
        errors.append("Topic cannot be empty")
    elif len(topic) > 5000:
        errors.append("Topic too long (max 5000 characters)")
    
    # Validate max_research_loops
    if max_research_loops is not None:
        if not isinstance(max_research_loops, int) or max_research_loops < 1:
            errors.append("max_research_loops must be a positive integer")
        elif max_research_loops > 10:
            errors.append("max_research_loops cannot exceed 10")
    
    # Validate initial_search_query_count
    if initial_search_query_count is not None:
        if not isinstance(initial_search_query_count, int) or initial_search_query_count < 1:
            errors.append("initial_search_query_count must be a positive integer")
        elif initial_search_query_count > 10:
            errors.append("initial_search_query_count cannot exceed 10")
    
    # Validate reasoning_model
    valid_models = [
        "gemini-2.0-flash",
        "gemini-2.5-flash", 
        "gemini-2.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-pro"
    ]
    if reasoning_model is not None and reasoning_model not in valid_models:
        errors.append(f"Invalid reasoning_model. Must be one of: {', '.join(valid_models)}")
    
    if errors:
        raise ValueError(f"Validation errors: {'; '.join(errors)}")
    
    return {
        "topic": topic.strip(),
        "max_research_loops": max_research_loops,
        "initial_search_query_count": initial_search_query_count,
        "reasoning_model": reasoning_model
    }


def timing_decorator(func):
    """Decorator to measure function execution time."""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger = logging.getLogger("mcp_server")
            logger.debug(f"{func.__name__} executed in {format_execution_time(execution_time)}")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger = logging.getLogger("mcp_server")
            logger.error(f"{func.__name__} failed after {format_execution_time(execution_time)}: {str(e)}")
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger = logging.getLogger("mcp_server")
            logger.debug(f"{func.__name__} executed in {format_execution_time(execution_time)}")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger = logging.getLogger("mcp_server")
            logger.error(f"{func.__name__} failed after {format_execution_time(execution_time)}: {str(e)}")
            raise
    
    # Return appropriate wrapper based on whether function is async
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


@asynccontextmanager
async def request_context(request_id: str):
    """Context manager for request tracking."""
    logger = logging.getLogger("mcp_server")
    start_time = time.time()
    
    logger.info(f"Request {request_id} started")
    try:
        yield
        execution_time = time.time() - start_time
        logger.info(f"Request {request_id} completed in {format_execution_time(execution_time)}")
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Request {request_id} failed after {format_execution_time(execution_time)}: {str(e)}")
        raise


def extract_source_urls(sources: list) -> list:
    """Extract clean URLs from source objects."""
    urls = []
    for source in sources:
        if isinstance(source, dict):
            url = source.get("value") or source.get("url") or source.get("source")
            if url:
                urls.append(url)
        elif isinstance(source, str):
            urls.append(source)
    
    return list(set(urls))  # Remove duplicates


def create_research_summary(result: Dict[str, Any]) -> str:
    """Create a brief summary of research results."""
    metadata = result.get("metadata", {})
    
    summary_parts = []
    
    if "total_sources" in metadata:
        summary_parts.append(f"{metadata['total_sources']} sources")
    
    if "queries_executed" in metadata:
        summary_parts.append(f"{metadata['queries_executed']} queries")
    
    if "research_loops" in metadata:
        summary_parts.append(f"{metadata['research_loops']} research loops")
    
    if "execution_time" in metadata:
        summary_parts.append(f"{format_execution_time(metadata['execution_time'])}")
    
    if summary_parts:
        return f"Research completed: {', '.join(summary_parts)}"
    else:
        return "Research completed" 