"""
Configuration management for the MCP server.

This module handles environment variable management, model configuration,
and validation for required credentials.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class MCPServerConfig(BaseModel):
    """Configuration for the MCP server."""
    
    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # API Keys
    gemini_api_key: str = Field(..., description="Google Gemini API key")
    
    # Research Agent Configuration
    default_max_research_loops: int = Field(default=2, description="Default maximum research loops")
    default_initial_search_query_count: int = Field(default=3, description="Default initial search query count")
    default_reasoning_model: str = Field(default="gemini-2.5-pro", description="Default reasoning model")
    
    # Model Configuration
    query_generator_model: str = Field(default="gemini-2.0-flash", description="Query generator model")
    reflection_model: str = Field(default="gemini-2.5-flash", description="Reflection model")
    answer_model: str = Field(default="gemini-2.5-pro", description="Answer model")
    
    # Timeout and Rate Limiting
    request_timeout: int = Field(default=300, description="Request timeout in seconds")
    max_concurrent_requests: int = Field(default=10, description="Maximum concurrent requests")
    
    @field_validator('gemini_api_key')
    @classmethod
    def validate_gemini_api_key(cls, v):
        if not v:
            raise ValueError("GEMINI_API_KEY is required")
        return v
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {valid_levels}")
        return v.upper()
    
    @field_validator('port')
    @classmethod
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v


def get_config() -> MCPServerConfig:
    """Get the server configuration from environment variables."""
    return MCPServerConfig(
        host=os.getenv("MCP_SERVER_HOST", "0.0.0.0"),
        port=int(os.getenv("MCP_SERVER_PORT", "8000")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        default_max_research_loops=int(os.getenv("DEFAULT_MAX_RESEARCH_LOOPS", "2")),
        default_initial_search_query_count=int(os.getenv("DEFAULT_INITIAL_SEARCH_QUERY_COUNT", "3")),
        default_reasoning_model=os.getenv("DEFAULT_REASONING_MODEL", "gemini-2.5-pro"),
        query_generator_model=os.getenv("QUERY_GENERATOR_MODEL", "gemini-2.0-flash"),
        reflection_model=os.getenv("REFLECTION_MODEL", "gemini-2.5-flash"),
        answer_model=os.getenv("ANSWER_MODEL", "gemini-2.5-pro"),
        request_timeout=int(os.getenv("REQUEST_TIMEOUT", "300")),
        max_concurrent_requests=int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
    )


def validate_config() -> None:
    """Validate the configuration and raise errors if invalid."""
    try:
        config = get_config()
        print(f"Configuration validated successfully")
        print(f"   - Server: {config.host}:{config.port}")
        print(f"   - Log Level: {config.log_level}")
        print(f"   - Default Model: {config.default_reasoning_model}")
        print(f"   - Max Concurrent Requests: {config.max_concurrent_requests}")
    except Exception as e:
        print(f"Configuration validation failed: {e}")
        raise 