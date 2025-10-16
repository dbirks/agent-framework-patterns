# Coding agent instructions

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

### Basic Patterns (01-09)
- **01_simple.py**: Minimal agent setup
- **02_tool.py**: Tool definition using `@agent.tool_plain` decorator
- **03_human_in_loop.py**: Interactive approval workflow
- **04_multiple_tools.py**: Multiple tools on single agent
- **05_logfire.py**: Observability and instrumentation
- **06_agent_tool.py**: Agent composition (coordinator → sub-agents)
- **07_structured_output.py**: Pydantic model outputs with `output_type`
- **08_mcp_server.py**: MCP (Model Context Protocol) integration
- **09_streaming.py**: Streaming responses with `run_stream()`

### Advanced Patterns (10-17)
- **10_conversation_history.py**: Multi-turn conversations using `message_history`
- **11_retry_validation.py**: Output validation with automatic retries
- **12_dynamic_system_prompts.py**: Context-dependent system prompts via `deps_type`
- **13_parallel_tool_calls.py**: Concurrent tool execution
- **14_rag_knowledge_base.py**: Retrieval-Augmented Generation pattern
- **15_reflection_self_correction.py**: Self-critique and improvement loop
- **16_llm_judge.py**: Using LLM to evaluate outputs
- **17_multi_agent_debate.py**: Multiple agents with different perspectives reaching consensus

## Key Architectural Concepts

### Tool Decorators
- `@agent.tool_plain`: Simple tools returning plain Python types (str, dict, list)
- `@agent.tool`: Tools with access to `RunContext` for state/dependencies

Use `tool_plain` for stateless operations, `tool` when you need `ctx.deps` or `ctx.retry`.

### Agent Composition
Agents can use other agents as tools (see 06_agent_tool.py):
```python
# Coordinator agent
coordinator = Agent(model)

@coordinator.tool_plain
def call_specialist(task: str) -> str:
    result = specialist_agent.run_sync(task)
    return result.output
```

### Dependency Injection
Use `deps_type` parameter with `RunContext` for type-safe runtime configuration (see 12_dynamic_system_prompts.py):
```python
agent = Agent(model, deps_type=MyDeps)

# Access in tools
@agent.tool
def my_tool(ctx: RunContext[MyDeps]) -> str:
    return ctx.deps.some_value
```

### Multi-Agent Patterns
For complex decision-making, multiple agents with different system prompts can debate or collaborate:
- Each agent maintains separate `message_history`
- Final synthesis by a "judge" or "coordinator" agent
- Enables diverse perspectives and reduces bias

## Notes

- No traditional test suite; examples are meant to be run and inspected
- No build step required; scripts are immediately executable
- No package manager beyond `uv` - dependencies declared inline per-script
- Models can be swapped via `MODEL` environment variable without code changes
