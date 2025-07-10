#!/usr/bin/env python3
"""
Simple test script for the MCP server.

This script tests basic functionality without requiring API keys.
"""

import os
import sys
import asyncio
from unittest.mock import patch

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_server_imports():
    """Test that all server components can be imported."""
    print("🧪 Testing server imports...")
    
    try:
        from mcp_server.config import MCPServerConfig
        from mcp_server.agent_adapter import LangGraphAgentAdapter, ProgressCallback
        from mcp_server.utils import validate_research_parameters, sanitize_topic
        print("✅ All imports successful")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    return True

async def test_configuration():
    """Test configuration loading."""
    print("\n🧪 Testing configuration...")
    
    try:
        from mcp_server.config import MCPServerConfig
        
        # Test with mock environment variables
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'test_key',
            'MCP_SERVER_HOST': '127.0.0.1',
            'MCP_SERVER_PORT': '8000',
            'LOG_LEVEL': 'INFO'
        }):
            config = MCPServerConfig(
                gemini_api_key="test_key",
                host="127.0.0.1",
                port=8000,
                log_level="INFO"
            )
            print(f"✅ Configuration created: {config.host}:{config.port}")
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False
    
    return True

async def test_utilities():
    """Test utility functions."""
    print("\n🧪 Testing utility functions...")
    
    try:
        from mcp_server.utils import (
            validate_research_parameters,
            sanitize_topic,
            format_execution_time,
            create_error_response
        )
        
        # Test topic sanitization
        topic = sanitize_topic("This is a test topic")
        assert topic == "This is a test topic"
        print("✅ Topic sanitization works")
        
        # Test execution time formatting
        formatted_time = format_execution_time(65.5)
        assert "1m" in formatted_time
        print("✅ Time formatting works")
        
        # Test parameter validation
        params = validate_research_parameters(
            topic="Test topic",
            max_research_loops=2,
            initial_search_query_count=3,
            reasoning_model="gemini-2.5-pro"
        )
        assert params["topic"] == "Test topic"
        print("✅ Parameter validation works")
        
        # Test error response creation
        error_response = create_error_response(ValueError("Test error"))
        assert "error" in error_response
        print("✅ Error response creation works")
        
    except Exception as e:
        print(f"❌ Utility test failed: {e}")
        return False
    
    return True

async def test_progress_callback():
    """Test progress callback functionality."""
    print("\n🧪 Testing progress callback...")
    
    try:
        from mcp_server.agent_adapter import ProgressCallback
        
        messages = []
        def collect_messages(msg):
            messages.append(msg)
        
        callback = ProgressCallback(collect_messages)
        
        await callback.info("Test info message")
        await callback.debug("Test debug message")
        await callback.warning("Test warning message")
        await callback.error("Test error message")
        
        assert len(messages) == 4
        assert "[INFO]" in messages[0]
        assert "[DEBUG]" in messages[1]
        assert "[WARNING]" in messages[2]
        assert "[ERROR]" in messages[3]
        
        print("✅ Progress callback works")
        
    except Exception as e:
        print(f"❌ Progress callback test failed: {e}")
        return False
    
    return True

async def main():
    """Run all tests."""
    print("🚀 Starting MCP Server Tests")
    print("=" * 50)
    
    tests = [
        test_server_imports,
        test_configuration,
        test_utilities,
        test_progress_callback
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("❌ Some tests failed")
        sys.exit(1)
    else:
        print("✅ All tests passed!")
        print("\n🎉 MCP Server is ready to use!")
        print("To start the server, run:")
        print("  python -m src.mcp_server")
        print("  (Make sure to set GEMINI_API_KEY environment variable)")

if __name__ == "__main__":
    asyncio.run(main()) 