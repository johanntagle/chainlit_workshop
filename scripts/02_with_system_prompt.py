"""
Script 02: With System Prompt
==============================
Adds personality and business context to the chatbot.
Now it feels like talking to Bella's Italian Restaurant!

New Features:
- System prompt with business personality
- Welcome message on chat start
- Conversation memory (message history)
- Streaming responses for better UX

To run: chainlit run scripts/02_with_system_prompt.py
"""

import os
from openai import OpenAI
import chainlit as cl

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# System prompt defines the bot's personality and knowledge
SYSTEM_PROMPT = """You are the AI assistant for Bella's Italian Restaurant, a family-owned Italian restaurant.

BUSINESS INFORMATION:
- Hours: Tuesday-Sunday, 11am-10pm (Closed Mondays)
  - Friday: 11am-11pm
  - Saturday: 10am-11pm (brunch from 10am-2pm)
  - Sunday: 10am-9pm (brunch from 10am-2pm)
- Services: Dine-in, takeout, delivery (via DoorDash), catering
- Location: 123 Main Street, Downtown, CA 90210
- Phone: (555) 123-4567
- We validate parking at Main Street Garage (2 hours free)

YOUR ROLE:
- Answer questions about the restaurant warmly and professionally
- Help with reservations and general inquiries
- Maintain a friendly, welcoming tone like a restaurant host
- If you don't know something, offer to connect them with staff

TONE: Warm, friendly, professional - like talking to a family friend who runs the restaurant
"""


@cl.on_chat_start
async def start():
    """Initialize conversation with a welcome message"""
    # Store message history in user session
    cl.user_session.set("message_history", [])

    welcome = "Buongiorno! Welcome to Bella's Italian Restaurant. I'm here to help you with reservations, menu questions, or anything else. How can I assist you today?"
    await cl.Message(content=welcome).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages with streaming response"""
    # Get message history from session
    message_history = cl.user_session.get("message_history", [])

    # Add user message to history
    message_history.append({"role": "user", "content": message.content})

    # Create the full message list with system prompt
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + message_history

    # Create streaming response
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True
    )

    # Stream the response to the user
    msg = cl.Message(content="")
    await msg.send()

    full_response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_response += content
            await msg.stream_token(content)

    await msg.update()

    # Add assistant response to history
    message_history.append({"role": "assistant", "content": full_response})
    cl.user_session.set("message_history", message_history)
