# Workshop Instructor Guide
## Building Customer Support Agents with Chainlit

**Duration:** 1.5 hours
**Format:** Progressive code examples with live coding
**Target Audience:** Python developers interested in AI automation for local businesses

---

## Workshop Overview

This workshop teaches developers how to build production-ready AI customer support agents using Chainlit. By the end, participants will have a complete, deployable chatbot for a fictional Italian restaurant that demonstrates real-world capabilities they can sell to clients.

### Learning Objectives

By the end of this workshop, participants will:
1. Understand Chainlit basics and setup
2. Implement input/output guardrails for safety
3. Add business actions with OpenAI function calling
4. Integrate RAG (Retrieval Augmented Generation)
5. Have a demo-ready agent to show potential clients

---

## Pre-Workshop Setup (15 minutes before start)

###Instructor Checklist:
- [ ] Test all scripts run without errors
- [ ] Verify OpenAI API key is working
- [ ] Run `python scripts/utils/validate_setup.py`
- [ ] Have Chainlit running on projector/screen share
- [ ] Prepare backup API key in case participants need one

### Participant Pre-requisites:
- Python 3.9+ installed
- OpenAI API key (or provide workshop keys)
- Basic Python knowledge
- Code editor (VS Code recommended)

Send participants ahead of time:
```bash
# Setup instructions
git clone [repo]
cd chainlit-workshop
pip install -e .
cp .env.example .env
# Add OPENAI_API_KEY to .env
python scripts/utils/setup_vectordb.py
python scripts/utils/validate_setup.py
```

---

## Workshop Timeline

### Introduction (5 minutes)

**Goals:**
- Set expectations
- Show the end result
- Explain the business opportunity

**Script:**
> "Today we're building something you can deploy for clients by tonight. We'll create a customer support chatbot for a restaurant, but this same framework works for salons, law firms, medical offices - any local business with FAQs and appointments."

**Demo:**
- Run `06_final_polished.py` briefly
- Show reservation booking, menu questions, escalation
- Mention: "This is where we're headed. Let's build it step by step."

---

### Section 1: The Bare Minimum (10 minutes)

**Script:** `01_bare_minimum_chatbot.py`

**Key Points:**
- "Let's start with the absolute minimum - under 20 lines"
- Show how simple Chainlit makes it
- Contrast with building web UI from scratch

**Live Coding:**
```python
# Walk through each line
import chainlit as cl
from openai import OpenAI

@cl.on_message
async def main(message: cl.Message):
    # Explain: This decorator runs on every user message
    response = client.chat.completions.create(...)
    await cl.Message(content=...).send()
```

**Run It:**
```bash
chainlit run scripts/01_bare_minimum_chatbot.py
```

**Test Queries:**
- "Hello"
- "What can you do?"

**Teaching Moments:**
- "Notice: No HTML, no CSS, no React - just Python"
- "The UI is auto-generated and mobile-friendly"
- "But this isn't useful yet - it has no personality or context"

---

### Section 2: Adding Personality (15 minutes)

**Script:** `02_with_system_prompt.py`

**Key Points:**
- System prompts define personality and knowledge
- Conversation memory maintains context
- Streaming improves UX

**Walk Through:**
1. **System Prompt Design**
   - Business info (hours, location, phone)
   - Role definition
   - Tone guidance

2. **Conversation Memory**
   - Store messages in `cl.user_session`
   - Build message history

3. **Streaming**
   - Why: Better UX, feels responsive
   - How: OpenAI stream=True + `msg.stream_token()`

**Live Demo:**
- "What are your hours?" → Should mention Tuesday-Sunday, closed Monday
- "Where are you located?" → Should say Downtown, Main Street
- Test memory: "What did I just ask?" → Should remember previous question

**Discussion:**
- Q: "Can we change this for a different business?"
- A: "Yes! Just edit the SYSTEM_PROMPT. That's the power of this approach."

---

### Section 3: Safety & Guardrails (20 minutes)

**Scripts:** `03a_input_guardrails.py` and `03b_output_guardrails.py`

**Key Teaching Point:**
> "Without guardrails, your bot can embarrass your client or worse. These are non-negotiable for production."

#### Part A: Input Guardrails (10 min)

**Demonstrate Failures First:**
- "What's the weather?" → Without guardrails, bot tries to answer
- Send 600 character message → Bot wastes tokens processing it

**Then Show Solution:**
```python
def validate_input(message: str) -> Tuple[bool, str]:
    # Length check
    # Off-topic detection
    # Inappropriate content
    # Spam detection
```

**Test Cases:**
- "weather" → Rejected
- "Tell me about pasta" → Accepted

#### Part B: Output Guardrails (10 min)

**Demonstrate Why We Need This:**
- "I got food poisoning!" → Should escalate, not just sympathize

**Show Escalation Logic:**
```python
ESCALATION_TRIGGERS = [
    "food poisoning", "complaint", "refund", "manager"
]
```

**Test Cases:**
- "I'm sick from your food!" → Immediate escalation with phone number
- "I want a refund" → Escalation to manager
- "What pasta do you have?" → Normal response

**Business Value:**
- "This protects your client's reputation"
- "It ensures serious issues get to humans immediately"
- "You can charge more for this level of safety"

---

### Section 4: Taking Actions with Tools (30 minutes)

**Scripts:** `04a`, `04b`, `04c`

**Key Concept:**
> "Now we're going from a chatbot to an actual business assistant that can DO things."

#### 4A: Availability Checking (10 min)

**Introduce Function Calling:**
```python
TOOLS = [{
    "type": "function",
    "function": {
        "name": "check_availability",
        "parameters": {...}
    }
}]
```

**Live Code:**
- Show how OpenAI decides when to call the function
- Walk through the mock availability logic
- Explain `@cl.step` decorator for UI visibility

**Demo:**
- "Do you have a table for 4 on Friday at 7pm?"
- Watch: Terminal shows tool call, UI shows step

**Discussion:**
"In production, this would call a real booking API (OpenTable, Toast, etc.). For now, we mock it."

#### 4B: Creating Reservations (10 min)

**Multi-Tool Orchestration:**
- First check availability
- Then collect name, phone
- Create reservation
- Return confirmation

**Key Teaching:**
- "Notice: The LLM orchestrates the conversation"
- "It knows to ask for missing info conversationally"
- "No hard-coded conversation flows needed"

**Demo:**
- "Make a reservation for 4 people Friday at 7pm"
- Let it ask for name
- Provide name: "John Smith"
- Let it ask for phone
- Provide phone: "555-0123"
- See confirmation number

#### 4C: Menu & Business Info (10 min)

**Loading Data:**
```python
# Load JSON at startup
with open('menu.json') as f:
    MENU_DATA = json.load(f)
```

**Show Tools:**
- `get_menu_info` - Query menu with filters
- `get_business_info` - Hours, parking, etc.

**Demo:**
- "What pasta dishes do you have?" → Lists from menu.json
- "Do you have vegetarian options?" → Filters menu
- "Is there parking?" → Queries business_info.json

---

### Section 5: RAG - Knowledge Base (15 minutes)

**Script:** `05_rag_basic.py`

**Setup:**
```bash
# If not already done
python scripts/utils/setup_vectordb.py
```

**Concept Introduction:**
> "Tools work for actions, but what about detailed questions? You can't put your entire wine list in a tool. That's where RAG comes in."

**Explain the Flow:**
1. User asks question
2. Convert question to embedding
3. Search vector DB for relevant chunks
4. Pass chunks to LLM as context
5. LLM answers using the context

**Live Demo:**
- "Do you cater weddings?" → Should cite catering.md
- "What wine pairs with carbonara?" → Should cite wine_list.md
- Show source citations in response

**Key Points:**
- "The bot can now answer questions from 100+ pages of docs"
- "It cites sources - builds trust"
- "Easy to update: just edit markdown files and re-run setup"

**Business Value:**
- "Client gives you their PDFs/docs, you embed them, done"
- "No need to manually program every FAQ"

---

### Section 6: Production Polish (10 minutes)

**Script:** `06_final_polished.py`

**Show Complete Features:**
1. **Branded Welcome**
   - Custom greeting
   - Action buttons (Make Reservation, View Menu, etc.)

2. **Session Tracking**
   - Stores customer name, phone
   - Tracks conversation metrics

3. **Lead Capture**
   - After 5 messages, offers VIP signup
   - Saves to leads.json

4. **Configuration**
   - Easy to customize for different businesses
   - All constants at top of file

**Demo Full Workflow:**
1. Start chat → See welcome + buttons
2. Click "Make a Reservation"
3. Complete booking
4. Ask menu question
5. Continue until VIP offer appears

**Wrap Up:**
- "This is production-ready"
- "You could deploy this tonight for a real client"

---

## Customization Exercise (5 minutes)

**Challenge participants:**

> "Pick a local business type and customize the system prompt. Then we'll see a few examples."

**Examples:**
- Dental office
- Hair salon
- Law firm
- Real estate agency

**Show:** How changing just the system prompt and data files makes it work for any business.

---

## Business Opportunity Discussion (5 minutes)

**Pricing Guide:**
- Setup: $2,000 - $5,000
- Monthly: $200 - $500 (hosting + maintenance)
- Per integration: $500 - $1,500 (booking system, POS, CRM)

**ROI for Client:**
- 24/7 availability
- Handles 70%+ of routine inquiries
- Frees staff for high-value interactions
- Better customer experience

**Target Clients:**
- Restaurants
- Salons & Spas
- Medical/Dental offices
- Law firms
- Real estate agencies
- Any local business with appointments + FAQs

---

## Q&A (10 minutes)

**Common Questions:**

**Q: What about voice/phone integration?**
A: You can integrate with Twilio for phone, but start with web chat - easier sell, easier implementation.

**Q: How do you handle multiple languages?**
A: OpenAI models are multilingual. Just add examples in target language to system prompt.

**Q: What about data privacy?**
A: Use OpenAI's Enterprise plan (doesn't train on data) or self-host open models. Discuss in CLIENT_PITCH_TEMPLATE.

**Q: How do you prevent the bot from making up information?**
A: The guardrails we built! Plus clear system prompt instructions. RAG helps too - only uses retrieved docs.

---

## Post-Workshop Resources

**Share with participants:**
1. This repository
2. `docs/CLIENT_PITCH_TEMPLATE.md` - Sales template
3. `docs/PRODUCTION_CHECKLIST.md` - Deployment guide
4. Chainlit documentation: https://docs.chainlit.io

**Follow-up:**
- Office hours (optional)
- Slack/Discord channel for questions
- Share success stories

---

## Troubleshooting Guide

| Issue | Solution |
|-------|----------|
| "Module not found" | Run `pip install -e .` |
| "ChromaDB error" | Run `python scripts/utils/setup_vectordb.py` |
| "OpenAI API error" | Check .env file, verify API key, check billing |
| "Port already in use" | Kill other Chainlit processes, or use `chainlit run --port 8001` |
| Slow responses | Check internet connection, consider using gpt-3.5-turbo instead of gpt-4 |

---

## Workshop Success Metrics

- [ ] All participants able to run at least scripts 01-04
- [ ] 80%+ complete RAG setup (script 05)
- [ ] 50%+ complete customization exercise
- [ ] Participants leave with working demo
- [ ] Participants understand business model

---

## Extension Topics (If Time Permits)

1. **Authentication** - Adding user login
2. **Analytics** - Tracking conversations, popular questions
3. **A/B Testing** - Testing different system prompts
4. **Multi-language** - Serving international customers
5. **Integrations** - Real booking systems, payment processing

---

## Instructor Notes

### Energy Management
- Demo enthusiastically - your energy sets the tone
- Celebrate when things work
- Stay calm when they don't (bugs happen!)
- Keep it conversational, not lecture-y

### Time Management
- Stick to timeline - use timer
- If running behind, skip optional discussions
- If ahead, do customization exercise in more depth

### Handling Different Skill Levels
- Beginners: Reassure them, focus on concepts over syntax
- Advanced: Let them experiment, answer deeper questions in Q&A
- Mixed group: "Let's keep moving, but I'll answer specific questions after/in Slack"

---

**Remember:** The goal isn't perfect understanding of every line - it's confidence that they can build and deploy this for clients!
