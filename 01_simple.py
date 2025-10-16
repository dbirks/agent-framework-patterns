from pydantic_ai import Agent

# Create a simple agent with Claude Sonnet 4.0
agent = Agent(
    "anthropic:claude-sonnet-4-0", instructions="Be concise, reply with one sentence."
)

# Run the agent synchronously with a simple prompt
result = agent.run_sync('Where does "hello world" come from?')
print(result.output)
