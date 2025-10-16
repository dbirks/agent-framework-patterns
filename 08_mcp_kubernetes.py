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

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

# Load environment variables
load_dotenv(override=True)
model = os.getenv("MODEL")


# Structured output for deployment status
class ServiceStatus(BaseModel):
    """Status information for a deployed service"""

    service_name: str = Field(description="Name of the service (api or ui)")
    deployment_found: bool = Field(description="Whether the deployment exists")
    image_tag: str = Field(description="Current image tag deployed")
    replicas: int = Field(description="Number of replicas")
    ready_replicas: int = Field(description="Number of ready replicas")
    last_restart_time: str = Field(description="Most recent pod restart time")
    issues_found: list[str] = Field(description="List of issues found in logs or pod status")


class ClusterReport(BaseModel):
    """Complete status report for ai-data-collector services"""

    api_status: ServiceStatus = Field(description="Status of the API service")
    ui_status: ServiceStatus = Field(description="Status of the UI service")
    summary: str = Field(description="Overall summary of the deployment health")


# Create agent with Kubernetes MCP integration
agent = Agent(
    model,
    output_type=ClusterReport,
    system_prompt=dedent(
        """
        You're a Kubernetes cluster monitoring assistant using the kubernetes-mcp-server.
        Check the status of ai-data-collector-api and ai-data-collector-ui deployments.

        For each service:
        1. Find the deployment and get the current image tag
        2. Check replica status (desired vs ready)
        3. Get the most recent pod restart time
        4. Check recent logs for errors or warnings

        Provide a comprehensive ClusterReport with findings.
        """
    ).strip(),
)


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
    agent_with_mcp = Agent(
        model,
        output_type=ClusterReport,
        toolsets=[server],
        system_prompt=agent.system_prompt,
    )

    # Query for deployment status with async context
    async with agent_with_mcp:
        result = await agent_with_mcp.run(
            dedent(
                """
                Check the status of these deployments in the cluster:
                - ai-data-collector-api
                - ai-data-collector-ui

                For each:
                1. Get the current image and tag
                2. Check replica counts
                3. Find the latest pod restart time
                4. Check logs for any errors or warnings in the last 50 lines

                Look for common issues like:
                - CrashLoopBackOff or ImagePullBackOff
                - Error messages in logs
                - Pod restarts
                - Unhealthy replicas
                """
            ).strip()
        )

    report: ClusterReport = result.output
    return report


# Run the async function
import asyncio

try:
    report = asyncio.run(check_cluster_status())

    print("=" * 70)
    print("📊 DEPLOYMENT STATUS REPORT")
    print("=" * 70)
    print()

    print(f"🔷 API Service: {report.api_status.service_name}")
    print(f"   Deployment Found: {'✅' if report.api_status.deployment_found else '❌'}")
    if report.api_status.deployment_found:
        print(f"   Image Tag: {report.api_status.image_tag}")
        print(f"   Replicas: {report.api_status.ready_replicas}/{report.api_status.replicas}")
        print(f"   Last Restart: {report.api_status.last_restart_time}")
        if report.api_status.issues_found:
            print(f"   ⚠️  Issues:")
            for issue in report.api_status.issues_found:
                print(f"      • {issue}")
        else:
            print(f"   ✅ No issues detected")
    print()

    print(f"🔷 UI Service: {report.ui_status.service_name}")
    print(f"   Deployment Found: {'✅' if report.ui_status.deployment_found else '❌'}")
    if report.ui_status.deployment_found:
        print(f"   Image Tag: {report.ui_status.image_tag}")
        print(f"   Replicas: {report.ui_status.ready_replicas}/{report.ui_status.replicas}")
        print(f"   Last Restart: {report.ui_status.last_restart_time}")
        if report.ui_status.issues_found:
            print(f"   ⚠️  Issues:")
            for issue in report.ui_status.issues_found:
                print(f"      • {issue}")
        else:
            print(f"   ✅ No issues detected")
    print()

    print("=" * 70)
    print(f"📋 SUMMARY")
    print("=" * 70)
    print(report.summary)
    print()

except Exception as e:
    print(f"❌ Error connecting to Kubernetes cluster: {e}")
    print()
    print("Make sure:")
    print("  • You have kubectl configured with cluster access")
    print("  • The ai-data-collector deployments exist")
    print("  • Node.js/pnpm is installed for running kubernetes-mcp-server")
