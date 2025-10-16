#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#   "pydantic-ai==1.1.0",
#   "python-dotenv==1.1.1",
# ]
# ///

import os

from dotenv import load_dotenv
from pydantic_ai import Agent

# Load environment variables from .env file
load_dotenv(override=True)

model = os.getenv("MODEL")

# Knowledge base - simulating a documentation database
KNOWLEDGE_BASE = [
    {
        "id": 1,
        "category": "getting-started",
        "title": "Creating an Agent",
        "content": "To create a PydanticAI agent, use the Agent class: `agent = Agent('model-name', system_prompt='...')`. The agent encapsulates model configuration and behavior instructions.",
    },
    {
        "id": 2,
        "category": "tools",
        "title": "Function Tools",
        "content": "Tools are registered using decorators: `@agent.tool_plain` for simple tools or `@agent.tool` for tools needing context. Tools let agents perform actions and retrieve information dynamically.",
    },
    {
        "id": 3,
        "category": "tools",
        "title": "Tool Parameters",
        "content": "Tool functions can accept typed parameters. PydanticAI automatically generates schemas from type hints. Tools can use Pydantic models for complex parameter validation.",
    },
    {
        "id": 4,
        "category": "dependencies",
        "title": "Dependency Injection",
        "content": "Pass runtime dependencies to agents using the deps_type parameter and RunContext. This enables type-safe configuration: `agent = Agent(model, deps_type=MyDeps)` then access via `ctx.deps` in tools and system prompts.",
    },
    {
        "id": 5,
        "category": "output",
        "title": "Structured Output",
        "content": "Define structured outputs using Pydantic models with output_type parameter: `agent = Agent(model, output_type=MyModel)`. The agent's response will be validated and typed automatically.",
    },
    {
        "id": 6,
        "category": "output",
        "title": "Streaming Responses",
        "content": "Use `agent.run_stream()` to stream responses token-by-token. This is useful for long-form content where you want to show progressive output to users.",
    },
    {
        "id": 7,
        "category": "advanced",
        "title": "Message History",
        "content": "Maintain conversation context by passing message_history: `result2 = agent.run_sync(prompt, message_history=result1.new_messages())`. This enables multi-turn conversations.",
    },
    {
        "id": 8,
        "category": "advanced",
        "title": "Result Validators",
        "content": "Add validation to agent outputs using Pydantic validators. Validators can enforce quality constraints and trigger retries if validation fails.",
    },
    {
        "id": 9,
        "category": "observability",
        "title": "Logfire Integration",
        "content": "Instrument agents with Logfire for observability: `logfire.instrument_pydantic_ai()` and set `instrument=True` on agents. This provides detailed tracing of agent operations.",
    },
]

# Create a RAG agent
agent = Agent(
    model,
    system_prompt="""You're a helpful PydanticAI documentation assistant.
When answering questions, always search the knowledge base first to provide accurate information.
If you find relevant documentation, cite it in your answer. If no relevant docs are found, say so.""",
)


@agent.tool_plain
def search_knowledge_base(query: str, max_results: int = 3) -> list[dict]:
    """Search the PydanticAI knowledge base for relevant documentation.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default 3)

    Returns:
        List of relevant documentation entries
    """
    print(f"   🔍 Searching knowledge base for: '{query}'")

    query_lower = query.lower()
    results = []

    # Simple keyword-based search
    for doc in KNOWLEDGE_BASE:
        score = 0
        # Check title and content for query terms
        for term in query_lower.split():
            if term in doc["title"].lower():
                score += 3
            if term in doc["content"].lower():
                score += 1
            if term in doc["category"].lower():
                score += 2

        if score > 0:
            results.append((score, doc))

    # Sort by relevance score and return top results
    results.sort(reverse=True, key=lambda x: x[0])
    top_results = [doc for score, doc in results[:max_results]]

    print(f"   ✅ Found {len(top_results)} relevant document(s)")
    return top_results


# Demo queries
print("📚 RAG Knowledge Base Demo")
print("=" * 70)
print("Agent retrieves relevant docs before answering questions\n")

questions = [
    "How do I create an agent in PydanticAI?",
    "What are tools and how do I use them?",
    "Can I maintain conversation history across multiple turns?",
    "How do I integrate Logfire for monitoring?",
]

for i, question in enumerate(questions, 1):
    print(f"\n{'=' * 70}")
    print(f"Question {i}: {question}")
    print()

    result = agent.run_sync(question)
    print(f"🤖 Answer:\n{result.output}")

print(f"\n{'=' * 70}")
print("✅ RAG Pattern Benefits:")
print("   - Agent retrieves relevant documentation before answering")
print("   - Answers are grounded in actual knowledge base content")
print("   - Reduces hallucination by providing factual context")
print("   - Knowledge base can be updated without retraining")
