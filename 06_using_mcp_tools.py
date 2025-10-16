#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#   "pydantic-ai==1.1.0",
#   "python-dotenv==1.1.1",
#   "mcp==1.17.0",
#   "rich==14.2.0",
# ]
# ///
"""
MCP Server Integration

Demonstrates connecting to an MCP server for Kubernetes and letting the agent use the tools.
"""

import os

import logfire
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()

load_dotenv(override=True)
model = os.getenv("MODEL")
logfire.configure(send_to_logfire=False)
logfire.instrument_pydantic_ai()

kubernetes_mcp_server = MCPServerStdio("pnpx", args=["kubernetes-mcp-server@0.0.53"], timeout=30)

agent = Agent(
    model,
    toolsets=[kubernetes_mcp_server],
    system_prompt="You're a Kubernetes monitoring assistant. Check deployment status and report findings in clear, formatted text. Be persistent and thorough.",
)

console.print("\n[bold cyan]Kubernetes investigation with MCP[/bold cyan]\n")

result = agent.run_sync("Check the status of ai-data-collector")

console.print(Panel(Markdown(result.output), title="Deployment Status", border_style="cyan"))
console.print()
