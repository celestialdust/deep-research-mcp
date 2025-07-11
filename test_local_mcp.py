#!/usr/bin/env python3
"""
Simple test script to verify local MCP server functionality.
"""

import asyncio
import sys
from fastmcp import Client

async def test_mcp_server():
    """Test the MCP server locally."""
    print("🧪 Testing MCP Server Locally...")
    
    try:
        # Connect to local server
        client = Client("http://localhost:8000/mcp/")
        
        async with client:
            print("✅ Connected to MCP server")
            
            # List available tools
            try:
                tools = await client.list_tools()
                tool_names = [tool.name for tool in tools]
                print(f"📋 Available tools: {tool_names}")
                
                # Check if research tool exists
                research_tool = next((tool for tool in tools if tool.name == 'research'), None)
                if research_tool:
                    print("✅ Research tool found")
                    print(f"📖 Description: {getattr(research_tool, 'description', 'No description')}")
                else:
                    print("❌ Research tool not found")
                    return False
                    
            except Exception as e:
                print(f"❌ Failed to list tools: {e}")
                return False
            
            # Test research tool with a simple query
            print("\n🔍 Testing research tool with simple query...")
            try:
                result = await client.call_tool("research", {
                    "topic": "What is FastMCP?",
                    "max_research_loops": 1,
                    "initial_search_query_count": 1
                })
                
                print("✅ Research tool executed successfully")
                
                # Access the content of the result
                if hasattr(result, 'content'):
                    content = result.content
                    print(f"📊 Result type: {type(content)}")
                    
                    if isinstance(content, list) and len(content) > 0:
                        # Get the first content item (usually text)
                        first_content = content[0]
                        if hasattr(first_content, 'text'):
                            # Parse the JSON content
                            import json
                            try:
                                data = json.loads(first_content.text)
                                print(f"📊 Result keys: {list(data.keys())}")
                                
                                if 'report' in data:
                                    print(f"📄 Report length: {len(data['report'])} characters")
                                if 'sources' in data:
                                    print(f"🔗 Sources found: {len(data['sources'])}")
                                if 'metadata' in data:
                                    print(f"⏱️ Execution time: {data['metadata'].get('execution_time', 'unknown')}")
                            except json.JSONDecodeError:
                                print(f"📝 Raw content: {first_content.text[:200]}...")
                    else:
                        print(f"📝 Raw result content: {str(content)[:200]}...")
                else:
                    print(f"📝 Raw result: {str(result)[:200]}...")
                
                return True
                
            except Exception as e:
                print(f"❌ Research tool test failed: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Failed to connect to MCP server: {e}")
        print("💡 Make sure the server is running on http://localhost:8000")
        return False

async def main():
    """Main test function."""
    success = await test_mcp_server()
    
    if success:
        print("\n🎉 All tests passed! The MCP server is working correctly.")
        return 0
    else:
        print("\n💥 Tests failed. Please check the server and try again.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 