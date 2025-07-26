"""
Computer Use MCP: Virtual computer control through MCP.
"""
import os
from dotenv import load_dotenv
import base64
import logging
import sys
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from fastmcp import FastMCP, Context

load_dotenv()

# Configure logging to stdout
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(name="Computer MCP 🖥️")

# Data Models
class ComputerConfig(BaseModel):
    os_type: str = Field("ubuntu", description="Operating system type")
    display_width: int = Field(1024, description="Display width in pixels")
    display_height: int = Field(768, description="Display height in pixels")

# Computer Registry
class ComputerRegistry:
    def __init__(self):
        self.computers = {}
        self.default_session = "default"
    
    def get(self, session_id: Optional[str] = None):
        session_id = session_id or self.default_session
        if session_id not in self.computers:
            raise ValueError(f"No computer found for session '{session_id}'. Initialize one first.")
        return self.computers[session_id]
    
    def add(self, computer, session_id: Optional[str] = None):
        session_id = session_id or self.default_session
        self.computers[session_id] = computer
        return session_id
    
    def remove(self, session_id: Optional[str] = None) -> bool:
        session_id = session_id or self.default_session
        return bool(self.computers.pop(session_id, None))
    
    def list_sessions(self) -> List[str]:
        return list(self.computers.keys())

registry = ComputerRegistry()

# Core Tools
@mcp.tool()
async def initialize_computer(
    project_id: Optional[str] = None,
    session_id: Optional[str] = None,
    base_api_url: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """Initialize a virtual computer with the provided API key."""
    if ctx:
        await ctx.info(f"Initializing computer for session: {session_id or 'default'}")
    
    try:
        from orgo import Computer
    except ImportError:
        if ctx:
            await ctx.error("Orgo SDK not installed. Run: pip install orgo")
        raise ValueError("Orgo SDK not installed")
    
    try:
        computer = Computer(
            project_id=project_id,
            base_api_url=base_api_url,
            config=config
        )
        
        session_id = registry.add(computer, session_id)
        status = computer.status()
        
        if ctx:
            await ctx.info(f"Computer initialized with project ID: {computer.project_id}")
        
        return {
            "session_id": session_id,
            "project_id": computer.project_id,
            "status": status
        }
    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to initialize computer: {str(e)}")
        raise ValueError(f"Computer initialization failed: {str(e)}")

@mcp.tool()
async def get_screenshot(session_id: Optional[str] = None, ctx: Optional[Context] = None) -> Dict[str, str]:
    """Take a screenshot of the virtual computer's display."""
    computer = registry.get(session_id)
    if ctx:
        await ctx.info("Taking screenshot...")
    
    try:
        image_data = computer.screenshot_base64()
        
        if not image_data:
            if ctx:
                await ctx.warning("No image data from screenshot_base64, trying fallback...")
            screenshot = computer.screenshot()
            from io import BytesIO
            buffer = BytesIO()
            screenshot.save(buffer, format="JPEG")
            image_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        return {"image": image_data}
    except Exception as e:
        if ctx:
            await ctx.error(f"Screenshot failed: {str(e)}")
        raise ValueError(f"Screenshot failed: {str(e)}")

@mcp.tool()
async def left_click(x: int, y: int, session_id: Optional[str] = None, ctx: Optional[Context] = None) -> str:
    """Perform a left mouse click at the specified coordinates."""
    computer = registry.get(session_id)
    if ctx:
        await ctx.info(f"Left-clicking at ({x}, {y})")
    
    try:
        computer.left_click(x, y)
        return f"Left-clicked at ({x}, {y})"
    except Exception as e:
        if ctx:
            await ctx.error(f"Left-click failed: {str(e)}")
        raise ValueError(f"Left-click failed: {str(e)}")

@mcp.tool()
async def right_click(x: int, y: int, session_id: Optional[str] = None, ctx: Optional[Context] = None) -> str:
    """Perform a right mouse click at the specified coordinates."""
    computer = registry.get(session_id)
    if ctx:
        await ctx.info(f"Right-clicking at ({x}, {y})")
    
    try:
        computer.right_click(x, y)
        return f"Right-clicked at ({x}, {y})"
    except Exception as e:
        if ctx:
            await ctx.error(f"Right-click failed: {str(e)}")
        raise ValueError(f"Right-click failed: {str(e)}")

@mcp.tool()
async def double_click(x: int, y: int, session_id: Optional[str] = None, ctx: Optional[Context] = None) -> str:
    """Perform a double click at the specified coordinates."""
    computer = registry.get(session_id)
    if ctx:
        await ctx.info(f"Double-clicking at ({x}, {y})")
    
    try:
        computer.double_click(x, y)
        return f"Double-clicked at ({x}, {y})"
    except Exception as e:
        if ctx:
            await ctx.error(f"Double-click failed: {str(e)}")
        raise ValueError(f"Double-click failed: {str(e)}")

@mcp.tool()
async def scroll(direction: str = "down", amount: int = 1, session_id: Optional[str] = None, ctx: Optional[Context] = None) -> str:
    """Scroll in the specified direction and amount."""
    computer = registry.get(session_id)
    if ctx:
        await ctx.info(f"Scrolling {direction} by {amount}")
    
    try:
        computer.scroll(direction, amount)
        return f"Scrolled {direction} by {amount}"
    except Exception as e:
        if ctx:
            await ctx.error(f"Scroll failed: {str(e)}")
        raise ValueError(f"Scroll failed: {str(e)}")

@mcp.tool()
async def type_text(text: str, session_id: Optional[str] = None, ctx: Optional[Context] = None) -> str:
    """Type the specified text into the virtual computer."""
    computer = registry.get(session_id)
    if ctx:
        await ctx.info(f"Typing text: {text[:50]}{'...' if len(text) > 50 else ''}")
    
    try:
        computer.type(text)
        return f"Typed: {text}"
    except Exception as e:
        if ctx:
            await ctx.error(f"Type text failed: {str(e)}")
        raise ValueError(f"Type text failed: {str(e)}")

@mcp.tool()
async def press_key(key: str, session_id: Optional[str] = None, ctx: Optional[Context] = None) -> str:
    """Press a key or key combination (e.g., 'Enter', 'ctrl+c')."""
    computer = registry.get(session_id)
    if ctx:
        await ctx.info(f"Pressing key: {key}")
    
    try:
        computer.key(key)
        return f"Pressed key: {key}"
    except Exception as e:
        if ctx:
            await ctx.error(f"Key press failed: {str(e)}")
        raise ValueError(f"Key press failed: {str(e)}")

@mcp.tool()
async def wait(seconds: float, session_id: Optional[str] = None, ctx: Optional[Context] = None) -> str:
    """Wait for the specified number of seconds."""
    computer = registry.get(session_id)
    if ctx:
        await ctx.info(f"Waiting for {seconds} seconds")
    
    try:
        computer.wait(seconds)
        return f"Waited for {seconds} seconds"
    except Exception as e:
        if ctx:
            await ctx.error(f"Wait failed: {str(e)}")
        raise ValueError(f"Wait failed: {str(e)}")

@mcp.tool()
async def execute_bash(command: str, session_id: Optional[str] = None, ctx: Optional[Context] = None) -> str:
    """Execute a bash command on the virtual computer."""
    computer = registry.get(session_id)
    if ctx:
        await ctx.info(f"Executing bash command: {command}")
    
    try:
        output = computer.bash(command)
        return output
    except Exception as e:
        if ctx:
            await ctx.error(f"Bash command failed: {str(e)}")
        raise ValueError(f"Bash command failed: {str(e)}")

@mcp.tool()
async def restart_computer(session_id: Optional[str] = None, ctx: Optional[Context] = None) -> Dict[str, Any]:
    """Restart the virtual computer."""
    computer = registry.get(session_id)
    if ctx:
        await ctx.info("Restarting computer...")
    
    try:
        result = computer.restart()
        return result
    except Exception as e:
        if ctx:
            await ctx.error(f"Restart failed: {str(e)}")
        raise ValueError(f"Restart failed: {str(e)}")

@mcp.tool()
async def shutdown_computer(session_id: Optional[str] = None, ctx: Optional[Context] = None) -> Dict[str, Any]:
    """Shutdown and terminate the virtual computer instance."""
    computer = registry.get(session_id)
    if ctx:
        await ctx.info("Shutting down computer...")
    
    try:
        result = computer.shutdown()
        registry.remove(session_id)
        return result
    except Exception as api_err:
        logger.warning(f"API error during shutdown: {api_err}. Removing from registry anyway.")
        registry.remove(session_id)
        return {
            "status": "removed_from_registry",
            "warning": f"API error occurred but computer removed from registry: {str(api_err)}"
        }

@mcp.tool()
async def get_status(session_id: Optional[str] = None, ctx: Optional[Context] = None) -> Dict[str, Any]:
    """Get the current status of the virtual computer."""
    computer = registry.get(session_id)
    if ctx:
        await ctx.info("Getting computer status...")
    
    try:
        status = computer.status()
        return status
    except Exception as e:
        if ctx:
            await ctx.error(f"Status check failed: {str(e)}")
        raise ValueError(f"Status check failed: {str(e)}")

@mcp.tool()
async def list_sessions(ctx: Optional[Context] = None) -> Dict[str, List[str]]:
    """List all active computer sessions."""
    if ctx:
        await ctx.info("Listing all active sessions...")
    
    try:
        sessions = registry.list_sessions()
        return {"sessions": sessions}
    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to list sessions: {str(e)}")
        raise ValueError(f"Failed to list sessions: {str(e)}")

@mcp.tool()
async def prompt(
    instruction: str,
    provider: str = "anthropic",
    model: str = "claude-3-7-sonnet-20250219",
    thinking_enabled: bool = False,
    session_id: Optional[str] = None,
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """Control the computer with natural language using an AI agent."""
    computer = registry.get(session_id)
    if ctx:
        await ctx.info(f"Executing prompt: {instruction[:100]}{'...' if len(instruction) > 100 else ''}")
    
    if provider == "anthropic" and not os.environ.get("ANTHROPIC_API_KEY"):
        raise ValueError("Anthropic API key required but not provided")
    
    try:
        result = computer.prompt(
            instruction=instruction,
            provider=provider,
            model=model,
            thinking_enabled=thinking_enabled,
        )
        
        return {
            "success": True,
            "message_count": len(result),
            "result": "Prompt executed successfully"
        }
    except Exception as e:
        if ctx:
            await ctx.error(f"Prompt execution failed: {str(e)}")
        raise ValueError(f"Prompt execution failed: {str(e)}")

# Resources
@mcp.resource("computer://server/info")
def server_info() -> Dict[str, Any]:
    """Information about the Computer MCP server."""
    return {
        "name": "Computer MCP",
        "description": "MCP interface for controlling virtual computers",
        "version": "1.0.0",
        "active_sessions": len(registry.computers)
    }

# Prompts
@mcp.prompt()
def desktop_guidelines() -> str:
    """Guidelines for interacting with the Ubuntu desktop environment."""
    return """# Ubuntu Desktop Interaction Guidelines

## Essential Desktop Actions
* **Opening applications/files**: ALWAYS use DOUBLE-CLICK rather than single-click
* **Menu selections**: Use SINGLE-CLICK for menu items
* **Taskbar icons**: Use SINGLE-CLICK to open applications from the taskbar
* **Window controls**: Use SINGLE-CLICK for close, minimize, maximize buttons

## Common Keyboard Shortcuts
* `Alt+Tab`: Switch between windows
* `Ctrl+Alt+T`: Open terminal
* `Ctrl+C`: Copy selected text
* `Ctrl+V`: Paste text
* `Alt+F4`: Close current window

## Best Practices
* Take a screenshot first to see the current state
* Use double_click instead of left_click for desktop icons
* Press "Enter" key for form submissions
* For long operations, consider the wait function
"""

if __name__ == "__main__":
    mcp.run()
    # mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)