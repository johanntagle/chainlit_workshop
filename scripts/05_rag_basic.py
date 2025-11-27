"""
Script 05: RAG (Retrieval Augmented Generation)
================================================
Adds semantic search over restaurant documents to answer detailed questions.
Combines vector database retrieval with LLM generation.

New Features:
- ChromaDB vector database integration
- Semantic search over FAQ, catering, and wine list documents
- Source citations in responses
- Combined tool + RAG approach (tools for actions, RAG for information)

Prerequisites:
- Run: python scripts/utils/setup_vectordb.py first to create the vector database

To run: uv run chainlit run scripts/05_rag_basic.py
"""

import os
import json
import re
import random
from datetime import datetime
from pathlib import Path
from openai import OpenAI
import chainlit as cl
from typing import List, Dict

# ChromaDB and embeddings
try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("[WARNING] ChromaDB or sentence-transformers not installed. RAG features will be limited.")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

# Paths
BASE_DIR = Path(__file__).parent.parent
MENU_PATH = BASE_DIR / "data" / "restaurant" / "menu.json"
BUSINESS_INFO_PATH = BASE_DIR / "data" / "restaurant" / "business_info.json"
CHROMA_PATH = BASE_DIR / "data" / "embeddings"

# Global variables
MENU_DATA = {}
BUSINESS_INFO = {}
chroma_client = None
collection = None
embedding_model = None


def load_data():
    """Load menu and business info"""
    global MENU_DATA, BUSINESS_INFO

    try:
        with open(MENU_PATH, 'r') as f:
            MENU_DATA = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load menu: {e}")

    try:
        with open(BUSINESS_INFO_PATH, 'r') as f:
            BUSINESS_INFO = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load business info: {e}")


def initialize_vector_db():
    """Initialize ChromaDB client and load collection"""
    global chroma_client, collection, embedding_model

    if not CHROMA_AVAILABLE:
        print("[WARNING] ChromaDB not available. Install with: pip install chromadb sentence-transformers")
        return False

    try:
        # Initialize embedding model
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Initialize ChromaDB
        chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))

        # Try to get existing collection
        try:
            collection = chroma_client.get_collection(name="restaurant_docs")
            print(f"[STARTUP] Loaded existing vector database with {collection.count()} documents")
            return True
        except:
            print("[WARNING] Vector database not found. Run 'python scripts/utils/setup_vectordb.py' first.")
            print("[INFO] RAG features will be disabled, but other features will work.")
            return False

    except Exception as e:
        print(f"[ERROR] Failed to initialize vector database: {e}")
        return False


# Initialize data
load_data()
rag_enabled = initialize_vector_db()


def retrieve_context(query: str, n_results: int = 3) -> List[Dict]:
    """
    Retrieve relevant context from vector database.

    Args:
        query: User's question
        n_results: Number of chunks to retrieve

    Returns:
        List of relevant document chunks with metadata
    """
    if not rag_enabled or not collection:
        return []

    try:
        # Generate query embedding
        query_embedding = embedding_model.encode(query).tolist()

        # Query the collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        # Format results
        contexts = []
        if results and results['documents'] and len(results['documents']) > 0:
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


# Enhanced system prompt with RAG instructions
SYSTEM_PROMPT_BASE = """You are the AI assistant for Bella's Italian Restaurant, a family-owned Italian restaurant.

LOCATION: 123 Main Street, Downtown, CA 90210
PHONE: (555) 123-4567

YOUR CAPABILITIES:
- Answer questions using retrieved context from our knowledge base
- Check table availability and make reservations
- Provide menu and business information
- Help with general inquiries

IMPORTANT RULES FOR USING RETRIEVED CONTEXT:
1. When you receive retrieved context, use it to answer questions accurately
2. Always cite your sources by mentioning the document (e.g., "According to our FAQ..." or "From our Catering menu...")
3. If the retrieved context doesn't contain the answer, use your tools or say you don't have that information
4. Never make up information not in the context or tools

TONE: Warm, friendly, professional Italian restaurant host
"""


# All tools from previous scripts
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check table availability",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string"},
                    "time": {"type": "string"},
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
            "description": "Get menu items",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "enum": ["appetizers", "pasta", "pizza", "entrees", "desserts", "drinks", ""]},
                    "dietary_filter": {"type": "string", "enum": ["vegetarian", "vegan", "gluten_free", ""]}
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
                    "info_type": {"type": "string", "enum": ["hours", "location", "parking", "dress_code", "accessibility", "services"]}
                },
                "required": ["info_type"]
            }
        }
    }
]


@cl.step(name="Retrieve Context", type="retrieval")
async def retrieve_step(query: str) -> str:
    """Retrieve relevant context and format for display"""
    contexts = retrieve_context(query, n_results=3)

    if not contexts:
        return "No relevant context found in knowledge base."

    formatted = "**Retrieved Context:**\n\n"
    for i, ctx in enumerate(contexts, 1):
        formatted += f"{i}. **{ctx['source']}** - {ctx['section']}\n"
        formatted += f"   {ctx['content'][:200]}...\n\n"

    return formatted


# Simplified tool implementations (same as 04c)
@cl.step(name="Check Availability", type="tool")
async def check_availability(date: str, time: str, party_size: int) -> dict:
    """Check availability"""
    try:
        booking_date = datetime.strptime(date, "%Y-%m-%d")
        if booking_date.weekday() == 0:
            return {"available": False, "message": "Closed Mondays."}
        if party_size >= 8:
            return {"available": False, "message": "Call (555) 123-4567 for large parties."}
        formatted = booking_date.strftime("%A, %B %d")
        return {"available": True, "message": f"Available: {formatted} at {time} for {party_size}"}
    except:
        return {"available": False, "message": "Invalid date/time."}


@cl.step(name="Create Reservation", type="tool")
async def create_reservation(name: str, phone: str, date: str, time: str, party_size: int, special_requests: str = "") -> dict:
    """Create reservation"""
    confirmation = f"BELLA-{random.randint(100000, 999999)}"
    return {"success": True, "confirmation_number": confirmation, "message": f"Confirmed! #{confirmation}"}


@cl.step(name="Get Menu", type="tool")
async def get_menu_info(category: str = "", dietary_filter: str = "") -> dict:
    """Get menu info"""
    if not MENU_DATA:
        return {"error": "Menu not available"}
    # Simplified - return category name or count
    if category and category in MENU_DATA:
        items = MENU_DATA[category]
        if isinstance(items, list):
            return {"found": True, "count": len(items), "items": items[:5]}
    return {"found": True, "message": "Menu data available"}


@cl.step(name="Get Business Info", type="tool")
async def get_business_info(info_type: str) -> dict:
    """Get business info"""
    if not BUSINESS_INFO:
        return {"error": "Info not available"}
    data = BUSINESS_INFO.get(info_type, {})
    return {"found": True, "data": data}


@cl.on_chat_start
async def start():
    """Initialize conversation"""
    cl.user_session.set("message_history", [])

    rag_status = "with RAG-powered knowledge base" if rag_enabled else "(RAG disabled - run setup_vectordb.py)"
    welcome = f"Buongiorno! Welcome to Bella's Italian Restaurant {rag_status}. I can help with menu questions, reservations, catering, wine pairings, and more. What would you like to know?"
    await cl.Message(content=welcome).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle messages with RAG + tools"""
    if len(message.content.strip()) == 0:
        return

    message_history = cl.user_session.get("message_history", [])

    # Step 1: Retrieve relevant context if RAG is enabled
    context_str = ""
    if rag_enabled:
        contexts = retrieve_context(message.content, n_results=3)
        if contexts:
            # Show retrieval step in UI
            await retrieve_step(message.content)

            # Format context for LLM
            context_str = "\n\nRETRIEVED CONTEXT:\n"
            for ctx in contexts:
                context_str += f"\nSource: {ctx['source']} - {ctx['section']}\n{ctx['content']}\n"

    # Step 2: Build system prompt with context
    system_prompt = SYSTEM_PROMPT_BASE
    if context_str:
        system_prompt += context_str

    # Step 3: Add user message
    message_history.append({"role": "user", "content": message.content})
    messages = [{"role": "system", "content": system_prompt}] + message_history

    # Step 4: Call OpenAI with tools
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
    )

    assistant_message = response.choices[0].message

    # Step 5: Handle tool calls
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

        # Get final response
        final_response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": system_prompt}] + message_history
        )

        final_message = final_response.choices[0].message.content
        await cl.Message(content=final_message).send()
        message_history.append({"role": "assistant", "content": final_message})
    else:
        # No tool call
        await cl.Message(content=assistant_message.content).send()
        message_history.append({"role": "assistant", "content": assistant_message.content})

    cl.user_session.set("message_history", message_history)
