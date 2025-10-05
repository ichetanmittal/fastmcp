# MCP Server - Python (FastMCP)

A production-ready Model Context Protocol (MCP) server built with FastMCP. This is the Python equivalent of the TypeScript version, designed for deployment to FastMCP Cloud.

## Features

- **Tools**: Execute actions (add, echo, timestamp)
- **Resources**: Access data (server info, greetings, data by ID)
- **Prompts**: Reusable prompt templates (analyze, code-review, summarize)

## Project Structure

```
mcp-server-python/
├── server.py              # Main server with all capabilities
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .gitignore
└── README.md
```

## Installation

### Local Setup

1. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy environment file:
   ```bash
   cp .env.example .env
   ```

## Running Locally

### Standard Mode (stdio)
```bash
python server.py
```

### Development Mode
```bash
fastmcp dev server.py
```

This will start the MCP Inspector for testing.

## Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector python server.py
```

Or use FastMCP's built-in inspector:
```bash
fastmcp dev server.py
```

## Available Capabilities

### Tools
- `add(a, b)` - Add two numbers
- `echo(message)` - Echo text back
- `timestamp()` - Get current timestamp (ISO, Unix, local)

### Resources
- `info://server` - Server information
- `greeting://{name}` - Personalized greeting
- `data://{id}` - Data by ID

### Prompts
- `analyze` - Analysis prompt template
- `code_review` - Code review prompt template
- `summarize` - Summarization prompt template

## Deploy to FastMCP Cloud

### Method 1: Via Web Interface

1. Go to [https://fastmcp.cloud](https://fastmcp.cloud)
2. Click "Deploy New Server"
3. Connect your GitHub repository
4. Set entrypoint: `server.py`
5. Deploy!

### Method 2: Via GitHub

1. Push this code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. On FastMCP Cloud:
   - Connect GitHub repository
   - Select repository
   - Set entrypoint: `server.py`
   - Configure resources (default: 1 vCPU / 2GB RAM)
   - Deploy

### Deployment Configuration

**Entrypoint**: `server.py`

**Build Resources**: 2 vCPU / 4GB RAM (default)

**Runtime Resources**: 1 vCPU / 2GB RAM (default)

**Authentication**: Optional (can enable for security)

**Discoverable**: Optional (makes it searchable)

## Environment Variables

Set these in FastMCP Cloud dashboard or locally in `.env`:

```env
SERVER_NAME=mcp-server
SERVER_VERSION=1.0.0
```

## Testing the Deployed Server

Once deployed, you'll get a URL like:
```
https://your-server-name.fastmcp.app/mcp
```

### Test with Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "fastmcp-server": {
      "url": "https://your-server-name.fastmcp.app/mcp"
    }
  }
}
```

### Test with Python Client

```python
from fastmcp import FastMCP

client = FastMCP("https://your-server-name.fastmcp.app/mcp")
result = client.call_tool("add", {"a": 5, "b": 3})
print(result)
```

## Differences from TypeScript Version

| Feature | TypeScript | Python (FastMCP) |
|---------|-----------|------------------|
| Framework | @modelcontextprotocol/sdk | FastMCP |
| Language | TypeScript/Node.js | Python 3.9+ |
| Deployment | Manual (Cloud Run, Railway) | FastMCP Cloud (one-click) |
| Schema Validation | Zod | Pydantic (built-in) |
| Type Hints | TypeScript types | Python type hints |

## Migration Notes

This Python version is **functionally identical** to the TypeScript version:

✅ Same 3 tools (add, echo, timestamp)
✅ Same 3 resources (info, greeting, data)
✅ Same 3 prompts (analyze, code-review, summarize)
✅ Same response formats
✅ Compatible with same clients

The only difference is the implementation language and deployment target.

## Development

### Add New Tool
```python
@mcp.tool()
def my_tool(param: str) -> str:
    """Tool description"""
    return f"Result: {param}"
```

### Add New Resource
```python
@mcp.resource("myscheme://{id}")
def my_resource(id: str) -> str:
    """Resource description"""
    return f"Data for {id}"
```

### Add New Prompt
```python
@mcp.prompt()
def my_prompt() -> list[dict[str, str]]:
    """Prompt description"""
    return [{"role": "user", "content": "Your prompt"}]
```

## License

MIT
