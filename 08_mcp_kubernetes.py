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
MCP Kubernetes Server Integration

Demonstrates integration with the Kubernetes MCP server to query cluster resources.
Uses pnpx to run the kubernetes-mcp-server and queries deployment information,
image tags, pod status, and logs for the ai-data-collector API and UI services.
Shows how to use MCP servers for infrastructure monitoring and operations.
"""

import os

import logfire
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

load_dotenv(override=True)
model = os.getenv("MODEL")
logfire.configure(send_to_logfire=False)
logfire.instrument_pydantic_ai()

kubernetes_mcp_server = MCPServerStdio("pnpx", args=["kubernetes-mcp-server@0.0.53"], timeout=30)

agent = Agent(
    model,
    toolsets=[kubernetes_mcp_server],
    system_prompt="You're a Kubernetes monitoring assistant. Check deployment status and report findings.",
)

with agent:
    result = agent.run_sync("Check the status of ai-data-collector")
    print(result.output)
