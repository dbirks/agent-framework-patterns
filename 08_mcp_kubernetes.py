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
from textwrap import dedent

import logfire
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

load_dotenv(override=True)
model = os.getenv("MODEL")
logfire.configure(send_to_logfire=False)
logfire.instrument_pydantic_ai()


# Structured output for deployment status
class DeploymentStatus(BaseModel):
    """Status information for a deployment"""

    name: str = Field(description="Deployment name")
    status: str = Field(description="Overall status summary")
    details: dict = Field(description="Additional details about the deployment")


# Deployments to monitor
DEPLOYMENTS = ["ai-data-collector-api", "ai-data-collector-ui"]


async def check_cluster_status():
    """Query Kubernetes cluster for ai-data-collector services"""
    print("☸️  Kubernetes Cluster Status Monitor")
    print("=" * 70)
    print()
    print("Connecting to Kubernetes MCP server...")
    print()

    # Create MCP server connection to kubernetes-mcp-server
    server = MCPServerStdio("pnpx", args=["kubernetes-mcp-server@0.0.53"], timeout=30)

    # Create agent with MCP server as toolset
    agent = Agent(
        model,
        toolsets=[server],
        system_prompt="You're a Kubernetes cluster monitoring assistant. Do thorough digging on the user's questions and check logs.",
    )

    # Query for deployment status
    async with agent:
        result = await agent.run(f"Check the status of these deployments: {', '.join(DEPLOYMENTS)}")

    return result.output


# Run the async function
import asyncio

try:
    output = asyncio.run(check_cluster_status())

    print()
    print("=" * 70)
    print("📊 DEPLOYMENT STATUS")
    print("=" * 70)
    print()
    print(output)
    print()

except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("Requirements:")
    print("  • kubectl configured with cluster access")
    print("  • Node.js/pnpm installed for kubernetes-mcp-server")
    print(f"  • Deployments exist: {', '.join(DEPLOYMENTS)}")
