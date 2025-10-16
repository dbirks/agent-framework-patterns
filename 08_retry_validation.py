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
When agent output fails validation, the agent automatically retries to produce valid output.
"""

import os
import re

import logfire
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator
from pydantic_ai import Agent

load_dotenv(override=True)
model = os.getenv("MODEL")
logfire.configure(send_to_logfire=False)
logfire.instrument_pydantic_ai()


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
        if not re.match(r"^\d{3}-\d{3}-\d{4}$", v):
            raise ValueError("Phone must be in format XXX-XXX-XXXX")
        return v


agent = Agent(
    model,
    output_type=ContactInfo,
    system_prompt="Extract contact information. Ensure email and phone are properly formatted.",
)

text = "Contact John Smith at john.smith@example.com or call 555-123-4567. He's 35 years old."

result = agent.run_sync(f"Extract contact information: {text}")
contact = result.output

print(f"Name: {contact.name}")
print(f"Email: {contact.email}")
print(f"Phone: {contact.phone}")
print(f"Age: {contact.age}")
