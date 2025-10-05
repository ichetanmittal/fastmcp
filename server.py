#!/usr/bin/env python3
"""
Production-ready MCP server built with FastMCP
Equivalent to the TypeScript version with tools, resources, and prompts
"""

from datetime import datetime
from typing import Any
import os
from dotenv import load_dotenv
from fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Server configuration
SERVER_NAME = os.getenv("SERVER_NAME", "mcp-server")
SERVER_VERSION = os.getenv("SERVER_VERSION", "1.0.0")

# Initialize FastMCP server
mcp = FastMCP(SERVER_NAME)


# ========== TOOLS ==========

@mcp.tool()
def add(a: float, b: float) -> str:
    """Add two numbers together

    Args:
        a: First number
        b: Second number

    Returns:
        Result of addition
    """
    result = a + b
    return f"Result: {result}"


@mcp.tool()
def echo(message: str) -> str:
    """Echo back the provided text

    Args:
        message: Message to echo

    Returns:
        The same message
    """
    return message


@mcp.tool()
def timestamp() -> dict[str, Any]:
    """Get the current timestamp

    Returns:
        Dictionary with ISO, Unix, and local time formats
    """
    now = datetime.now()
    return {
        "iso": now.isoformat(),
        "unix": int(now.timestamp()),
        "local": now.strftime("%Y-%m-%d %H:%M:%S")
    }


# ========== RESOURCES ==========

@mcp.resource("info://server")
def get_server_info() -> str:
    """Get information about this MCP server"""
    info = {
        "name": SERVER_NAME,
        "version": SERVER_VERSION,
        "capabilities": ["tools", "resources", "prompts"],
        "description": "A production-ready MCP server built with FastMCP (Python)"
    }
    import json
    return json.dumps(info, indent=2)


@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting

    Args:
        name: Name of the person to greet
    """
    return f"Hello, {name}! Welcome to the MCP server."


@mcp.resource("data://{id}")
def get_data(id: str) -> str:
    """Access data by ID

    Args:
        id: The data identifier
    """
    import json
    mock_data = {
        "id": id,
        "timestamp": datetime.now().isoformat(),
        "status": "active",
        "metadata": {
            "source": "mcp-server",
            "type": "example"
        }
    }
    return json.dumps(mock_data, indent=2)


# ========== PROMPTS ==========

@mcp.prompt()
def analyze() -> list[dict[str, str]]:
    """Analysis prompt template"""
    return [
        {
            "role": "user",
            "content": "Please analyze the following data and provide insights."
        }
    ]


@mcp.prompt()
def code_review() -> list[dict[str, str]]:
    """Code review prompt template"""
    return [
        {
            "role": "user",
            "content": """Please review the following code for:
1. Best practices
2. Potential bugs
3. Performance issues
4. Security concerns"""
        }
    ]


@mcp.prompt()
def summarize() -> list[dict[str, str]]:
    """Summarization prompt template"""
    return [
        {
            "role": "user",
            "content": "Please provide a concise summary of the key points."
        }
    ]


if __name__ == "__main__":
    # Run the server
    mcp.run()
