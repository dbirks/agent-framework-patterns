#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#   "pydantic-ai==1.1.0",
#   "python-dotenv==1.1.1",
# ]
# ///

import os
from dataclasses import dataclass
from datetime import datetime

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

# Load environment variables from .env file
load_dotenv(override=True)

model = os.getenv("MODEL")


# Define dependencies that will control the dynamic system prompt
@dataclass
class UserContext:
    name: str
    expertise_level: str  # beginner, intermediate, expert
    preferred_language: str  # casual, professional, technical
    time_of_day: str  # morning, afternoon, evening


# Create agent with dynamic system prompts
agent = Agent(model, deps_type=UserContext)


# Dynamic system prompt based on user expertise
@agent.system_prompt
def expertise_prompt(ctx: RunContext[UserContext]) -> str:
    level_prompts = {
        "beginner": "Explain concepts simply, avoid jargon, and use analogies.",
        "intermediate": "Provide detailed explanations with some technical terms.",
        "expert": "Use precise technical language and focus on advanced details.",
    }
    return level_prompts.get(ctx.deps.expertise_level, level_prompts["intermediate"])


# Dynamic system prompt based on preferred language style
@agent.system_prompt
def style_prompt(ctx: RunContext[UserContext]) -> str:
    style_prompts = {
        "casual": f"Be friendly and conversational. Call the user {ctx.deps.name}.",
        "professional": "Be polite and formal in your responses.",
        "technical": "Be precise and concise, focusing on technical accuracy.",
    }
    return style_prompts.get(ctx.deps.preferred_language, style_prompts["professional"])


# Dynamic system prompt based on time of day
@agent.system_prompt
def time_prompt(ctx: RunContext[UserContext]) -> str:
    time_greetings = {
        "morning": "Start with an energizing morning tone.",
        "afternoon": "Keep the tone steady and focused.",
        "evening": "Be slightly more relaxed and concise.",
    }
    return time_greetings.get(ctx.deps.time_of_day, time_greetings["afternoon"])


# Demo function
def ask_question(context: UserContext, question: str) -> str:
    print(f"\n👤 {context.name} ({context.expertise_level}, {context.preferred_language}):")
    print(f"   {question}")
    result = agent.run_sync(question, deps=context)
    print(f"🤖 Assistant: {result.output}")
    return result.output


# Run demonstrations
print("🎭 Dynamic System Prompts Demo")
print("=" * 70)
print("Same question, different personas - watch how responses adapt!\n")

question = "What is async/await in Python?"

# Scenario 1: Beginner in the morning, casual style
print("\n" + "=" * 70)
print("SCENARIO 1: Beginner learning in the morning")
context1 = UserContext(name="Alice", expertise_level="beginner", preferred_language="casual", time_of_day="morning")
ask_question(context1, question)

# Scenario 2: Expert in the evening, technical style
print("\n" + "=" * 70)
print("SCENARIO 2: Expert reviewing in the evening")
context2 = UserContext(
    name="Dr. Smith", expertise_level="expert", preferred_language="technical", time_of_day="evening"
)
ask_question(context2, question)

# Scenario 3: Intermediate, professional style
print("\n" + "=" * 70)
print("SCENARIO 3: Intermediate developer, professional setting")
context3 = UserContext(
    name="Bob", expertise_level="intermediate", preferred_language="professional", time_of_day="afternoon"
)
ask_question(context3, question)

print("\n" + "=" * 70)
print("✅ System prompts adapted dynamically based on:")
print("   - User expertise level")
print("   - Communication style preference")
print("   - Time of day context")
print("\n   This enables personalized, context-aware interactions!")
