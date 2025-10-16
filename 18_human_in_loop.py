#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.14,<3.15"
# dependencies = [
#   "pydantic-ai==1.1.0",
#   "python-dotenv==1.1.1",
#   "rich==14.2.0",
# ]
# ///
"""
Human-in-the-Loop Negotiation

Demonstrates multi-agent negotiation with human approval. Your AI negotiator works
with you to buy goats from an unpredictable seller. Type 'buy' to seal the deal,
or provide feedback for your agent to continue negotiating.
"""

import os
from textwrap import dedent

import logfire
from dotenv import load_dotenv
from pydantic_ai import Agent
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

load_dotenv(override=True)
model = os.getenv("MODEL")
logfire.configure(send_to_logfire=False)
logfire.instrument_pydantic_ai()

# Unpredictable seller agent
seller_agent = Agent(
    "anthropic:claude-haiku-4-5",
    system_prompt=dedent(
        """
        You're a goat farmer selling your herd. You have 50 goats.

        Your pricing: Start at $200/goat but you'll go as low as $150/goat.

        Be unpredictable and colorful:
        - Sometimes get offended and raise prices
        - Sometimes ramble about your goats' names or personalities
        - Sometimes offer weird terms (trade for chickens, singing lessons, etc)
        - Sometimes be shrewd, sometimes be generous
        - Keep it entertaining but eventually work toward a deal

        Format your response as a natural conversation. Be expressive!
        """
    ).strip(),
    instrument=True,
)

# Your negotiator agent
negotiator_agent = Agent(
    model,
    system_prompt=dedent(
        """
        You're helping your client buy goats. Budget: $8000 total.

        Your job:
        1. Negotiate with the seller based on their offers
        2. When showing offers to your client, format them clearly with:
           - Current offer details (price, quantity, terms)
           - Your analysis and recommendation
           - What you plan to say next if they approve

        Be strategic but respect your client's feedback. If they want changes,
        incorporate their wishes into your negotiation strategy.

        Format your output as markdown with clear sections.
        """
    ).strip(),
    instrument=True,
)

console.print("\n[bold cyan]🐐 Goat Negotiation Simulator[/bold cyan]\n")
console.print("[dim]Type 'buy' to accept a deal, or give feedback to continue negotiating[/dim]\n")

logfire.info("Starting negotiation")

# Get seller's opening offer
seller_response = seller_agent.run_sync("Make your opening pitch to sell your goats.")
logfire.info(f"Seller opened: {seller_response.output[:100]}")

conversation_history = f"Seller said: {seller_response.output}"

while True:
    # Our agent analyzes and presents to us
    logfire.info("Negotiator preparing proposal")

    negotiator_response = negotiator_agent.run_sync(
        f"Here's the conversation so far:\n\n{conversation_history}\n\n"
        f"Present the current situation to your client and recommend next steps."
    )

    console.print(Panel(Markdown(negotiator_response.output), title="Your Negotiator", border_style="blue"))

    # Get human input
    user_input = Prompt.ask("\n[bold green]Your decision[/bold green]").strip()

    if user_input.lower() == "buy":
        console.print("\n[bold green]🤝 Deal sealed![/bold green]\n")
        logfire.info("Deal accepted by human")
        break

    # User gave feedback - negotiate more rounds
    logfire.info(f"Human feedback: {user_input}")
    console.print()

    # Agent takes feedback and negotiates with seller
    for round_num in range(3):  # Up to 3 rounds of back-and-forth
        logfire.info(f"Negotiation round {round_num + 1}")

        agent_prompt = f"""
Previous conversation:
{conversation_history}

Your client said: "{user_input}"

Respond to the seller based on your client's feedback. Be natural and conversational.
"""

        negotiator_response = negotiator_agent.run_sync(agent_prompt)
        logfire.info(f"Negotiator says: {negotiator_response.output[:100]}")

        conversation_history += f"\n\nYou: {negotiator_response.output}"

        # Seller responds
        seller_response = seller_agent.run_sync(
            f"Previous conversation:\n{conversation_history}\n\n"
            f"The buyer said: {negotiator_response.output}\n\n"
            f"Respond to their offer or counteroffer."
        )

        logfire.info(f"Seller responds: {seller_response.output[:100]}")
        conversation_history += f"\n\nSeller: {seller_response.output}"

    # After negotiation rounds, show update
    console.print(
        Panel(
            Markdown(f"**Latest from seller:**\n\n{seller_response.output}"),
            title="Seller's Response",
            border_style="red",
        )
    )
