# Computer Use MCP Server 🖥️

Control virtual computers through the Model Context Protocol (MCP). Built with FastMCP and Orgo.

Spin up cloud desktop environments for Computer Use Agents (CUA).

## Quick Start

### 1. Install Dependencies
```bash
# Create virtual environment
python3 -m venv mcp-env
source mcp-env/bin/activate

# Install packages
pip install fastmcp pydantic orgo
```

### 2. Get API Keys
- **Orgo API Key**: Sign up at [orgo.ai](https://orgo.ai)
- **Anthropic API Key**: Get from [console.anthropic.com](https://console.anthropic.com)

### 3. Run Server
```bash
# Set environment variables
export ORGO_API_KEY="your_orgo_key"
export ANTHROPIC_API_KEY="your_anthropic_key"

# Start server
python server.py
```

Server runs on `http://127.0.0.1:9000`

## Test Client

```python
import asyncio
from fastmcp import Client

async def demo():
    async with Client("http://127.0.0.1:9000/mcp") as client:
        # Initialize computer
        result = await client.call_tool("initialize_computer", {
            "api_key": "your_orgo_key"
        })
        print(f"Computer ready: {result[0].text}")
        
        # Take screenshot
        screenshot = await client.call_tool("get_screenshot")
        print("Screenshot taken!")
        
        # Click and type
        await client.call_tool("left_click", {"x": 100, "y": 200})
        await client.call_tool("type_text", {"text": "Hello World"})
        await client.call_tool("press_key", {"key": "Enter"})

if __name__ == "__main__":
    asyncio.run(demo())
```

## Available Tools

| Tool | Description |
|------|-------------|
| `initialize_computer` | Start virtual computer |
| `get_screenshot` | Take screen capture |
| `left_click`, `right_click`, `double_click` | Mouse actions |
| `scroll` | Scroll up/down |
| `type_text`, `press_key` | Keyboard input |
| `wait` | Wait for specified seconds |
| `execute_bash` | Run terminal commands |
| `restart_computer`, `shutdown_computer` | Computer lifecycle |
| `get_status`, `list_sessions` | Status and session management |
| `prompt` | Claude AI Computer Use |

## Claude AI Computer Use Example

```python
# Let Claude control the computer
await client.call_tool("prompt", {
    "instruction": "Open Firefox and go to google.com"
})
```

## Smithery Configuration

This MCP is configured for use with Smithery. The `smithery.yaml` file defines the required configuration:

- `orgoApiKey`: Your Orgo API key
- `anthropicApiKey`: Your Anthropic API key

When using with Smithery, these keys will be automatically passed as environment variables to the server.

## Requirements

- Python 3.8+
- Orgo API key
- Anthropic API key (for Claude CUA)