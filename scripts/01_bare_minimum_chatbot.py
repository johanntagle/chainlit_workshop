"""
Script 01: Bare Minimum Chatbot
================================
The absolute simplest Chainlit chatbot possible.
Shows how easy it is to get started - under 20 lines!

Key Learning: "This is how easy it is to get started"

To run: uv run chainlit run scripts/01_bare_minimum_chatbot.py
"""

import os
from openai import OpenAI
import chainlit as cl

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

@cl.on_message
async def main(message: cl.Message):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": message.content}]
    )

    await cl.Message(content=response.choices[0].message.content).send()
