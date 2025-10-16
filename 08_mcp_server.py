#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#   "pydantic-ai==1.1.0",
#   "python-dotenv==1.1.1",
#   "mcp==1.3.2",
# ]
# ///
"""
MCP-Style File System Tools

Demonstrates tools that follow the Model Context Protocol (MCP) pattern for file operations.
Shows how to create file system tools that can read files, list directories, and get file info.
MCP-style tools provide a standardized interface for agent-environment interactions.
"""

import os

from dotenv import load_dotenv
from pydantic_ai import Agent

# Load environment variables from .env file
load_dotenv(override=True)

model = os.getenv("MODEL")

# Create an agent that uses MCP-style tools
agent = Agent(
    model,
    system_prompt="You're a file system assistant that can read and list files.",
)


# MCP-style tool for reading files
@agent.tool_plain
def read_file(path: str) -> str:
    """Read contents of a file (MCP-style operation)."""
    try:
        with open(path, "r") as f:
            content = f.read()
        return f"File content:\n{content}"
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except Exception as e:
        return f"Error reading file: {e}"


# MCP-style tool for listing directory
@agent.tool_plain
def list_directory(path: str = ".") -> str:
    """List files in a directory (MCP-style operation)."""
    try:
        import os as os_module

        files = os_module.listdir(path)
        return f"Files in {path}:\n" + "\n".join(f"- {f}" for f in files[:10])
    except Exception as e:
        return f"Error listing directory: {e}"


# MCP-style tool for file info
@agent.tool_plain
def get_file_info(path: str) -> str:
    """Get information about a file (MCP-style operation)."""
    try:
        import os as os_module

        stat = os_module.stat(path)
        return f"File: {path}\nSize: {stat.st_size} bytes\nModified: {stat.st_mtime}"
    except Exception as e:
        return f"Error getting file info: {e}"


# Run the agent with MCP-style tools
print("📁 MCP-Style File System Tools Demo")
print("=" * 50)
result = agent.run_sync(
    "What files are in the current directory? Show me info about the .env.example file and read its contents."
)
print(f"\n{result.output}")
