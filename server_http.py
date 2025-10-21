#!/usr/bin/env python3
"""
Run FastMCP server in HTTP mode for testing
"""

import sys
sys.path.insert(0, '/Users/chetanmittal/Desktop/block/mcp/fastmcp')

from server import mcp

if __name__ == "__main__":
    print("🚀 Starting FastMCP server in HTTP mode...")
    print("📡 Server will be available at http://localhost:8000/mcp")
    print("Press Ctrl+C to stop the server\n")

    # Run in streamable-http mode
    mcp.run(transport="streamable-http")
