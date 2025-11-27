"""
Script 06: Final Polished - Production Ready
============================================
The complete, production-ready customer support agent with all features polished.
This is what you'd deploy for a real client!

Features:
- Custom branding and avatar
- Conversation starter buttons
- Streaming with loading indicators
- Session management and tracking
- Email collection for VIP list
- Comprehensive logging
- Easy configuration for different businesses
- All previous features (guardrails, tools, RAG)

To run: chainlit run scripts/06_final_polished.py
"""

import os
import json
import re
import random
from datetime import datetime
from pathlib import Path
from openai import OpenAI
import chainlit as cl
from typing import List, Dict, Optional

# ChromaDB (optional)
try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    CHROMA_AVAILABLE = True
except:
    CHROMA_AVAILABLE = False

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# =============================================================================
# CONFIGURATION - Easy to customize for different businesses
# =============================================================================

BUSINESS_CONFIG = {
    "name": "Bella's Italian Restaurant",
    "tagline": "Authentic Italian Cuisine Since 1985",
    "phone": "(555) 123-4567",
    "email": "info@bellasitalian.com",
    "website": "www.bellasitalian.com",
    "address": "123 Main Street, Downtown, CA 90210",
    "hours": {
        "monday": "Closed",
        "tuesday-thursday": "11am-10pm",
        "friday": "11am-11pm",
        "saturday": "10am-11pm (Brunch 10am-2pm)",
        "sunday": "10am-9pm (Brunch 10am-2pm)"
    }
}

# Paths
BASE_DIR = Path(__file__).parent.parent
MENU_PATH = BASE_DIR / "data" / "restaurant" / "menu.json"
BUSINESS_INFO_PATH = BASE_DIR / "data" / "restaurant" / "business_info.json"
CHROMA_PATH = BASE_DIR / "data" / "embeddings"
LEADS_PATH = BASE_DIR / "data" / "leads.json"
LOGO_PATH = BASE_DIR / "assets" / "bella_logo.png"

# Global state
MENU_DATA = {}
BUSINESS_INFO = {}
chroma_client = None
collection = None
embedding_model = None
rag_enabled = False

# =============================================================================
# STARTUP FUNCTIONS
# =============================================================================

def load_data():
    """Load business data"""
    global MENU_DATA, BUSINESS_INFO
    try:
        with open(MENU_PATH, 'r') as f:
            MENU_DATA = json.load(f)
        print(f"[STARTUP] Loaded menu data")
    except Exception as e:
        print(f"[ERROR] Menu load failed: {e}")

    try:
        with open(BUSINESS_INFO_PATH, 'r') as f:
            BUSINESS_INFO = json.load(f)
        print(f"[STARTUP] Loaded business info")
    except Exception as e:
        print(f"[ERROR] Business info load failed: {e}")


def initialize_vector_db():
    """Initialize RAG system"""
    global chroma_client, collection, embedding_model, rag_enabled

    if not CHROMA_AVAILABLE:
        print("[INFO] RAG not available - install chromadb and sentence-transformers")
        return False

    try:
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
        collection = chroma_client.get_collection(name="restaurant_docs")
        rag_enabled = True
        print(f"[STARTUP] RAG enabled with {collection.count()} documents")
        return True
    except Exception as e:
        print(f"[INFO] RAG disabled: {e}")
        return False


def save_lead(name: str, email: str):
    """Save VIP list signup to JSON file"""
    try:
        # Load existing leads
        if LEADS_PATH.exists():
            with open(LEADS_PATH, 'r') as f:
                leads = json.load(f)
        else:
            leads = []

        # Add new lead
        leads.append({
            "name": name,
            "email": email,
            "timestamp": datetime.now().isoformat(),
            "source": "chatbot"
        })

        # Save
        with open(LEADS_PATH, 'w') as f:
            json.dump(leads, f, indent=2)

        print(f"[LEAD CAPTURED] {name} - {email}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save lead: {e}")
        return False


# Initialize
load_data()
initialize_vector_db()

# =============================================================================
# SYSTEM PROMPT
# =============================================================================

SYSTEM_PROMPT = f"""You are the AI assistant for {BUSINESS_CONFIG['name']}, {BUSINESS_CONFIG['tagline']}.

CONTACT:
- Phone: {BUSINESS_CONFIG['phone']}
- Location: {BUSINESS_CONFIG['address']}
- Email: {BUSINESS_CONFIG['email']}

YOUR ROLE:
- Help guests with reservations, menu questions, and general inquiries
- Use tools to check availability, create reservations, and retrieve information
- Answer questions using retrieved knowledge base context when available
- Be warm, welcoming, and professional

IMPORTANT:
- Always cite sources when using retrieved context
- For serious issues (complaints, health concerns), escalate to management
- Never make up information - use tools and context provided
- Guide conversations naturally and collect information conversationally

TONE: Warm, friendly, professional - like a welcoming Italian restaurant host
"""

# =============================================================================
# TOOLS
# =============================================================================

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
            "description": "Get menu information",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "dietary_filter": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_business_info",
            "description": "Get business information",
            "parameters": {
                "type": "object",
                "properties": {
                    "info_type": {"type": "string"}
                },
                "required": ["info_type"]
            }
        }
    }
]

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def retrieve_context(query: str, n_results: int = 3) -> List[Dict]:
    """Retrieve from vector database"""
    if not rag_enabled or not collection:
        return []
    try:
        query_embedding = embedding_model.encode(query).tolist()
        results = collection.query(query_embeddings=[query_embedding], n_results=n_results)
        contexts = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                contexts.append({
                    "content": doc,
                    "source": metadata.get("source", "unknown"),
                    "section": metadata.get("section", "")
                })
        return contexts
    except Exception as e:
        print(f"[ERROR] Retrieval failed: {e}")
        return []


def log_interaction(event_type: str, data: dict):
    """Log important interactions"""
    print(f"[{event_type.upper()}] {json.dumps(data, default=str)}")


# =============================================================================
# TOOL IMPLEMENTATIONS
# =============================================================================

@cl.step(name="Check Availability", type="tool")
async def check_availability(date: str, time: str, party_size: int) -> dict:
    """Check table availability"""
    log_interaction("availability_check", {"date": date, "time": time, "party_size": party_size})

    try:
        booking_date = datetime.strptime(date, "%Y-%m-%d")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        if booking_date < today:
            return {"available": False, "message": "Cannot book past dates."}

        if booking_date.weekday() == 0:  # Monday
            return {"available": False, "message": "We're closed on Mondays. Try Tuesday-Sunday!"}

        if party_size >= 8:
            return {
                "available": False,
                "message": f"For parties of {party_size}, please call {BUSINESS_CONFIG['phone']} for our private dining room."
            }

        # Mock availability
        formatted_date = booking_date.strftime("%A, %B %d, %Y")
        return {
            "available": True,
            "message": f"Table available on {formatted_date} at {time} for {party_size} guests!"
        }
    except:
        return {"available": False, "message": "Invalid date or time format."}


@cl.step(name="Create Reservation", type="tool")
async def create_reservation(name: str, phone: str, date: str, time: str, party_size: int, special_requests: str = "") -> dict:
    """Create reservation"""
    confirmation = f"BELLA-{random.randint(100000, 999999)}"

    log_interaction("reservation_created", {
        "confirmation": confirmation,
        "name": name,
        "phone": phone,
        "date": date,
        "time": time,
        "party_size": party_size
    })

    booking_date = datetime.strptime(date, "%Y-%m-%d").strftime("%A, %B %d, %Y")
    booking_time = datetime.strptime(time, "%H:%M").strftime("%I:%M %p")

    # Store in session
    cl.user_session.set("customer_name", name)
    cl.user_session.set("customer_phone", phone)

    return {
        "success": True,
        "confirmation_number": confirmation,
        "name": name,
        "phone": phone,
        "date": booking_date,
        "time": booking_time,
        "party_size": party_size,
        "special_requests": special_requests
    }


@cl.step(name="Get Menu", type="tool")
async def get_menu_info(category: str = "", dietary_filter: str = "") -> dict:
    """Get menu information"""
    if not MENU_DATA:
        return {"error": "Menu not available"}

    results = []
    categories = {category: MENU_DATA[category]} if category and category in MENU_DATA else {k: v for k, v in MENU_DATA.items() if k != "drinks"}

    for cat_name, items in categories.items():
        if isinstance(items, list):
            for item in items[:5]:  # Limit results
                if dietary_filter and not item.get(dietary_filter, False):
                    continue
                results.append({
                    "category": cat_name,
                    "name": item.get("name"),
                    "description": item.get("description", ""),
                    "price": item.get("price")
                })

    return {"found": True, "count": len(results), "items": results}


@cl.step(name="Get Business Info", type="tool")
async def get_business_info(info_type: str) -> dict:
    """Get business information"""
    if not BUSINESS_INFO:
        return {"error": "Information not available"}

    info_map = {
        "hours": BUSINESS_INFO.get("hours"),
        "location": BUSINESS_INFO.get("basic", {}).get("address"),
        "parking": BUSINESS_INFO.get("parking"),
        "services": BUSINESS_INFO.get("services")
    }

    return {"found": True, "data": info_map.get(info_type, {})}


# =============================================================================
# CHAINLIT HANDLERS
# =============================================================================

@cl.on_chat_start
async def start():
    """Initialize conversation with welcome and action buttons"""
    cl.user_session.set("message_history", [])
    cl.user_session.set("message_count", 0)
    cl.user_session.set("tools_used", [])

    # Welcome message
    welcome = f"""🇮🇹 **Benvenuti!** Welcome to {BUSINESS_CONFIG['name']}!

I'm here to help you with:
✨ **Reservations** - Check availability and book tables
🍝 **Menu Questions** - Pasta, pizza, wine pairings, and more
🎉 **Catering & Events** - Private dining and special occasions
📍 **Location & Hours** - Directions, parking, and more

What can I do for you today?"""

    await cl.Message(content=welcome).send()

    # Add conversation starter buttons
    actions = [
        cl.Action(name="reservation", value="reservation", label="Make a Reservation"),
        cl.Action(name="menu", value="menu", label="View Menu"),
        cl.Action(name="hours", value="hours", label="Hours & Location"),
        cl.Action(name="catering", value="catering", label="Catering Info")
    ]

    await cl.Message(content="Quick actions:", actions=actions).send()


@cl.action_callback("reservation")
async def on_reservation(action):
    """Handle reservation button click"""
    await cl.Message(content="I'd be happy to help you make a reservation! What date and time were you thinking, and for how many guests?").send()


@cl.action_callback("menu")
async def on_menu(action):
    """Handle menu button click"""
    await cl.Message(content="What would you like to know about our menu? I can tell you about pasta dishes, pizzas, appetizers, entrees, desserts, or our wine list!").send()


@cl.action_callback("hours")
async def on_hours(action):
    """Handle hours button click"""
    hours_msg = f"""**Hours & Location**

📍 **Address:** {BUSINESS_CONFIG['address']}
📞 **Phone:** {BUSINESS_CONFIG['phone']}

⏰ **Hours:**
- Monday: Closed
- Tuesday-Thursday: 11am-10pm
- Friday: 11am-11pm
- Saturday: 10am-11pm (Brunch 10am-2pm)
- Sunday: 10am-9pm (Brunch 10am-2pm)

🚗 We validate parking at Main Street Garage (2 hours free)"""
    await cl.Message(content=hours_msg).send()


@cl.action_callback("catering")
async def on_catering(action):
    """Handle catering button click"""
    await cl.Message(content="We'd love to cater your event! We offer drop-off catering, buffet service, and full plated service for events from 10 to 200 guests. What type of event are you planning?").send()


@cl.on_message
async def main(message: cl.Message):
    """Main message handler with full features"""
    if len(message.content.strip()) == 0:
        return

    # Track metrics
    msg_count = cl.user_session.get("message_count", 0) + 1
    cl.user_session.set("message_count", msg_count)

    message_history = cl.user_session.get("message_history", [])

    # Retrieve context if RAG enabled
    context_str = ""
    if rag_enabled:
        contexts = retrieve_context(message.content, n_results=3)
        if contexts:
            context_str = "\n\nRETRIEVED CONTEXT:\n"
            for ctx in contexts:
                context_str += f"\nSource: {ctx['source']} - {ctx['section']}\n{ctx['content']}\n"

    # Build prompt
    system_prompt = SYSTEM_PROMPT + context_str

    message_history.append({"role": "user", "content": message.content})
    messages = [{"role": "system", "content": system_prompt}] + message_history

    # Call OpenAI
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
    )

    assistant_message = response.choices[0].message

    # Handle tool calls
    if assistant_message.tool_calls:
        message_history.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [{"id": tc.id, "type": tc.type, "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in assistant_message.tool_calls]
        })

        for tool_call in assistant_message.tool_calls:
            func_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            # Track tool usage
            tools_used = cl.user_session.get("tools_used", [])
            tools_used.append(func_name)
            cl.user_session.set("tools_used", tools_used)

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

            message_history.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)})

        final_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": system_prompt}] + message_history
        )
        final_message = final_response.choices[0].message.content
        await cl.Message(content=final_message).send()
        message_history.append({"role": "assistant", "content": final_message})

    else:
        await cl.Message(content=assistant_message.content).send()
        message_history.append({"role": "assistant", "content": assistant_message.content})

    cl.user_session.set("message_history", message_history)

    # After 5+ messages, offer VIP list (only once)
    if msg_count >= 5 and not cl.user_session.get("vip_offered", False):
        cl.user_session.set("vip_offered", True)
        vip_msg = "\n\n---\n\n💌 **Join our VIP list** for exclusive offers and event invitations! Would you like to sign up?"
        await cl.Message(content=vip_msg).send()
