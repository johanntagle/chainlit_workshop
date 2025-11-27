"""
Script 04b: Tools - Reservation Creation
=========================================
Adds ability to actually create reservations!
Shows multi-tool orchestration and conversational data collection.

New Features:
- create_reservation tool
- Multi-turn conversation to collect all required details
- Phone number validation
- Confirmation number generation
- Complete reservation summary

To run: uv run chainlit run scripts/04b_tools_reservation.py
"""

import os
import json
import re
import random
from datetime import datetime
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
- Location: 123 Main Street, Downtown, CA 90210
- Phone: (555) 123-4567

YOUR ROLE:
- Help guests check table availability and make reservations
- Collect required information conversationally (name, phone, date, time, party size)
- Answer questions warmly and professionally
- Use check_availability first, then create_reservation once availability is confirmed

WORKFLOW FOR RESERVATIONS:
1. Check availability with check_availability tool
2. If available, collect: name, phone number
3. Create reservation with create_reservation tool
4. Provide confirmation details

TONE: Warm, friendly, professional - guide guests through the process naturally
"""

# Tool definitions
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check if a table is available for the requested date, time, and party size",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                    "time": {"type": "string", "description": "Time in HH:MM 24-hour format"},
                    "party_size": {"type": "integer", "description": "Number of guests (1-20)"}
                },
                "required": ["date", "time", "party_size"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_reservation",
            "description": "Create a restaurant reservation after availability has been confirmed",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Guest's full name"},
                    "phone": {"type": "string", "description": "Guest's phone number"},
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                    "time": {"type": "string", "description": "Time in HH:MM 24-hour format"},
                    "party_size": {"type": "integer", "description": "Number of guests"},
                    "special_requests": {"type": "string", "description": "Any special requests or notes (optional)"}
                },
                "required": ["name", "phone", "date", "time", "party_size"]
            }
        }
    }
]


@cl.step(name="Check Availability", type="tool")
async def check_availability(date: str, time: str, party_size: int) -> dict:
    """Check table availability (mock implementation)"""
    try:
        booking_date = datetime.strptime(date, "%Y-%m-%d")
        booking_time = datetime.strptime(time, "%H:%M")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        if booking_date < today:
            return {"available": False, "message": "Cannot book tables in the past."}

        if booking_date.weekday() == 0:  # Monday
            return {"available": False, "message": "We're closed on Mondays."}

        hour = booking_time.hour

        # Simple availability check
        if party_size >= 8:
            return {
                "available": False,
                "message": f"For parties of {party_size}, please call (555) 123-4567 for our private dining room."
            }

        # Peak hours have some unavailability
        if 18 <= hour < 20 and random.random() < 0.3:
            return {
                "available": False,
                "message": f"Fully booked at {time}. Try 5:00 PM, 5:30 PM, or 8:00 PM.",
                "alternative_times": ["17:00", "17:30", "20:00"]
            }

        formatted_date = booking_date.strftime("%A, %B %d, %Y")
        formatted_time = booking_time.strftime("%I:%M %p")

        return {
            "available": True,
            "message": f"Table available on {formatted_date} at {formatted_time} for {party_size} guests!",
            "date": date,
            "time": time,
            "party_size": party_size
        }

    except ValueError:
        return {"available": False, "message": "Invalid date or time format."}


@cl.step(name="Create Reservation", type="tool")
async def create_reservation(
    name: str,
    phone: str,
    date: str,
    time: str,
    party_size: int,
    special_requests: str = ""
) -> dict:
    """
    Create a reservation (mock implementation).

    In production, this would integrate with a real booking system.
    """
    # Validate phone number (simple validation)
    phone_clean = re.sub(r'[^\d]', '', phone)
    if len(phone_clean) < 10:
        return {
            "success": False,
            "message": "Please provide a valid 10-digit phone number."
        }

    # Format phone number
    if len(phone_clean) == 10:
        formatted_phone = f"({phone_clean[:3]}) {phone_clean[3:6]}-{phone_clean[6:]}"
    elif len(phone_clean) == 11 and phone_clean[0] == '1':
        formatted_phone = f"({phone_clean[1:4]}) {phone_clean[4:7]}-{phone_clean[7:]}"
    else:
        formatted_phone = phone

    # Generate confirmation number
    confirmation_number = f"BELLA-{random.randint(100000, 999999)}"

    # Format date and time for display
    booking_date = datetime.strptime(date, "%Y-%m-%d")
    booking_time = datetime.strptime(time, "%H:%M")
    formatted_date = booking_date.strftime("%A, %B %d, %Y")
    formatted_time = booking_time.strftime("%I:%M %p")

    # Mock: Save to database (in production)
    print(f"[RESERVATION CREATED] {confirmation_number} - {name}, {formatted_phone}, {formatted_date} {formatted_time}, Party of {party_size}")

    return {
        "success": True,
        "confirmation_number": confirmation_number,
        "name": name,
        "phone": formatted_phone,
        "date": formatted_date,
        "time": formatted_time,
        "party_size": party_size,
        "special_requests": special_requests,
        "message": f"Reservation confirmed! Confirmation number: {confirmation_number}"
    }


def validate_input(message: str) -> Tuple[bool, str]:
    """Validate user input"""
    if len(message.strip()) == 0:
        return False, "Please send a message."
    if len(message) > 500:
        return False, "Please keep messages under 500 characters."
    return True, ""


@cl.on_chat_start
async def start():
    """Initialize conversation"""
    cl.user_session.set("message_history", [])

    welcome = "Buongiorno! Welcome to Bella's Italian Restaurant. I can help you check availability and make reservations. What can I do for you today?"
    await cl.Message(content=welcome).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle messages with multi-tool support"""
    # Validate input
    is_valid, error_message = validate_input(message.content)
    if not is_valid:
        await cl.Message(content=error_message).send()
        return

    # Get message history
    message_history = cl.user_session.get("message_history", [])
    message_history.append({"role": "user", "content": message.content})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + message_history

    # Call OpenAI with tools
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
    )

    assistant_message = response.choices[0].message

    # Handle tool calls
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

        # Execute tool calls
        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            if function_name == "check_availability":
                result = await check_availability(
                    date=args["date"],
                    time=args["time"],
                    party_size=args["party_size"]
                )
            elif function_name == "create_reservation":
                result = await create_reservation(
                    name=args["name"],
                    phone=args["phone"],
                    date=args["date"],
                    time=args["time"],
                    party_size=args["party_size"],
                    special_requests=args.get("special_requests", "")
                )
            else:
                result = {"error": "Unknown function"}

            # Add tool result to history
            message_history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

        # Get final response with tool results
        final_response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + message_history
        )

        final_message = final_response.choices[0].message.content
        await cl.Message(content=final_message).send()
        message_history.append({"role": "assistant", "content": final_message})

    else:
        # No tool call, just respond
        await cl.Message(content=assistant_message.content).send()
        message_history.append({"role": "assistant", "content": assistant_message.content})

    cl.user_session.set("message_history", message_history)
