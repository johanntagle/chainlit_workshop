"""
Script 04c: Tools - Menu and Business Information
==================================================
Adds tools to query menu items and business information from JSON files.
Shows how to integrate with existing business data.

New Features:
- get_menu_info tool (queries menu.json)
- get_business_info tool (queries business_info.json)
- Load JSON data at startup
- Filter and search capabilities

To run: chainlit run scripts/04c_tools_menu_business.py
"""

import os
import json
import re
import random
from datetime import datetime
from pathlib import Path
from openai import OpenAI
import chainlit as cl
from typing import Tuple, Optional

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Load business data at startup
BASE_DIR = Path(__file__).parent.parent
MENU_PATH = BASE_DIR / "data" / "restaurant" / "menu.json"
BUSINESS_INFO_PATH = BASE_DIR / "data" / "restaurant" / "business_info.json"

# Global variables to store loaded data
MENU_DATA = {}
BUSINESS_INFO = {}


def load_data():
    """Load menu and business information from JSON files"""
    global MENU_DATA, BUSINESS_INFO

    try:
        with open(MENU_PATH, 'r') as f:
            MENU_DATA = json.load(f)
        print(f"[STARTUP] Loaded menu data from {MENU_PATH}")
    except Exception as e:
        print(f"[ERROR] Failed to load menu: {e}")
        MENU_DATA = {}

    try:
        with open(BUSINESS_INFO_PATH, 'r') as f:
            BUSINESS_INFO = json.load(f)
        print(f"[STARTUP] Loaded business info from {BUSINESS_INFO_PATH}")
    except Exception as e:
        print(f"[ERROR] Failed to load business info: {e}")
        BUSINESS_INFO = {}


# Load data when module is imported
load_data()

SYSTEM_PROMPT = """You are the AI assistant for Bella's Italian Restaurant, a family-owned Italian restaurant.

LOCATION: 123 Main Street, Downtown, CA 90210
PHONE: (555) 123-4567

YOUR CAPABILITIES:
- Check table availability and make reservations
- Answer menu questions using get_menu_info tool
- Provide business information using get_business_info tool
- Help with general inquiries

WORKFLOW:
- For menu questions: Use get_menu_info tool
- For hours/location/parking/policies: Use get_business_info tool
- For reservations: Use check_availability then create_reservation
- Be conversational and warm

TONE: Warm, friendly, professional Italian restaurant host
"""

# Tool definitions
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check table availability",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "YYYY-MM-DD"},
                    "time": {"type": "string", "description": "HH:MM"},
                    "party_size": {"type": "integer"}
                },
                "required": ["date", "time", "party_size"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_reservation",
            "description": "Create a reservation",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "phone": {"type": "string"},
                    "date": {"type": "string"},
                    "time": {"type": "string"},
                    "party_size": {"type": "integer"},
                    "special_requests": {"type": "string"}
                },
                "required": ["name", "phone", "date", "time", "party_size"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_menu_info",
            "description": "Get information about menu items. Can filter by category or search all items.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Menu category: appetizers, pasta, pizza, entrees, desserts, or drinks. Leave empty for all categories.",
                        "enum": ["appetizers", "pasta", "pizza", "entrees", "desserts", "drinks", ""]
                    },
                    "dietary_filter": {
                        "type": "string",
                        "description": "Filter by dietary preference: vegetarian, vegan, or gluten_free",
                        "enum": ["vegetarian", "vegan", "gluten_free", ""]
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_business_info",
            "description": "Get business information like hours, location, parking, policies, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "info_type": {
                        "type": "string",
                        "description": "Type of information requested",
                        "enum": ["hours", "location", "parking", "dress_code", "accessibility", "services", "payment_methods", "private_dining", "gift_cards", "contact"]
                    }
                },
                "required": ["info_type"]
            }
        }
    }
]


@cl.step(name="Check Availability", type="tool")
async def check_availability(date: str, time: str, party_size: int) -> dict:
    """Check table availability"""
    try:
        booking_date = datetime.strptime(date, "%Y-%m-%d")
        booking_time = datetime.strptime(time, "%H:%M")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        if booking_date < today:
            return {"available": False, "message": "Cannot book past dates."}
        if booking_date.weekday() == 0:
            return {"available": False, "message": "Closed Mondays."}
        if party_size >= 8:
            return {"available": False, "message": f"For {party_size} guests, call (555) 123-4567 for private dining."}

        formatted_date = booking_date.strftime("%A, %B %d, %Y")
        formatted_time = booking_time.strftime("%I:%M %p")
        return {"available": True, "message": f"Available: {formatted_date} at {formatted_time} for {party_size}"}
    except:
        return {"available": False, "message": "Invalid date/time."}


@cl.step(name="Create Reservation", type="tool")
async def create_reservation(name: str, phone: str, date: str, time: str, party_size: int, special_requests: str = "") -> dict:
    """Create reservation"""
    confirmation = f"BELLA-{random.randint(100000, 999999)}"
    booking_date = datetime.strptime(date, "%Y-%m-%d").strftime("%A, %B %d, %Y")
    booking_time = datetime.strptime(time, "%H:%M").strftime("%I:%M %p")

    return {
        "success": True,
        "confirmation_number": confirmation,
        "name": name,
        "date": booking_date,
        "time": booking_time,
        "party_size": party_size,
        "message": f"Confirmed! #{confirmation}"
    }


@cl.step(name="Get Menu Info", type="tool")
async def get_menu_info(category: str = "", dietary_filter: str = "") -> dict:
    """
    Get menu information, optionally filtered by category and dietary preferences.
    """
    if not MENU_DATA:
        return {"error": "Menu data not available. Please contact staff at (555) 123-4567"}

    results = []

    # Determine which categories to search
    if category and category in MENU_DATA:
        categories_to_search = {category: MENU_DATA[category]}
    elif category == "drinks" and "drinks" in MENU_DATA:
        categories_to_search = {"drinks": MENU_DATA["drinks"]}
    else:
        # Search all non-drink categories
        categories_to_search = {k: v for k, v in MENU_DATA.items() if k != "drinks"}

    # Collect items
    for cat_name, items in categories_to_search.items():
        if cat_name == "drinks":
            # Handle drinks structure differently
            for drink_type, drink_items in items.items():
                for item in drink_items:
                    results.append({
                        "category": f"drinks/{drink_type}",
                        "name": item.get("name"),
                        "description": item.get("description", ""),
                        "price": item.get("price") or item.get("glass_price", "")
                    })
        else:
            for item in items:
                # Apply dietary filter if specified
                if dietary_filter:
                    if not item.get(dietary_filter, False):
                        continue

                results.append({
                    "category": cat_name,
                    "name": item.get("name"),
                    "description": item.get("description"),
                    "price": item.get("price"),
                    "vegetarian": item.get("vegetarian", False),
                    "vegan": item.get("vegan", False),
                    "gluten_free": item.get("gluten_free", False),
                    "popular": item.get("popular", False)
                })

    if not results:
        return {
            "found": False,
            "message": f"No items found for category='{category}' with dietary filter='{dietary_filter}'"
        }

    # Limit results to avoid overwhelming the context
    max_items = 10
    if len(results) > max_items:
        results = results[:max_items]
        truncated = True
    else:
        truncated = False

    return {
        "found": True,
        "count": len(results),
        "items": results,
        "truncated": truncated,
        "message": f"Found {len(results)} items" + (" (showing first 10)" if truncated else "")
    }


@cl.step(name="Get Business Info", type="tool")
async def get_business_info(info_type: str) -> dict:
    """Get specific business information"""
    if not BUSINESS_INFO:
        return {"error": "Business information not available."}

    info_map = {
        "hours": BUSINESS_INFO.get("hours"),
        "location": BUSINESS_INFO.get("basic", {}).get("address"),
        "parking": BUSINESS_INFO.get("parking"),
        "dress_code": {"dress_code": BUSINESS_INFO.get("dress_code")},
        "accessibility": {"accessibility": BUSINESS_INFO.get("accessibility")},
        "services": {"services": BUSINESS_INFO.get("services")},
        "payment_methods": {"payment_methods": BUSINESS_INFO.get("payment_methods")},
        "private_dining": BUSINESS_INFO.get("private_dining"),
        "gift_cards": BUSINESS_INFO.get("gift_cards"),
        "contact": BUSINESS_INFO.get("basic")
    }

    data = info_map.get(info_type)
    if data:
        return {"found": True, "info_type": info_type, "data": data}
    else:
        return {"found": False, "message": f"Information type '{info_type}' not found."}


@cl.on_chat_start
async def start():
    """Initialize conversation"""
    cl.user_session.set("message_history", [])

    welcome = "Buongiorno! Welcome to Bella's Italian Restaurant. I can help you with our menu, reservations, hours, and more. What would you like to know?"
    await cl.Message(content=welcome).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle messages with all available tools"""
    if len(message.content.strip()) == 0 or len(message.content) > 500:
        await cl.Message(content="Please send a valid message (1-500 characters).").send()
        return

    message_history = cl.user_session.get("message_history", [])
    message_history.append({"role": "user", "content": message.content})
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + message_history

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
    )

    assistant_message = response.choices[0].message

    if assistant_message.tool_calls:
        message_history.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [{
                "id": tc.id,
                "type": tc.type,
                "function": {"name": tc.function.name, "arguments": tc.function.arguments}
            } for tc in assistant_message.tool_calls]
        })

        for tool_call in assistant_message.tool_calls:
            func_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            if func_name == "check_availability":
                result = await check_availability(**args)
            elif func_name == "create_reservation":
                result = await create_reservation(**args)
            elif func_name == "get_menu_info":
                result = await get_menu_info(**args)
            elif func_name == "get_business_info":
                result = await get_business_info(**args)
            else:
                result = {"error": "Unknown function"}

            message_history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

        final_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + message_history
        )

        final_message = final_response.choices[0].message.content
        await cl.Message(content=final_message).send()
        message_history.append({"role": "assistant", "content": final_message})
    else:
        await cl.Message(content=assistant_message.content).send()
        message_history.append({"role": "assistant", "content": assistant_message.content})

    cl.user_session.set("message_history", message_history)
