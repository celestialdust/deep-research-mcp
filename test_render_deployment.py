#!/usr/bin/env python3
"""
Test script to verify Deep Research MCP Server deployment on Render.

Usage:
    python test_render_deployment.py https://your-service-name.onrender.com
"""

import asyncio
import sys
import json
import time
from typing import Optional
import argparse
import traceback

try:
    import httpx
    from fastmcp import Client
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("pip install httpx fastmcp")
    sys.exit(1)

class RenderMCPTester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.health_url = f"{self.base_url}/health"
        self.mcp_url = f"{self.base_url}/mcp/"
        self.stats_url = f"{self.base_url}/stats"
        
    async def test_health_check(self) -> bool:
        """Test the health check endpoint."""
        print("🔍 Testing health check endpoint...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.health_url)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Health check passed")
                    print(f"   Status: {data.get('status')}")
                    print(f"   Service: {data.get('service')}")
                    print(f"   Version: {data.get('version')}")
                    print(f"   Agent Status: {data.get('agent_status')}")
                    return True
                else:
                    print(f"❌ Health check failed with status {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    async def test_stats_endpoint(self) -> bool:
        """Test the stats endpoint."""
        print("\n📊 Testing stats endpoint...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.stats_url)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Stats endpoint accessible")
                    print(f"   Server stats available: {'server_stats' in data}")
                    print(f"   Config available: {'config' in data}")
                    return True
                else:
                    print(f"❌ Stats endpoint failed with status {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Stats endpoint error: {e}")
            return False
    
    async def test_mcp_connection(self) -> bool:
        """Test basic MCP connection."""
        print("\n🔗 Testing MCP connection...")
        
        try:
            client = Client(self.mcp_url)
            async with client:
                print("✅ MCP connection successful")
                return True
                
        except Exception as e:
            print(f"❌ MCP connection failed: {e}")
            return False
    
    async def test_mcp_tools(self) -> bool:
        """Test MCP tools listing."""
        print("\n🛠️ Testing MCP tools...")
        
        try:
            client = Client(self.mcp_url)
            async with client:
                tools = await client.list_tools()
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"   - {tool.name}: {tool.description}")
                return len(tools) > 0
                
        except Exception as e:
            print(f"❌ MCP tools test failed: {e}")
            return False
    
    async def test_research_tool(self, quick_test: bool = True) -> bool:
        """Test the research tool with a simple query."""
        print("\n🔬 Testing research tool...")
        
        if quick_test:
            print("   Running quick test (minimal research)...")
            topic = "What is Python?"
            max_loops = 1
            query_count = 1
        else:
            print("   Running full test (comprehensive research)...")
            topic = "What are the latest developments in artificial intelligence?"
            max_loops = 2
            query_count = 3
        
        try:
            client = Client(self.mcp_url)
            async with client:
                print(f"   📝 Research topic: {topic}")
                print(f"   ⏱️ Starting research...")
                
                start_time = time.time()
                
                result = await client.call_tool("research", {
                    "topic": topic,
                    "max_research_loops": max_loops,
                    "initial_search_query_count": query_count
                })
                
                end_time = time.time()
                duration = end_time - start_time
                
                if result and len(result) > 0:
                    # Extract the result data
                    result_data = result[0].text if hasattr(result[0], 'text') else str(result[0])
                    
                    try:
                        # Try to parse as JSON
                        parsed_result = json.loads(result_data)
                        report = parsed_result.get('report', '')
                        sources = parsed_result.get('sources', [])
                        metadata = parsed_result.get('metadata', {})
                        
                        print(f"✅ Research completed successfully!")
                        print(f"   📄 Report length: {len(report)} characters")
                        print(f"   🔗 Sources found: {len(sources)}")
                        print(f"   ⏱️ Duration: {duration:.2f} seconds")
                        print(f"   📊 Metadata: {metadata}")
                        
                        if quick_test:
                            print(f"   📝 Report preview: {report[:200]}...")
                        
                        return True
                        
                    except json.JSONDecodeError:
                        print(f"✅ Research completed (raw result)")
                        print(f"   📄 Result length: {len(result_data)} characters")
                        print(f"   ⏱️ Duration: {duration:.2f} seconds")
                        return True
                        
                else:
                    print(f"❌ Research returned empty result")
                    return False
                    
        except Exception as e:
            print(f"❌ Research tool test failed: {e}")
            traceback.print_exc()
            return False
    
    async def run_all_tests(self, quick_test: bool = True) -> bool:
        """Run all tests."""
        print(f"🚀 Testing Deep Research MCP Server at: {self.base_url}")
        print(f"{'=' * 60}")
        
        results = []
        
        # Test health check
        results.append(await self.test_health_check())
        
        # Test stats endpoint
        results.append(await self.test_stats_endpoint())
        
        # Test MCP connection
        results.append(await self.test_mcp_connection())
        
        # Test MCP tools
        results.append(await self.test_mcp_tools())
        
        # Test research tool
        results.append(await self.test_research_tool(quick_test))
        
        # Summary
        print(f"\n{'=' * 60}")
        passed = sum(results)
        total = len(results)
        
        if passed == total:
            print(f"🎉 All tests passed! ({passed}/{total})")
            print(f"✅ Your MCP server is working correctly!")
            return True
        else:
            print(f"❌ Some tests failed ({passed}/{total})")
            print(f"🔧 Check the logs above for details")
            return False

def main():
    parser = argparse.ArgumentParser(description='Test Deep Research MCP Server deployment on Render')
    parser.add_argument('url', help='Base URL of your deployed server (e.g., https://your-service.onrender.com)')
    parser.add_argument('--full-test', action='store_true', help='Run full research test (slower but comprehensive)')
    parser.add_argument('--quick', action='store_true', help='Run quick test only (default)')
    
    args = parser.parse_args()
    
    # Validate URL
    if not args.url.startswith(('http://', 'https://')):
        print("❌ Invalid URL. Must start with http:// or https://")
        sys.exit(1)
    
    # Determine test mode
    quick_test = not args.full_test
    
    # Run tests
    tester = RenderMCPTester(args.url)
    
    try:
        success = asyncio.run(tester.run_all_tests(quick_test))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test runner error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 