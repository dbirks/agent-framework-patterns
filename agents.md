# Notes for Future Coding Agents

This document contains important patterns, conventions, and lessons learned while developing this project.

## Project Structure

- **Numbered Scripts (01-09)**: Each script demonstrates a specific PydanticAI pattern
- **Self-Contained**: Each script uses PEP 723 inline script metadata with dependencies
- **Executable**: All scripts have `#!/usr/bin/env -S uv run` shebang for direct execution
- **.env Configuration**: Model and API keys configured via environment variables

## Code Style & Conventions

### Standard Setup Block
All scripts follow this pattern:
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

### System Prompts
- Use `dedent()` and `.strip()` for multi-line prompts
- Place closing `"""` on new line
- Keep prompts clear and concise

Example:
```python
system_prompt=dedent(
    """
    You're a helpful assistant.
    Be concise and clear.
    """
).strip()
```

### Rich Output
- Use Rich panels and markdown for user-facing output
- Avoid decorative print statements or emoji unless explicitly requested
- Let Logfire handle observability, use Rich for presentation

### Type Safety with Agent Generics
**IMPORTANT**: Use explicit Agent generic syntax instead of `cast()`

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

The `Agent[DepsT, OutputT]` syntax provides proper type inference without needing `cast()`.

## PydanticAI Patterns

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
```

### Output Validators
Use `@agent.output_validator` for quality control:
```python
@writer_agent.output_validator
def validate_with_judge(post: str) -> str:
    judge_result = judge_agent.run_sync(f"Evaluate: {post}")
    judgment = judge_result.output
    
    if not judgment.approved:
        raise ModelRetry(f"Rejected. {judgment.feedback}")
    return post
```

### Message History
Pass `message_history` between runs for multi-turn conversations:
```python
result = agent.run_sync("First message")
message_history = result.new_messages()

result = agent.run_sync("Second message", message_history=message_history)
message_history = result.new_messages()
```

### Tool Definition
Use `@agent.tool_plain` for simple tools returning Python types:
```python
@agent.tool_plain
def get_weather(city: str) -> dict[str, str | int]:
    """Fetch weather data for a city."""
    # Implementation
    return {"city": city, "temp": 72}
```

## Model Configuration

### .env.example Format
- Include API key documentation links as comments
- Compact format without section headers
- List common models as commented options
- Default to `anthropic:claude-haiku-4-5`

### Model Prefixes
- Anthropic: `anthropic:claude-haiku-4-5`
- OpenAI: `openai:gpt-4o`
- Google Gemini: `google-gla:gemini-2.5-pro` (uses Generative Language API)
- Google Vertex: `google-vertex:gemini-2.5-pro` (uses Vertex AI)

## Rich Markdown Rendering

### Bullet Point Issue
Rich markdown needs proper line breaks for bullet points. Instruct LLMs:

```python
system_prompt="Use proper markdown formatting with bullet points on separate lines (- item or * item, each on its own line)."
```

Without explicit line breaks, bullets appear inline instead of as lists.

## Logfire Observability

### Configuration
- Always use `send_to_logfire=False` for local development
- Use `instrument=True` on agents for automatic tracing
- Call `logfire.instrument_pydantic_ai()` once at startup

### String Truncation
Logfire automatically truncates long strings in output. If detailed output is needed, don't rely on logfire logging—use Rich panels or other output methods.

## Common Patterns

### Multi-Agent Composition
Coordinator delegates to specialized sub-agents:
```python
research_agent = Agent("anthropic:claude-haiku-4-5", ...)
writing_agent = Agent("openai:o4-mini", ...)

coordinator = Agent[None, Article](
    "anthropic:claude-haiku-4-5",
    output_type=Article,
    instrument=True,
)

@coordinator.tool_plain
def research_topic(topic: str) -> str:
    result = research_agent.run_sync(f"Research: {topic}")
    return result.output
```

### Human-in-the-Loop
Use Rich prompts for interactive input:
```python
from rich.prompt import Prompt

user_input = Prompt.ask("\n[bold blue]You[/bold blue]")
```

### MCP Server Integration
Connect to MCP servers for external tools:
```python
from pydantic_ai.mcp import MCPServerStdio

mcp_server = MCPServerStdio("pnpx", args=["kubernetes-mcp-server@0.0.53"], timeout=30)

agent = Agent(
    model,
    toolsets=[mcp_server],
    system_prompt="...",
)
```

## Script Descriptions

When writing README or documentation, base descriptions on actual script behavior, not just docstrings. Read the code to understand what it actually does.

## Type Checking

Run type checker with:
```bash
uvx --from basedpyright basedpyright *.py
```

Fix errors before committing. Warnings from library code are acceptable.

## Commits

- Keep commits focused and atomic
- Use conventional commit prefixes: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`
- Run type checker before committing major changes
