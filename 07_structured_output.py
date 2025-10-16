#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#   "pydantic-ai==1.1.0",
#   "python-dotenv==1.1.1",
# ]
# ///

import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from pydantic_ai import Agent

# Load environment variables from .env file
load_dotenv(override=True)

model = os.getenv("MODEL")


# Define structured output models
class Task(BaseModel):
    title: str = Field(description="Task title")
    priority: str = Field(description="Priority level: high, medium, or low")
    estimated_hours: float = Field(description="Estimated hours to complete")


class TaskList(BaseModel):
    tasks: list[Task] = Field(description="List of extracted tasks")
    total_estimated_hours: float = Field(description="Sum of all estimated hours")


# Create an agent that returns structured output
agent = Agent(model, output_type=TaskList)

# Run the agent and get structured output
text = """
I need to finish the project report by Friday (about 5 hours),
review the code changes (2 hours), and update the documentation (3 hours).
Also need to respond to urgent customer emails (1 hour).
"""

print("📋 Structured Output Demo")
print("=" * 50)
result = agent.run_sync(f"Extract tasks from this text with priorities and time estimates: {text}")

# The output is automatically validated and typed
task_list: TaskList = result.output

print(f"\n✅ Extracted {len(task_list.tasks)} tasks:\n")
for i, task in enumerate(task_list.tasks, 1):
    print(f"{i}. [{task.priority.upper()}] {task.title}")
    print(f"   ⏱️  Estimated: {task.estimated_hours} hours\n")

print(f"📊 Total estimated time: {task_list.total_estimated_hours} hours")
