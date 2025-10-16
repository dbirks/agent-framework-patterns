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

Demonstrates interactive approval workflow where a human negotiates a business deal
with AI assistance. Your agent makes offers, you approve or modify them, and another
agent plays the seller. Shows multi-agent coordination with human decision points.
"""

import os
from textwrap import dedent
from typing import cast

import logfire
from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

console = Console()

load_dotenv(override=True)
model = os.getenv("MODEL")
logfire.configure(send_to_logfire=False)
logfire.instrument_pydantic_ai()


class Offer(BaseModel):
    price: int
    quantity: int
    terms: str
    reasoning: str


# Seller agent - plays the other business partner
seller_agent = Agent(
    "anthropic:claude-haiku-4-5",
    output_type=Offer,
    system_prompt=dedent(
        """
        You're a goat farmer trying to sell your herd. You have 50 healthy goats.

        Your bottom line: You need at least $150 per goat to make it worthwhile.
        Your starting position: Ask for $200 per goat.

        Be a shrewd negotiator but willing to compromise. Consider:
        - Buying more goats should get a better per-goat price
        - You prefer selling the whole herd at once
        - Payment terms matter (cash upfront is worth a discount)

        Make counteroffers that move toward a deal but protect your interests.
        """
    ).strip(),
    instrument=True,
)

# Negotiator agent - your AI advisor
negotiator_agent = Agent(
    model,
    output_type=Offer,
    system_prompt=dedent(
        """
        You're a business negotiator helping your client buy goats for their farm.

        Your client's budget: $8000 total
        Your goal: Get as many goats as possible at the best price

        Analyze the seller's offers and make smart counteroffers that:
        - Work toward a deal
        - Respect your client's budget
        - Look for win-win terms (bulk discount, payment terms, etc)

        Be professional but firm in negotiations.
        """
    ).strip(),
    instrument=True,
)


def display_offer(title: str, offer: Offer, color: str):
    """Display an offer in a nice panel."""
    content = f"""
**Price per goat:** ${offer.price}
**Quantity:** {offer.quantity} goats
**Total:** ${offer.price * offer.quantity}

**Terms:** {offer.terms}

*{offer.reasoning}*
"""
    console.print(Panel(Markdown(content), title=title, border_style=color))


console.print("\n[bold cyan]Goat Negotiation Simulator[/bold cyan]")
console.print("[dim]You're buying goats for your farm. Your AI negotiator will help you make deals.[/dim]\n")

logfire.info("Starting negotiation session")

# Round 1: Seller makes opening offer
console.print("[bold yellow]Round 1: Opening Offer[/bold yellow]\n")
logfire.info("Seller making opening offer")

seller_result = seller_agent.run_sync("Make your opening offer for selling goats.")
seller_offer = cast(Offer, seller_result.output)

display_offer("Seller's Opening Offer", seller_offer, "red")
logfire.info(f"Seller offers: {seller_offer.quantity} goats at ${seller_offer.price} each")

# Negotiation loop
round_num = 2
max_rounds = 5

for round_num in range(2, max_rounds + 1):
    console.print(f"\n[bold yellow]Round {round_num}: Your Turn[/bold yellow]\n")

    # Our negotiator analyzes and prepares counteroffer
    logfire.info("Negotiator preparing counteroffer")

    history = f"""
Seller's last offer:
- {seller_offer.quantity} goats at ${seller_offer.price} each (${seller_offer.price * seller_offer.quantity} total)
- Terms: {seller_offer.terms}
- Their reasoning: {seller_offer.reasoning}
"""

    negotiator_result = negotiator_agent.run_sync(f"The seller made this offer:\n{history}\n\nMake your counteroffer.")
    our_offer = cast(Offer, negotiator_result.output)

    logfire.info(f"Negotiator suggests: {our_offer.quantity} goats at ${our_offer.price} each")

    display_offer("Your AI Negotiator Suggests", our_offer, "blue")

    # Human approval step
    console.print()
    approved = Confirm.ask("[bold green]Accept this counteroffer?[/bold green]")

    if not approved:
        logfire.info("Human rejected AI suggestion, requesting modifications")
        console.print()
        new_price = Prompt.ask("What price per goat?", default=str(our_offer.price))
        new_quantity = Prompt.ask("How many goats?", default=str(our_offer.quantity))
        new_terms = Prompt.ask("Any special terms?", default=our_offer.terms)

        our_offer.price = int(new_price)
        our_offer.quantity = int(new_quantity)
        our_offer.terms = new_terms
        our_offer.reasoning = "Modified by human negotiator based on their preferences"

        logfire.info(f"Human modified offer: {our_offer.quantity} goats at ${our_offer.price} each")
        console.print()
        display_offer("Your Modified Counteroffer", our_offer, "green")
    else:
        logfire.info("Human approved AI suggestion")

    # Check if we have a deal based on reasonable terms
    total_cost = our_offer.price * our_offer.quantity
    seller_total = seller_offer.price * seller_offer.quantity

    if abs(total_cost - seller_total) < 500 and abs(our_offer.quantity - seller_offer.quantity) <= 5:
        console.print(f"\n[bold green]🤝 Deal reached![/bold green]")
        console.print(f"[green]Final terms: {our_offer.quantity} goats at ${our_offer.price} each[/green]")
        console.print(f"[green]Total: ${total_cost}[/green]\n")
        logfire.info(f"Deal reached: {our_offer.quantity} goats at ${our_offer.price} each")
        break

    # Seller responds to our counteroffer
    console.print(f"\n[bold yellow]Round {round_num + 1}: Seller's Response[/bold yellow]\n")
    logfire.info("Sending counteroffer to seller")

    seller_result = seller_agent.run_sync(
        f"Buyer countered with: {our_offer.quantity} goats at ${our_offer.price} each. "
        f"Terms: {our_offer.terms}. Their reasoning: {our_offer.reasoning}. "
        f"Make your counteroffer."
    )
    seller_offer = cast(Offer, seller_result.output)

    display_offer("Seller's Counteroffer", seller_offer, "red")
    logfire.info(f"Seller counters: {seller_offer.quantity} goats at ${seller_offer.price} each")

else:
    console.print("\n[bold red]❌ No deal reached after {max_rounds} rounds[/bold red]\n")
    logfire.warn(f"Negotiation failed after {max_rounds} rounds")
