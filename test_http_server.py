#!/usr/bin/env python3
"""
Test the FastMCP HTTP server
"""

import json
import requests

def test_list_tools():
    """Test listing tools from the MCP server"""
    print("Testing FastMCP HTTP server at http://localhost:8000/mcp\n")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }

    try:
        # Step 1: Initialize the MCP session
        print("Step 1: Initializing MCP session...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }

        init_response = requests.post(
            "http://localhost:8000/mcp",
            json=init_request,
            headers=headers,
            timeout=5
        )

        print(f"   Status: {init_response.status_code}")

        if init_response.status_code != 200:
            print(f"   ❌ Initialization failed: {init_response.text}")
            return False

        # Extract session ID from response headers
        session_id = init_response.headers.get("mcp-session-id")
        print(f"   ✅ Session ID: {session_id}\n")

        # Add session ID to headers for subsequent requests
        headers["mcp-session-id"] = session_id

        # Step 2: Send initialized notification
        print("Step 2: Sending initialized notification...")
        notif_request = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }

        requests.post(
            "http://localhost:8000/mcp",
            json=notif_request,
            headers=headers,
            timeout=5
        )
        print("   ✅ Notification sent\n")

        # Step 3: List tools
        print("Step 3: Listing tools...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }

        tools_response = requests.post(
            "http://localhost:8000/mcp",
            json=tools_request,
            headers=headers,
            timeout=5
        )

        print(f"   Status: {tools_response.status_code}")
        print(f"   Content-Type: {tools_response.headers.get('content-type')}")
        print(f"   Response text (first 500 chars): {tools_response.text[:500]}\n")

        if tools_response.status_code == 200:
            # Try to parse SSE format
            if "text/event-stream" in tools_response.headers.get('content-type', ''):
                # Parse SSE response
                lines = tools_response.text.strip().split('\n')
                for line in lines:
                    if line.startswith('data: '):
                        data = json.loads(line[6:])  # Remove 'data: ' prefix
                        break
            else:
                data = tools_response.json()

            print("✅ Server is running!\n")

            # Count tools
            if "result" in data and "tools" in data["result"]:
                tools = data["result"]["tools"]
                print(f"📦 Total tools available: {len(tools)}")

                # Find Blockza event tools
                event_tools = [t for t in tools if "event" in t["name"].lower()]
                print(f"🎯 Blockza event tools: {len(event_tools)}")

                print("\n📋 Available Blockza Event Tools:")
                for tool in event_tools:
                    print(f"   • {tool['name']}: {tool['description']}")

                return True
        else:
            print(f"❌ Error: {tools_response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_list_tools()
    exit(0 if success else 1)
