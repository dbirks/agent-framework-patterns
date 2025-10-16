#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#   "pydantic-ai==1.1.0",
#   "python-dotenv==1.1.1",
# ]
# ///
"""
Retry and Validation

Demonstrates output validation using Pydantic validators with automatic retries.
When agent output fails validation (e.g., invalid email format), the agent automatically
retries to produce valid output. Ensures data quality and format compliance.
"""

import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator
from pydantic_ai import Agent

# Load environment variables from .env file
load_dotenv(override=True)

model = os.getenv("MODEL")


# Define structured output with strict validation
class ContactInfo(BaseModel):
    name: str = Field(description="Full name of the person")
    email: str = Field(description="Email address")
    phone: str = Field(description="Phone number in format XXX-XXX-XXXX")
    age: int = Field(description="Age in years", ge=0, le=120)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[1]:
            raise ValueError("Invalid email format")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        # Simple US phone format validation
        import re

        if not re.match(r"^\d{3}-\d{3}-\d{4}$", v):
            raise ValueError("Phone must be in format XXX-XXX-XXXX")
        return v


# Create an agent with structured output and validation
agent = Agent(
    model,
    output_type=ContactInfo,
    system_prompt="Extract contact information. Ensure email and phone are properly formatted.",
)

# Test with valid data
print("🔄 Retry & Validation Demo")
print("=" * 50)

text = "Contact John Smith at john.smith@example.com or call 555-123-4567. He's 35 years old."

print(f"\nExtracting contact info from:\n{text}\n")
try:
    result = agent.run_sync(f"Extract contact information: {text}")
    contact: ContactInfo = result.output

    print("✅ Validation successful!")
    print(f"\nName: {contact.name}")
    print(f"Email: {contact.email}")
    print(f"Phone: {contact.phone}")
    print(f"Age: {contact.age}")
except Exception as e:
    print(f"❌ Validation failed: {e}")

# Test with invalid data to show retry behavior
print("\n" + "=" * 50)
print("\nTesting with potentially invalid data...")
invalid_text = "Reach Jane Doe, she's reachable somehow, probably around 28"

try:
    result = agent.run_sync(f"Extract contact information: {invalid_text}")
    print("✅ Agent successfully handled missing/invalid data")
    print(f"Result: {result.output}")
except Exception as e:
    print(f"❌ Could not extract valid contact info: {e}")
