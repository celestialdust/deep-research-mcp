#!/usr/bin/env python3
"""
Example client for the Deep Research MCP Server.

This script demonstrates how to use the MCP server for research.
"""

import asyncio
import os
from typing import Dict, Any

# Try to import FastMCP client
try:
    from fastmcp import Client
    HAS_FASTMCP = True
except ImportError:
    HAS_FASTMCP = False
    print("Warning: FastMCP client not available. Install with: pip install fastmcp")

# Alternative HTTP client for demonstration
import json
import aiohttp

async def test_with_fastmcp_client():
    """Test the MCP server using FastMCP client."""
    if not HAS_FASTMCP:
        print("FastMCP client not available")
        return False
    
    print("Testing with FastMCP client...")
    
    try:
        # Connect to the MCP server
        client = Client("http://localhost:8000/mcp/")
        
        async with client:
            # Test the research tool
            result = await client.call_tool("research", {
                "topic": "What are the latest developments in AI research in 2024?",
                "max_research_loops": 2,
                "initial_search_query_count": 3
            })
            
            print("Research completed successfully!")
            
            # CORRECT WAY: Access the data attribute which contains the parsed JSON
            data = result.data  # This is a dictionary
            
            print(f"Report length: {len(data['report'])} characters")
            print(f"Sources found: {len(data['sources'])}")
            print(f"Execution time: {data['metadata']['execution_time']}s")
            
            # Print a snippet of the report
            if data['report']:
                print("\nReport snippet:")
                print("-" * 40)
                print(data['report'][:500] + "..." if len(data['report']) > 500 else data['report'])
                print("-" * 40)
            
            return True
            
    except Exception as e:
        print(f"FastMCP client test failed: {e}")
        return False

async def test_with_http_client():
    """Test the MCP server using direct HTTP client."""
    print("\nTesting with HTTP client...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test health endpoint
            async with session.get("http://localhost:8000/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"Health check passed: {health_data['status']}")
                else:
                    print(f"Health check failed: {response.status}")
                    return False
            
            # Test stats endpoint
            async with session.get("http://localhost:8000/stats") as response:
                if response.status == 200:
                    stats_data = await response.json()
                    print(f"Server stats: {stats_data}")
                else:
                    print(f"Warning: Stats endpoint returned: {response.status}")
            
            return True
            
    except Exception as e:
        print(f"HTTP client test failed: {e}")
        return False

async def demonstrate_research_variations():
    """Demonstrate different research configurations."""
    if not HAS_FASTMCP:
        print("FastMCP client required for research demonstrations")
        return False
    
    print("\nDemonstrating research variations...")
    
    research_configs = [
        {
            "name": "Quick Research",
            "config": {
                "topic": "What is quantum computing?",
                "max_research_loops": 1,
                "initial_search_query_count": 2
            }
        },
        {
            "name": "Deep Research",
            "config": {
                "topic": "Impact of artificial intelligence on healthcare",
                "max_research_loops": 3,
                "initial_search_query_count": 4
            }
        },
        {
            "name": "Technical Research",
            "config": {
                "topic": "How do transformer models work in natural language processing?",
                "max_research_loops": 2,
                "initial_search_query_count": 3,
                "reasoning_model": "gemini-2.5-pro"
            }
        }
    ]
    
    client = Client("http://localhost:8000/mcp/")
    
    try:
        async with client:
            for demo in research_configs:
                print(f"\n{demo['name']}:")
                print(f"   Topic: {demo['config']['topic']}")
                print(f"   Config: {demo['config']}")
                
                try:
                    result = await client.call_tool("research", demo['config'])
                    # CORRECT WAY: Access the data attribute
                    data = result.data
                    print(f"   Completed in {data['metadata']['execution_time']}s")
                    print(f"   {data['metadata']['total_sources']} sources, {data['metadata']['queries_executed']} queries")
                except Exception as e:
                    print(f"   Failed: {e}")
                
                # Small delay between requests
                await asyncio.sleep(1)
        
        return True
        
    except Exception as e:
        print(f"Research demonstration failed: {e}")
        return False

async def main():
    """Main function to run all tests."""
    print("Deep Research MCP Server Client Examples")
    print("=" * 50)
    
    # Check if server is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health") as response:
                if response.status != 200:
                    print("MCP server is not running or not healthy")
                    print("   Start the server with: python -m src.mcp_server")
                    return
    except Exception:
        print("Cannot connect to MCP server")
        print("   Make sure the server is running on localhost:8000")
        print("   Start with: python -m src.mcp_server")
        return
    
    print("MCP server is running")
    
    # Run tests
    tests = [
        test_with_http_client,
        test_with_fastmcp_client,
        # demonstrate_research_variations,  # Commented out as it requires API key
    ]
    
    for test in tests:
        try:
            await test()
        except Exception as e:
            print(f"Test {test.__name__} failed: {e}")
        
        print()  # Add spacing between tests
    
    print("Client examples completed!")
    print("\nTo use the research tool with real API keys:")
    print("   1. Set GEMINI_API_KEY environment variable")
    print("   2. Start the server: python -m src.mcp_server")
    print("   3. Use FastMCP client or HTTP requests to call the research tool")

if __name__ == "__main__":
    asyncio.run(main()) 