# Chainlit Workshop Progression Guide
## Feature-by-Feature Breakdown

This guide explains what new Chainlit concepts and features are introduced in each script, helping you understand the progressive learning path.

---

## Script 01: Bare Minimum Chatbot
**File:** `scripts/01_bare_minimum_chatbot.py`

### New Chainlit Concepts Introduced

#### 1. `@cl.on_message` Decorator
```python
@cl.on_message
async def main(message: cl.Message):
    # Handle incoming user messages
```

**What it does:** This decorator defines what happens whenever a user sends a message in the chat. It's the core message handler for your chatbot.

**Parameters:**
- `message: cl.Message` - Contains the user's message content accessible via `message.content`

**Key Points:**
- Must be an `async` function
- Gets called automatically for every user message
- This is where you process input and generate responses

#### 2. `cl.Message().send()` Pattern
```python
await cl.Message(content=response_text).send()
```

**What it does:** Creates and sends a message to the user interface.

**Usage:**
- `cl.Message(content="text")` - Creates a message object
- `.send()` - Sends it to the UI (must be awaited)

#### 3. Basic OpenAI Integration
In this version, we make a simple OpenAI API call and send the response directly to the user. No memory, no streaming, just the absolute minimum to get a working chatbot.

**What's NOT here yet:**
- No conversation history/memory
- No system prompt (personality)
- No streaming responses
- No welcome message
- No session management

---

## Script 02: With System Prompt
**File:** `scripts/02_with_system_prompt.py`

### New Chainlit Concepts Introduced

#### 1. `@cl.on_chat_start` Decorator
```python
@cl.on_chat_start
async def start():
    """Initialize conversation when user opens chat"""
    cl.user_session.set("message_history", [])
    await cl.Message(content=welcome_message).send()
```

**What it does:** This function runs once when a user first opens/starts the chat session. Perfect for initialization and welcome messages.

**Common uses:**
- Send welcome messages
- Initialize session variables
- Load data or set up resources
- Set user preferences

#### 2. `cl.user_session` - Session State Management
```python
# Store data
cl.user_session.set("message_history", [])

# Retrieve data
message_history = cl.user_session.get("message_history", [])
```

**What it does:** Provides persistent storage for user-specific data throughout their chat session.

**Key Features:**
- Data persists across multiple messages
- Isolated per user (each user has their own session)
- Use `.set(key, value)` to store
- Use `.get(key, default)` to retrieve

**In this script:** We use it to maintain conversation history so the bot remembers the conversation context.

#### 3. Message History Pattern
```python
message_history = cl.user_session.get("message_history", [])
message_history.append({"role": "user", "content": message.content})

messages = [{"role": "system", "content": SYSTEM_PROMPT}] + message_history

# After getting response
message_history.append({"role": "assistant", "content": full_response})
cl.user_session.set("message_history", message_history)
```

**What it does:** Maintains conversation context by storing all messages in OpenAI's expected format.

**Structure:**
- System message (first): Defines bot personality/behavior
- User messages: `{"role": "user", "content": "text"}`
- Assistant messages: `{"role": "assistant", "content": "text"}`

#### 4. Streaming Responses
```python
stream = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    stream=True  # Enable streaming
)

msg = cl.Message(content="")
await msg.send()

for chunk in stream:
    if chunk.choices[0].delta.content:
        content = chunk.choices[0].delta.content
        full_response += content
        await msg.stream_token(content)  # Stream each token

await msg.update()  # Finalize the message
```

**What it does:** Shows the AI's response as it's being generated, token by token (like ChatGPT's typing effect).

**Pattern:**
1. Create empty message and send it
2. Stream tokens one by one with `msg.stream_token()`
3. Call `msg.update()` when done

**Benefits:**
- Better UX - users see immediate feedback
- Feels more interactive
- Users can start reading before completion

#### 5. System Prompt
Not a Chainlit feature, but crucial for bot personality:

```python
SYSTEM_PROMPT = """You are the AI assistant for Bella's Italian Restaurant..."""
```

The system prompt defines:
- Bot personality and tone
- Business information
- Behavioral rules
- Response guidelines

---

## Script 03a: Input Guardrails
**File:** `scripts/03a_input_guardrails.py`

### New Concepts Introduced

#### 1. Early Return Pattern in `@cl.on_message`
```python
@cl.on_message
async def main(message: cl.Message):
    is_valid, error_message = validate_input(message.content)

    if not is_valid:
        await cl.Message(content=error_message).send()
        return  # Exit early, don't process further

    # Continue with normal processing...
```

**What it does:** Allows you to validate input and stop processing before making expensive API calls.

**Benefits:**
- Save API costs by rejecting bad input early
- Provide immediate feedback on invalid input
- Protect your system from abuse

#### 2. Input Validation Pattern
This script introduces validation logic (not Chainlit-specific) but demonstrates how to integrate it into the message handler.

**Validations shown:**
- Length checks (too short, too long)
- Off-topic detection
- Inappropriate content filtering
- Spam detection using session data

**Key Pattern:**
```python
# Store last message to detect spam
cl.user_session.set("last_user_message", message.content)

# Later, retrieve to compare
recent_message = cl.user_session.get("last_user_message", "")
if recent_message == message:
    return False, "Duplicate message detected"
```

---

## Script 03b: Output Guardrails
**File:** `scripts/03b_output_guardrails.py`

### New Concepts Introduced

#### 1. Escalation Pattern
```python
needs_escalation, escalation_type = check_for_escalation(message.content)

if needs_escalation:
    escalation_response = await handle_escalation(escalation_type, message.content)
    await cl.Message(content=escalation_response).send()
    return  # Don't send to LLM
```

**What it does:** Detects sensitive situations that require human intervention and handles them immediately without LLM involvement.

**Examples:**
- Health emergencies
- Legal issues
- Complaints
- Refund requests

#### 2. Enhanced System Prompt with Rules
Demonstrates how to add strict rules to system prompts:

```python
CRITICAL RULES - YOU MUST FOLLOW THESE:
1. If you don't know something, say "I don't have that information"
2. NEVER make up menu items, prices, or policies
3. NEVER confirm reservations - always say...
```

**Purpose:** Prevent hallucinations and ensure accurate business information.

---

## Script 04a: Tools - Availability Checking
**File:** `scripts/04a_tools_availability.py`

### New Chainlit Concepts Introduced

#### 1. `@cl.step` Decorator for Tool Calls
```python
@cl.step(name="Check Availability", type="tool")
async def check_availability(date: str, time: str, party_size: int) -> dict:
    """Check table availability"""
    # Implementation
    return {"available": True, "message": "..."}
```

**What it does:** Creates a visible step in the UI showing tool execution with a collapsible section.

**Parameters:**
- `name`: Display name in UI (e.g., "Check Availability")
- `type`: Step type - use `"tool"` for function calls

**Benefits:**
- Users see what the bot is doing
- Transparent AI behavior
- Professional appearance
- Debug-friendly

**UI Display:**
When the function is called, users see:
```
🔧 Check Availability
  [Collapsible section with execution details]
```

#### 2. OpenAI Function Calling Integration
```python
TOOLS = [{
    "type": "function",
    "function": {
        "name": "check_availability",
        "description": "Check if a table is available...",
        "parameters": {...}
    }
}]

response = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    tools=TOOLS,
    tool_choice="auto"
)
```

**What it does:** Enables the LLM to call Python functions to take actions.

**Flow:**
1. LLM decides it needs to call a tool
2. Returns tool call information
3. You execute the Python function
4. Send results back to LLM
5. LLM generates final response using tool results

#### 3. Tool Call Handling Pattern
```python
assistant_message = response.choices[0].message

if assistant_message.tool_calls:
    # Store assistant message with tool calls in history
    message_history.append({
        "role": "assistant",
        "content": assistant_message.content,
        "tool_calls": [...]
    })

    # Execute tools
    for tool_call in assistant_message.tool_calls:
        args = json.loads(tool_call.function.arguments)
        result = await check_availability(**args)

        # Add tool result to history
        message_history.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result)
        })

    # Get final response with tool results
    final_response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", ...}] + message_history
    )
```

**Key Points:**
- Tool calls must be added to message history
- Tool results must include `tool_call_id`
- Second API call needed to get final natural language response

---

## Script 04b: Tools - Reservation Creation
**File:** `scripts/04b_tools_reservation.py`

### New Concepts Introduced

#### 1. Multiple Tools Pattern
```python
TOOLS = [
    {
        "type": "function",
        "function": {"name": "check_availability", ...}
    },
    {
        "type": "function",
        "function": {"name": "create_reservation", ...}
    }
]
```

**What it does:** Provides multiple tools for the LLM to orchestrate.

**Key Pattern:**
- LLM decides which tool(s) to call
- Can call multiple tools in sequence
- Each tool returns data for next step

#### 2. Multi-Turn Conversation for Data Collection
Demonstrates how LLM naturally collects missing information:
- Asks for date if not provided
- Asks for phone number after availability confirmed
- Conversational flow without hardcoded logic

#### 3. Tool Call Router Pattern
```python
for tool_call in assistant_message.tool_calls:
    if tool_call.function.name == "check_availability":
        result = await check_availability(**args)
    elif tool_call.function.name == "create_reservation":
        result = await create_reservation(**args)
```

Routes to correct Python function based on tool name.

---

## Script 04c: Tools - Menu and Business Info
**File:** `scripts/04c_tools_menu_business.py`

### New Concepts Introduced

#### 1. Data Loading at Startup
```python
BASE_DIR = Path(__file__).parent.parent
MENU_PATH = BASE_DIR / "data" / "restaurant" / "menu.json"

with open(MENU_PATH, 'r') as f:
    MENU_DATA = json.load(f)
```

**Pattern:** Load business data once at startup, then access it in tools.

**Benefits:**
- Don't reload data on every call
- Faster tool execution
- Can cache external API calls

#### 2. Information Retrieval Tools
Tools that query existing data rather than performing actions:

```python
@cl.step(name="Get Menu", type="tool")
async def get_menu_info(category: str = None, search: str = None) -> dict:
    """Query menu data and return relevant items"""
```

**Use cases:**
- Menu queries
- Business hours
- Location info
- Policies and procedures

---

## Script 05: RAG (Retrieval Augmented Generation)
**File:** `scripts/05_rag_basic.py`

### New Concepts Introduced

#### 1. RAG Tool Integration
```python
@cl.step(name="Search Knowledge Base", type="tool")
async def search_knowledge_base(query: str) -> dict:
    """Search vector database for relevant information"""
    # Semantic search through documents
    results = collection.query(
        query_texts=[query],
        n_results=3
    )
    return {"documents": results, "sources": [...]}
```

**What it does:** Enables semantic search over your knowledge base (FAQs, policies, wine lists, etc.).

**Pattern:**
- Tool that searches documents
- Returns relevant excerpts
- LLM synthesizes into natural answer
- Provides source citations

#### 2. ChromaDB Integration (Not Chainlit-specific)
Shows how to integrate vector databases with Chainlit tools.

---

## Script 06: Final Polished
**File:** `scripts/06_final_polished.py`

### New Chainlit Concepts Introduced

#### 1. `@cl.action_callback` - Interactive Buttons
```python
@cl.action_callback("reservation")
async def on_reservation_click(action: cl.Action):
    """Handle reservation button click"""
    await cl.Message(content="I'd be happy to help you make a reservation!").send()
```

**What it does:** Creates clickable buttons that users can interact with.

**Creating actions:**
```python
actions = [
    cl.Action(name="reservation", label="Make a Reservation", value="reservation"),
    cl.Action(name="menu", label="View Menu", value="menu"),
    cl.Action(name="hours", label="Hours & Location", value="hours")
]

await cl.Message(content="How can I help you?", actions=actions).send()
```

**Key Points:**
- `name`: Internal identifier for callback
- `label`: Display text on button
- `value`: Data passed to callback
- Callbacks handle the click event

**Benefits:**
- Conversation starters
- Quick actions
- Better UX than typing
- Guided user experience

#### 2. Chainlit Configuration Customization
```python
# In @cl.on_chat_start
await cl.Avatar(
    name="Bella's Assistant",
    url="./assets/bella_logo.png"
).send()
```

**What it does:** Customizes the bot's visual appearance.

**Other customizations via `.chainlit/config.toml`:**
- Theme (light/dark)
- Colors
- Layout
- Features (enable/disable)
- Branding

#### 3. Session Tracking Pattern
```python
session_id = str(uuid.uuid4())
cl.user_session.set("session_id", session_id)
cl.user_session.set("session_start", datetime.now().isoformat())

# Track interactions
interactions = cl.user_session.get("interaction_count", 0)
cl.user_session.set("interaction_count", interactions + 1)
```

**Use cases:**
- Analytics
- Session logging
- User behavior tracking
- A/B testing

#### 4. Lead Collection Pattern
```python
@cl.action_callback("vip_list")
async def collect_email(action: cl.Action):
    """Collect email for VIP list"""
    # Save to database/file
    save_lead(email, source="chatbot")
```

**Integration with business goals:**
- Email capture
- Contact info collection
- Appointment booking
- Lead generation

---

## Chainlit Concepts Summary

### Core Decorators
| Decorator | When It Runs | Purpose |
|-----------|-------------|---------|
| `@cl.on_chat_start` | Once when chat starts | Initialize session, send welcome |
| `@cl.on_message` | Every user message | Handle incoming messages |
| `@cl.action_callback("name")` | Button click | Handle interactive actions |
| `@cl.step(name="...", type="...")` | Function call | Show tool execution in UI |

### Key Patterns

#### Message Sending
```python
# Simple message
await cl.Message(content="text").send()

# Message with streaming
msg = cl.Message(content="")
await msg.send()
await msg.stream_token("token")
await msg.update()

# Message with actions
await cl.Message(content="text", actions=[...]).send()
```

#### Session Management
```python
# Store
cl.user_session.set("key", value)

# Retrieve
value = cl.user_session.get("key", default)
```

#### Tool Integration
```python
# Define tool
@cl.step(name="Tool Name", type="tool")
async def tool_function(param: str) -> dict:
    return {"result": "..."}

# OpenAI function calling
response = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    tools=TOOLS,
    tool_choice="auto"
)

# Handle tool calls
if response.choices[0].message.tool_calls:
    # Execute tools, add results to history
    # Get final response
```

---

## Learning Path Recommendations

### For Beginners
1. Start with Script 01 - understand the basics
2. Move to Script 02 - learn session management and streaming
3. Study Script 03a/03b - understand production safety

### For Intermediate
1. Scripts 04a-04c - master OpenAI function calling
2. Understand tool orchestration patterns
3. Learn data integration approaches

### For Advanced
1. Script 05 - RAG integration
2. Script 06 - production polish and customization
3. Adapt to your own business use case

---

## Next Steps

After completing the workshop:

1. **Customize the config:**
   - Edit `.chainlit/config.toml` for your brand
   - Add custom CSS/JS if needed

2. **Extend the tools:**
   - Add tools specific to your business
   - Integrate with real booking systems
   - Connect to your database

3. **Enhance the knowledge base:**
   - Add more documents to vector DB
   - Improve semantic search
   - Add more data sources

4. **Production considerations:**
   - Proper logging
   - Error handling
   - Rate limiting
   - Authentication
   - Deployment (Railway, Heroku, Fly.io, etc.)

---

## Common Patterns Reference

### Error Handling in Tools
```python
@cl.step(name="Tool", type="tool")
async def tool_function(param: str) -> dict:
    try:
        # Tool logic
        return {"success": True, "data": "..."}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### Logging Pattern
```python
print(f"[INFO] User action: {action_name}")
print(f"[ERROR] Tool failed: {error}")
print(f"[DEBUG] State: {cl.user_session.get('key')}")
```

### Multi-Step Workflows
```python
# Step 1: Check something
result1 = await tool1()

# Step 2: Use result from step 1
if result1["success"]:
    result2 = await tool2(result1["data"])

# Step 3: Final action
await finalize(result2)
```

---

## Troubleshooting Tips

### Message Not Appearing
- Did you `await` the `.send()` call?
- Check for errors in console
- Verify message content isn't empty

### Session Data Not Persisting
- Ensure you're using `cl.user_session.set()` after updates
- Check you're in the same session (not browser reload)

### Tools Not Being Called
- Verify tool definitions match OpenAI schema
- Check system prompt mentions the tools
- Ensure `tool_choice="auto"` is set

### Streaming Not Working
- Verify `stream=True` in OpenAI call
- Check you're calling `msg.stream_token()` in loop
- Don't forget `msg.update()` at end

---

## Additional Resources

- **Chainlit Documentation:** https://docs.chainlit.io
- **OpenAI Function Calling:** https://platform.openai.com/docs/guides/function-calling
- **ChromaDB Documentation:** https://docs.trychroma.com
- **Workshop GitHub:** [Your repository URL]

---

*This progression guide is designed to help you understand exactly what each script teaches and how the concepts build on each other. Use it as a reference while building your own Chainlit applications!*
