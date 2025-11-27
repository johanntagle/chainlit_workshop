"""
Script 04a: Tools - Availability Checking
==========================================
Introduces OpenAI function calling with a table availability checker.
The bot can now take actions, not just answer questions!

New Features:
- OpenAI function calling / tools
- check_availability tool for table bookings
- @cl.step decorator for UI visibility
- Multi-turn conversation to collect missing parameters
- Mock availability logic based on party size and time

To run: chainlit run scripts/04a_tools_availability.py
"""

import os
import json
from datetime import datetime, timedelta
from openai import OpenAI
import chainlit as cl
from typing import Tuple
import random

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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
- Help guests check table availability
- Answer questions warmly and professionally
- Use the check_availability tool when guests ask about reservations
- If you need more information (date, time, party size), ask conversationally

CRITICAL RULES:
1. If you don't know something, say "I don't have that information."
2. NEVER make up menu items, prices, or policies
3. Always use the check_availability tool to verify table availability
4. For complaints or serious issues, offer to escalate to a manager

TONE: Warm, friendly, professional
"""

# Tool definition for OpenAI function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check if a table is available for the requested date, time, and party size at Bella's Italian Restaurant",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format (e.g., 2024-12-25)"
                    },
                    "time": {
                        "type": "string",
                        "description": "Time in HH:MM format using 24-hour time (e.g., 19:00 for 7pm)"
                    },
                    "party_size": {
                        "type": "integer",
                        "description": "Number of guests (1-20)"
                    }
                },
                "required": ["date", "time", "party_size"]
            }
        }
    }
]


@cl.step(name="Check Availability", type="tool")
async def check_availability(date: str, time: str, party_size: int) -> dict:
    """
    Check table availability (mock implementation for workshop).

    In production, this would connect to a real booking system.
    """
    try:
        # Parse and validate inputs
        booking_date = datetime.strptime(date, "%Y-%m-%d")
        booking_time = datetime.strptime(time, "%H:%M")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Validation checks
        if booking_date < today:
            return {
                "available": False,
                "message": "I can't book tables in the past. Please choose a future date.",
                "alternative_times": []
            }

        # Check if it's Monday (closed)
        if booking_date.weekday() == 0:  # Monday is 0
            return {
                "available": False,
                "message": "We're closed on Mondays. We're open Tuesday-Sunday. Would you like to book for another day?",
                "alternative_times": []
            }

        # Check if time is within business hours
        hour = booking_time.hour
        day_of_week = booking_date.weekday()

        # Business hours check
        if day_of_week == 4:  # Friday (open until 11pm)
            if hour < 11 or hour >= 23:
                return {
                    "available": False,
                    "message": "We're open 11am-11pm on Fridays. Please choose a time within our hours.",
                    "alternative_times": ["18:00", "18:30", "19:00"]
                }
        elif day_of_week in [5, 6]:  # Saturday and Sunday (brunch from 10am)
            if day_of_week == 5:  # Saturday (until 11pm)
                if hour < 10 or hour >= 23:
                    return {
                        "available": False,
                        "message": "We're open 10am-11pm on Saturdays. Please choose a time within our hours.",
                        "alternative_times": ["18:00", "18:30", "19:00"]
                    }
            else:  # Sunday (until 9pm)
                if hour < 10 or hour >= 21:
                    return {
                        "available": False,
                        "message": "We're open 10am-9pm on Sundays. Please choose a time within our hours.",
                        "alternative_times": ["17:00", "17:30", "18:00"]
                    }
        else:  # Tuesday-Thursday (11am-10pm)
            if hour < 11 or hour >= 22:
                return {
                    "available": False,
                    "message": "We're open 11am-10pm on weekdays. Please choose a time within our hours.",
                    "alternative_times": ["18:00", "18:30", "19:00"]
                }

        # Check party size
        if party_size < 1:
            return {
                "available": False,
                "message": "Please specify at least 1 guest.",
                "alternative_times": []
            }

        if party_size > 20:
            return {
                "available": False,
                "message": "For parties larger than 20 guests, please call us directly at (555) 123-4567 to discuss private event options.",
                "alternative_times": []
            }

        # Mock availability logic
        # Large parties (8+) are often unavailable
        if party_size >= 8:
            return {
                "available": False,
                "message": f"For parties of {party_size}, we recommend our private dining room. Please call (555) 123-4567 to arrange this special booking.",
                "alternative_times": []
            }

        # Peak hours (6pm-8pm) have 50% chance of being unavailable
        if 18 <= hour < 20:
            if random.random() < 0.5:
                # Generate alternative times
                alternatives = []
                for offset in [-2, -1, 1, 2]:
                    alt_hour = hour + offset
                    if 11 <= alt_hour < 22:
                        alternatives.append(f"{alt_hour:02d}:00")

                return {
                    "available": False,
                    "message": f"Unfortunately, we're fully booked at {time} on {date}. However, we have tables available at nearby times.",
                    "alternative_times": alternatives[:3]
                }

        # Otherwise, table is available
        formatted_date = booking_date.strftime("%A, %B %d, %Y")
        formatted_time = booking_time.strftime("%I:%M %p")

        return {
            "available": True,
            "message": f"Great news! We have tables available on {formatted_date} at {formatted_time} for {party_size} guests.",
            "date": date,
            "time": time,
            "party_size": party_size
        }

    except ValueError as e:
        return {
            "available": False,
            "message": f"I had trouble understanding that date or time. Please use format YYYY-MM-DD for date and HH:MM for time.",
            "alternative_times": []
        }


def validate_input(message: str) -> Tuple[bool, str]:
    """Validate user input before processing"""
    if len(message.strip()) == 0:
        return False, "Please send a message with at least one character."
    if len(message) > 500:
        return False, "I'd love to help! Could you please ask your question in a shorter message?"
    return True, ""


@cl.on_chat_start
async def start():
    """Initialize conversation"""
    cl.user_session.set("message_history", [])

    welcome = "Buongiorno! Welcome to Bella's Italian Restaurant. I can help you check table availability and answer any questions. What can I do for you today?"
    await cl.Message(content=welcome).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages with tool support"""
    # Validate input
    is_valid, error_message = validate_input(message.content)
    if not is_valid:
        await cl.Message(content=error_message).send()
        return

    # Get message history
    message_history = cl.user_session.get("message_history", [])
    message_history.append({"role": "user", "content": message.content})

    # Prepare messages for OpenAI
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + message_history

    # Call OpenAI with tools
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
    )

    assistant_message = response.choices[0].message

    # Check if the model wants to call a tool
    if assistant_message.tool_calls:
        # Add assistant message to history
        message_history.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                } for tc in assistant_message.tool_calls
            ]
        })

        # Execute each tool call
        for tool_call in assistant_message.tool_calls:
            if tool_call.function.name == "check_availability":
                # Parse arguments
                args = json.loads(tool_call.function.arguments)

                # Call the function
                result = await check_availability(
                    date=args["date"],
                    time=args["time"],
                    party_size=args["party_size"]
                )

                # Add tool result to message history
                message_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

        # Get final response from OpenAI with tool results
        final_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + message_history
        )

        final_message = final_response.choices[0].message.content
        await cl.Message(content=final_message).send()

        message_history.append({"role": "assistant", "content": final_message})

    else:
        # No tool call, just send the response
        await cl.Message(content=assistant_message.content).send()
        message_history.append({"role": "assistant", "content": assistant_message.content})

    cl.user_session.set("message_history", message_history)
