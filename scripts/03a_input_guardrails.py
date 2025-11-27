"""
Script 03a: Input Guardrails
=============================
Protect the business from inappropriate or off-topic requests.
Validates user input BEFORE sending to the LLM.

New Features:
- Message length validation (1-500 characters)
- Off-topic detection (politics, weather, etc.)
- Inappropriate content filtering
- Spam pattern detection
- Input validation without wasting LLM calls

To run: uv run chainlit run scripts/03a_input_guardrails.py
"""

import os
from openai import OpenAI
import chainlit as cl
from typing import Tuple

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

SYSTEM_PROMPT = """You are the AI assistant for Bella's Italian Restaurant, a family-owned Italian restaurant.

BUSINESS INFORMATION:
- Hours: Tuesday-Sunday, 11am-10pm (Closed Mondays)
  - Friday: 11am-11pm
  - Saturday: 10am-11pm (brunch from 10am-2pm)
  - Sunday: 10am-9pm (brunch from 10am-2pm)
- Services: Dine-in, takeout, delivery (via DoorDash), catering
- Location: 123 Main Street, Downtown, CA 90210
- Phone: (555) 123-4567

YOUR ROLE:
- Answer questions about the restaurant warmly and professionally
- Help with reservations and general inquiries
- Maintain a friendly, welcoming tone like a restaurant host
- If you don't know something, offer to connect them with staff

TONE: Warm, friendly, professional - like talking to a family friend who runs the restaurant
"""

# Off-topic keywords that indicate the user is asking about non-restaurant topics
OFF_TOPIC_KEYWORDS = [
    "politics", "political", "election", "president", "congress",
    "weather", "forecast", "temperature", "rain", "snow",
    "sports", "football", "basketball", "baseball", "game score",
    "medical advice", "doctor", "diagnosis", "prescription", "treatment",
    "legal advice", "lawyer", "lawsuit", "court",
    "stock", "crypto", "bitcoin", "investment"
]

# Inappropriate content keywords
INAPPROPRIATE_KEYWORDS = [
    "hate", "racist", "sexist", "violence", "weapon",
    # Add more as needed, keeping it simple for demo
]


def validate_input(message: str) -> Tuple[bool, str]:
    """
    Validate user input before processing.

    Returns:
        (is_valid, error_message): If valid, error_message is empty
    """
    # Check 1: Message length
    if len(message.strip()) == 0:
        return False, "Please send a message with at least one character."

    if len(message) > 500:
        return False, "I'd love to help! Could you please ask your question in a shorter message? I work best with concise questions (under 500 characters)."

    # Check 2: Off-topic detection
    message_lower = message.lower()
    for keyword in OFF_TOPIC_KEYWORDS:
        if keyword in message_lower:
            return False, f"I'm here to help with Bella's Italian Restaurant - reservations, menu questions, and more. For {keyword}-related information, you might want to check other resources. Can I help you with anything about our restaurant?"

    # Check 3: Inappropriate content
    for keyword in INAPPROPRIATE_KEYWORDS:
        if keyword in message_lower:
            return False, "I'm here to provide helpful information about Bella's. Let's keep our conversation respectful and focused on how I can assist you with the restaurant."

    # Check 4: Spam detection (repeated characters or very short repetitive messages)
    # Simple check: if message is the same character repeated
    unique_chars = set(message.replace(" ", ""))
    if len(unique_chars) <= 2 and len(message) > 10:
        return False, "I didn't quite understand that. How can I help you with Bella's Italian Restaurant?"

    # Check 5: Detect repeated messages (spam)
    # Get recent message from session
    recent_message = cl.user_session.get("last_user_message", "")
    if recent_message == message and len(message) > 5:
        return False, "I received your message! Is there something else I can help you with?"

    # All checks passed
    return True, ""


@cl.on_chat_start
async def start():
    """Initialize conversation with a welcome message"""
    cl.user_session.set("message_history", [])
    cl.user_session.set("last_user_message", "")

    welcome = "Buongiorno! Welcome to Bella's Italian Restaurant. I'm here to help you with reservations, menu questions, or anything else. How can I assist you today?"
    await cl.Message(content=welcome).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages with input validation"""
    # VALIDATE INPUT FIRST - before calling LLM
    is_valid, error_message = validate_input(message.content)

    if not is_valid:
        # Log the invalid attempt (in production, you'd use proper logging)
        print(f"[INPUT REJECTED] {message.content[:100]}")

        # Respond with error message WITHOUT calling LLM
        await cl.Message(content=error_message).send()
        return

    # Store this message to detect spam
    cl.user_session.set("last_user_message", message.content)

    # Input is valid - proceed with normal flow
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
