"""
Script 03b: Output Guardrails
==============================
Prevent hallucinations and ensure accurate business information.
Detects when issues need human escalation.

New Features:
- Enhanced system prompt with strict output rules
- Never make up information (must say "I don't know")
- Never quote prices without verification
- Escalation detection for complaints/serious issues
- Human handoff protocol

To run: uv run chainlit run scripts/03b_output_guardrails.py
"""

import os
from openai import OpenAI
import chainlit as cl
from typing import Tuple

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

# Enhanced system prompt with strict output rules
SYSTEM_PROMPT = """You are the AI assistant for Bella's Italian Restaurant, a family-owned Italian restaurant.

BUSINESS INFORMATION:
- Hours: Tuesday-Sunday, 11am-10pm (Closed Mondays)
  - Friday: 11am-11pm
  - Saturday: 10am-11pm (brunch from 10am-2pm)
  - Sunday: 10am-9pm (brunch from 10am-2pm)
- Services: Dine-in, takeout, delivery (via DoorDash), catering
- Location: 123 Main Street, Downtown, CA 90210
- Phone: (555) 123-4567
- Email: info@bellasitalian.com

YOUR ROLE:
- Answer questions about the restaurant warmly and professionally
- Help with reservations and general inquiries
- Maintain a friendly, welcoming tone like a restaurant host

CRITICAL RULES - YOU MUST FOLLOW THESE:
1. If you don't know something, say "I don't have that information. Let me connect you with our staff who can help."
2. NEVER make up menu items, prices, or policies
3. NEVER confirm reservations - always say "I can help you check availability and start the reservation process"
4. For complaints or serious issues, IMMEDIATELY offer to escalate to a manager
5. For health/safety concerns (food poisoning, allergies, injuries), escalate IMMEDIATELY
6. If asked about specific pricing, say you can provide general information but recommend calling for exact current prices

TONE: Warm, friendly, professional - but safety and accuracy come FIRST
"""

OFF_TOPIC_KEYWORDS = [
    "politics", "political", "election", "president", "congress",
    "weather", "forecast", "temperature", "rain", "snow",
    "sports", "football", "basketball", "baseball", "game score",
    "medical advice", "doctor", "diagnosis", "prescription", "treatment",
    "legal advice", "lawyer", "lawsuit", "court",
    "stock", "crypto", "bitcoin", "investment"
]

INAPPROPRIATE_KEYWORDS = ["hate", "racist", "sexist", "violence", "weapon"]

# Keywords that trigger immediate escalation to human staff
ESCALATION_TRIGGERS = [
    "complaint", "complain", "angry", "upset", "furious", "disappointed",
    "refund", "money back", "charge", "overcharged",
    "manager", "supervisor", "owner", "speak to someone",
    "allergic reaction", "food poisoning", "sick", "ill", "vomit", "hospital",
    "legal", "lawyer", "sue", "lawsuit",
    "wrong order", "cold food", "undercooked", "raw", "hair in food",
    "rude", "unprofessional", "terrible service"
]


def validate_input(message: str) -> Tuple[bool, str]:
    """Validate user input before processing"""
    if len(message.strip()) == 0:
        return False, "Please send a message with at least one character."

    if len(message) > 500:
        return False, "I'd love to help! Could you please ask your question in a shorter message? I work best with concise questions (under 500 characters)."

    message_lower = message.lower()

    for keyword in OFF_TOPIC_KEYWORDS:
        if keyword in message_lower:
            return False, f"I'm here to help with Bella's Italian Restaurant - reservations, menu questions, and more. For {keyword}-related information, you might want to check other resources. Can I help you with anything about our restaurant?"

    for keyword in INAPPROPRIATE_KEYWORDS:
        if keyword in message_lower:
            return False, "I'm here to provide helpful information about Bella's. Let's keep our conversation respectful and focused on how I can assist you with the restaurant."

    unique_chars = set(message.replace(" ", ""))
    if len(unique_chars) <= 2 and len(message) > 10:
        return False, "I didn't quite understand that. How can I help you with Bella's Italian Restaurant?"

    recent_message = cl.user_session.get("last_user_message", "")
    if recent_message == message and len(message) > 5:
        return False, "I received your message! Is there something else I can help you with?"

    return True, ""


def check_for_escalation(message: str) -> Tuple[bool, str]:
    """
    Check if the message contains escalation triggers that require human intervention.

    Returns:
        (needs_escalation, escalation_type): If escalation needed, type describes the issue
    """
    message_lower = message.lower()

    for trigger in ESCALATION_TRIGGERS:
        if trigger in message_lower:
            # Categorize the type of escalation
            if trigger in ["allergic reaction", "food poisoning", "sick", "ill", "vomit", "hospital"]:
                return True, "health_emergency"
            elif trigger in ["legal", "lawyer", "sue", "lawsuit"]:
                return True, "legal_issue"
            elif trigger in ["refund", "money back", "charge", "overcharged"]:
                return True, "financial_dispute"
            elif trigger in ["manager", "supervisor", "owner"]:
                return True, "management_request"
            else:
                return True, "complaint"

    return False, ""


async def handle_escalation(escalation_type: str, user_message: str) -> str:
    """Generate appropriate escalation response based on issue type"""

    # Log the escalation (in production, this would alert staff)
    print(f"[ESCALATION - {escalation_type.upper()}] {user_message[:100]}")

    if escalation_type == "health_emergency":
        return """I'm very sorry to hear you're not feeling well. This is important and needs immediate attention from our management team.

Please call us right away at (555) 123-4567 so we can address this properly, or give me your phone number and I'll have a manager call you within the hour.

Your health and safety are our top priority."""

    elif escalation_type == "legal_issue":
        return """I understand this is a serious matter. For legal concerns, please contact our management directly:

Phone: (555) 123-4567
Email: info@bellasitalian.com

They will be able to discuss this with you properly and provide you with the appropriate contact information."""

    elif escalation_type == "financial_dispute":
        return """I apologize for any billing concerns. Let me get you connected with someone who can review your charges and help resolve this.

Please call us at (555) 123-4567 and ask to speak with a manager, or provide your phone number and I'll have them call you back shortly.

We want to make sure this is handled correctly."""

    elif escalation_type == "management_request":
        return """I'd be happy to connect you with our management team.

You can reach them directly at (555) 123-4567, or if you'd prefer, give me your phone number and preferred time, and I'll have a manager call you back.

What works best for you?"""

    else:  # General complaint
        return """I'm sorry to hear you had a disappointing experience. Your feedback is important to us, and I want to make sure this is addressed properly.

Please call us at (555) 123-4567 to speak with a manager, or give me your phone number and I'll have someone from our management team call you back today.

We appreciate your patience and want to make this right."""


@cl.on_chat_start
async def start():
    """Initialize conversation with a welcome message"""
    cl.user_session.set("message_history", [])
    cl.user_session.set("last_user_message", "")

    welcome = "Buongiorno! Welcome to Bella's Italian Restaurant. I'm here to help you with reservations, menu questions, or anything else. How can I assist you today?"
    await cl.Message(content=welcome).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages with input validation and escalation detection"""
    # Step 1: Validate input
    is_valid, error_message = validate_input(message.content)

    if not is_valid:
        print(f"[INPUT REJECTED] {message.content[:100]}")
        await cl.Message(content=error_message).send()
        return

    cl.user_session.set("last_user_message", message.content)

    # Step 2: Check for escalation triggers
    needs_escalation, escalation_type = check_for_escalation(message.content)

    if needs_escalation:
        # Handle escalation immediately without going to LLM
        escalation_response = await handle_escalation(escalation_type, message.content)
        await cl.Message(content=escalation_response).send()
        return

    # Step 3: Normal processing
    message_history = cl.user_session.get("message_history", [])
    message_history.append({"role": "user", "content": message.content})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + message_history

    stream = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        stream=True
    )

    msg = cl.Message(content="")
    await msg.send()

    full_response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_response += content
            await msg.stream_token(content)

    await msg.update()

    message_history.append({"role": "assistant", "content": full_response})
    cl.user_session.set("message_history", message_history)
