# Agent framework patterns

A collection of example scripts demonstrating common patterns and capabilities in PydanticAI. These scripts progress from basic agent setup to advanced multi-agent orchestration, showing practical patterns for building AI agents with structured outputs, tool use, and observability.

## Prerequisites

### Install uv

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and script execution.

**macOS:**
```bash
brew install uv
```

**Windows:**
```powershell
winget install astral-sh.uv
```

### Configure environment variables

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Get your API keys from:
# Anthropic: https://console.anthropic.com/settings/keys
ANTHROPIC_API_KEY=sk-ant-...

# OpenAI: https://platform.openai.com/settings/organization/api-keys
OPENAI_API_KEY=sk-proj-...

# Google: https://console.cloud.google.com/apis/credentials
GOOGLE_API_KEY=ABC123...

# Choose your model
MODEL=anthropic:claude-haiku-4-5
```

## Running Scripts

Each script is self-contained with its own dependencies. Simply run:

```bash
./01_hello.py
```

Or explicitly with uv:

```bash
uv run 01_hello.py
```

## Scripts

### [`01_hello.py`](01_hello.py) - Simple Agent
The most basic example. Creates an agent that answers a single question with one sentence.

### [`02_tool_call.py`](02_tool_call.py) - Tool Definition
Shows how to define custom tools with `@agent.tool_plain`. Agent uses a dice rolling tool to generate random numbers.

### [`03_multiple_tool_calls.py`](03_multiple_tool_calls.py) - Multiple Tools with Logfire
Agent calls a weather API tool multiple times to compare temperatures across Tokyo, Sydney, and London. Includes Logfire observability for tracking tool calls.

### [`04_structured_outputs.py`](04_structured_outputs.py) - Structured Outputs with Rich Tables
Agent fetches weather data for 13 cities worldwide and returns a typed `WeatherReport` object, displayed in a Rich table. Shows type-safe outputs with `Agent[None, OutputType]` syntax.

### [`05_multi_agent.py`](05_multi_agent.py) - Agent Composition
A coordinator agent delegates to two specialized sub-agents: a research agent that searches DuckDuckGo for quantum computing information, and a writing agent that transforms findings into prose.

### [`06_using_mcp_tools.py`](06_using_mcp_tools.py) - MCP Server Integration
Connects to a Kubernetes MCP server and uses its tools to check deployment status. Shows how to integrate external tool servers using Model Context Protocol.

### [`07_conversation_history.py`](07_conversation_history.py) - Conversation History
Interactive travel planning assistant that maintains context across multiple turns by passing `message_history` between runs. The agent asks questions and remembers your answers.

### [`08_llm_as_judge.py`](08_llm_as_judge.py) - LLM as Judge Pattern
A writer agent creates LinkedIn posts, and a judge agent (claude haiku) validates them against criteria. Uses `@agent.output_validator` for automatic retry loops.

### [`09_human_in_the_loop.py`](09_human_in_the_loop.py) - Human-in-the-Loop
Multi-agent goat negotiation where your negotiator agent works with you to buy goats from an unpredictable seller agent. You approve or modify each counteroffer before it's sent.
