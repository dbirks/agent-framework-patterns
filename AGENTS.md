# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains educational examples demonstrating AI agent patterns using the PydanticAI framework. Each numbered Python script is a standalone, executable example showcasing a specific pattern or capability.

## Running Examples

All scripts use Python's inline script metadata (PEP 723) and are designed to run directly with `uv`:

```bash
# Run any example directly
./01_simple.py
# or
uv run 01_simple.py
```

Each script is self-contained with:
- Shebang: `#!/usr/bin/env -S uv run`
- Inline dependencies in `# /// script` blocks
- Python 3.14 requirement
- Core dependencies: `pydantic-ai==1.1.0`, `python-dotenv==1.1.1`

## Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Set your API keys and desired model:
   ```bash
   MODEL=anthropic:claude-haiku-4-5
   ANTHROPIC_API_KEY=sk-ant-...
   ```

The `.env.example` file contains an extensive list of available models across Anthropic, OpenAI, and Gemini providers with descriptions of their capabilities.

## Code Quality

- **Linting**: `uvx ruff check`
- **Auto-fix**: `uvx ruff check --fix`
- **Format**: `uvx ruff format`
- **Type checking**: `uvx ty check <script.py>`

Configuration in `.ruff.toml` with Python 3.14 target.

## Git Workflow

**Commit frequently** with short conventional commit messages:

```bash
git add -A && git commit -m "feat: add new pattern example"
git add -A && git commit -m "fix: correct tool parameter types"
git add -A && git commit -m "docs: update usage instructions"
git add -A && git commit -m "refactor: simplify agent composition"
```

Use conventional commit prefixes: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`

## Script Descriptions

**Each script has a docstring at the top describing what it demonstrates.** When adding new scripts or significantly modifying existing ones, always update the docstring to reflect the current functionality.

Example format:
```python
"""
Script Title

Brief description of what the script demonstrates.
Additional context about the pattern or technique shown.
"""
```

## Architecture Patterns

The examples progress from basic to advanced patterns:

### Current Scripts (01-09)
- **01_hello.py**: Simple agent with one sentence response
- **02_tool_call.py**: Tool definition using `@agent.tool_plain` decorator with dice rolling
- **03_multiple_tool_calls.py**: Multiple weather API tool calls with Logfire observability
- **04_structured_outputs.py**: Structured outputs with Rich tables showing global weather
- **05_multi_agent.py**: Agent composition - coordinator delegates to research and writing sub-agents
- **06_using_mcp_tools.py**: MCP server integration for Kubernetes tools
- **07_conversation_history.py**: Multi-turn travel planning with `message_history`
- **08_llm_as_judge.py**: Output validation with judge agent and `@agent.output_validator`
- **09_human_in_the_loop.py**: Multi-agent goat negotiation with human approval

## Key Architectural Concepts

### Type Safety with Agent Generics
**IMPORTANT**: Use explicit Agent generic syntax instead of `cast()` for type-safe outputs:

```python
# Correct approach
agent = Agent[None, OutputType](
    model,
    output_type=OutputType,
    system_prompt="...",
    instrument=True,
)

result = agent.run_sync("prompt")
output = result.output  # Properly typed as OutputType
```

**Don't use**:
```python
# Avoid this
from typing import cast
agent = Agent(model, output_type=OutputType, ...)
output = cast(OutputType, result.output)
```

The `Agent[DepsT, OutputT]` syntax provides proper type inference automatically.

### Tool Decorators
- `@agent.tool_plain`: Simple tools returning plain Python types (str, dict, list)
- `@agent.tool`: Tools with access to `RunContext` for state/dependencies

Use `tool_plain` for stateless operations, `tool` when you need `ctx.deps` or `ctx.retry`.

### Agent Composition
Agents can use other agents as tools (see 05_multi_agent.py):
```python
# Specialized sub-agents
research_agent = Agent("anthropic:claude-haiku-4-5", ...)
writing_agent = Agent("openai:o4-mini", ...)

# Coordinator agent
coordinator = Agent[None, Article](
    "anthropic:claude-haiku-4-5",
    output_type=Article,
)

@coordinator.tool_plain
def research_topic(topic: str) -> str:
    result = research_agent.run_sync(f"Research: {topic}")
    return result.output
```

### Retry Configuration
- `retries`: Controls both tool calls AND output validation (default: 1)
- `output_retries`: Specifically for output validation, overrides `retries` if set
- For LLM-as-judge pattern, use high `output_retries` (e.g., 10) for iterative improvement

```python
writer_agent = Agent(
    model,
    output_retries=10,  # More attempts for validation loops
    instrument=True,
)

@writer_agent.output_validator
def validate_with_judge(post: str) -> str:
    judge_result = judge_agent.run_sync(f"Evaluate: {post}")
    judgment = judge_result.output
    
    if not judgment.approved:
        raise ModelRetry(f"Rejected. {judgment.feedback}")
    return post
```

### Dependency Injection
Use `deps_type` parameter with `RunContext` for type-safe runtime configuration:
```python
agent = Agent(model, deps_type=MyDeps)

# Access in tools
@agent.tool
def my_tool(ctx: RunContext[MyDeps]) -> str:
    return ctx.deps.some_value
```

### Multi-Agent Patterns
Multiple agents can collaborate or compete:
- **LLM-as-Judge**: One agent validates another's outputs (see 08_llm_as_judge.py)
- **Human-in-the-Loop**: Multiple agents with human approval at key points (see 09_human_in_the_loop.py)
- **Coordinator Pattern**: Main agent delegates to specialized sub-agents (see 05_multi_agent.py)
- Each agent can maintain separate `message_history`
- Different models can be used for different specialized tasks

### Rich Output Formatting
- Use Rich panels and markdown for user-facing output
- Avoid decorative print statements or emoji unless requested
- Let Logfire handle observability, use Rich for presentation

**Rich Markdown Rendering**: Instruct LLMs to use proper line breaks for bullets:
```python
system_prompt="Use proper markdown formatting with bullet points on separate lines (- item or * item, each on its own line)."
```

## Standard Setup Pattern

All scripts follow this standard setup:
```python
import os
from textwrap import dedent

import logfire
from dotenv import load_dotenv
from pydantic_ai import Agent

load_dotenv(override=True)
model = os.getenv("MODEL")
logfire.configure(send_to_logfire=False)
logfire.instrument_pydantic_ai()
```

System prompts use `dedent()` and `.strip()` with closing `"""` on new line:
```python
system_prompt=dedent(
    """
    You're a helpful assistant.
    Be concise and clear.
    """
).strip()
```

## Model Configuration

### Model Prefixes
- Anthropic: `anthropic:claude-haiku-4-5`
- OpenAI: `openai:gpt-4o`
- Google Gemini (Generative Language API): `google-gla:gemini-2.5-pro`
- Google Vertex AI: `google-vertex:gemini-2.5-pro`

The `.env.example` contains extensive model lists with defaults to Haiku for cost efficiency.

## Notes

- No traditional test suite; examples are meant to be run and inspected
- No build step required; scripts are immediately executable
- No package manager beyond `uv` - dependencies declared inline per-script
- Models can be swapped via `MODEL` environment variable without code changes
- Always base script descriptions on actual behavior, not just docstrings
