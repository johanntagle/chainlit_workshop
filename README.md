# Building Customer Support Agents with Chainlit
## Workshop Materials - From Zero to Production in 90 Minutes

> Learn to build production-ready AI customer support agents using Chainlit. Build something you can deploy for clients by the end of this workshop.

---

## What You'll Build

A complete customer support agent for "Bella's Italian Restaurant" featuring:

- ✅ Natural conversation with business personality
- ✅ Input/output guardrails for safety and quality
- ✅ Function calling for checking availability and making reservations
- ✅ Menu and business information queries
- ✅ RAG (Retrieval Augmented Generation) for detailed knowledge base questions
- ✅ Professional UI with branding and conversation starters
- ✅ Lead capture and session management
- ✅ Production-ready code you can customize for any local business

**This same framework works for restaurants, salons, law firms, medical offices, and any local business with FAQs and appointments.**

---

## Workshop Overview

### Duration
1.5 hours of progressive learning

### Prerequisites
- Python 3.10+ installed
- Basic Python knowledge (functions, dictionaries, async/await)
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))
- Code editor (VS Code recommended)

### What You'll Learn
1. Chainlit basics and rapid prototyping
2. System prompts and conversation design
3. Safety guardrails for production use
4. OpenAI function calling for business actions
5. RAG with ChromaDB for knowledge retrieval
6. Production polish and deployment

---

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd chainlit-workshop

# Install uv (recommended package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Or use pip
pip install -e .
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_key_here
```

### 3. Initialize Vector Database (for RAG features)

```bash
uv run scripts/utils/setup_vectordb.py
```

### 4. Validate Setup

```bash
uv run scripts/utils/validate_setup.py
```

You should see all green checkmarks! ✅

### 5. Run Your First Script

```bash
chainlit run scripts/01_bare_minimum_chatbot.py
```

Open your browser to `http://localhost:8000` and start chatting!

---

## Repository Structure

```
chainlit-workshop/
├── README.md                          # You are here
├── pyproject.toml                     # Dependencies
├── .env.example                       # Environment template
├── .python-version                    # Python version requirement
│
├── scripts/                           # Progressive workshop scripts
│   ├── 01_bare_minimum_chatbot.py    # Start here: < 20 lines!
│   ├── 02_with_system_prompt.py      # Add personality + streaming
│   ├── 03a_input_guardrails.py       # Input validation
│   ├── 03b_output_guardrails.py      # Output safety + escalation
│   ├── 04a_tools_availability.py     # First function calling
│   ├── 04b_tools_reservation.py      # Multi-step reservations
│   ├── 04c_tools_menu_business.py    # Data queries
│   ├── 05_rag_basic.py               # Knowledge base retrieval
│   ├── 06_final_polished.py          # Production ready!
│   │
│   └── utils/                         # Helper scripts
│       ├── setup_vectordb.py         # Initialize ChromaDB
│       ├── test_queries.py           # Testing scenarios
│       └── validate_setup.py         # Environment checker
│
├── data/                              # Business data
│   ├── restaurant/
│   │   ├── menu.json                 # 50+ menu items
│   │   ├── business_info.json        # Hours, location, policies
│   │   ├── faq.md                    # Comprehensive FAQ
│   │   ├── catering.md               # Catering services
│   │   └── wine_list.md              # Wine pairings
│   │
│   └── embeddings/                    # Vector database (generated)
│
├── docs/                              # Documentation
│   ├── WORKSHOP_GUIDE.md             # Instructor guide
│   ├── CLIENT_PITCH_TEMPLATE.md      # Sales template
│   └── PRODUCTION_CHECKLIST.md       # Deployment guide
│
└── assets/                            # Branding assets
    ├── logo_specification.md          # Logo guidelines
    └── conversation_examples.md       # Example dialogues
```

---

## Workshop Progression

Each script builds on the previous one. Follow them in order!

### Script 01: Bare Minimum (5 minutes)
**Concept:** "This is how easy it is to get started"
- Under 20 lines of code
- Basic OpenAI integration
- Auto-generated Chainlit UI

```bash
uv run chainlit run scripts/01_bare_minimum_chatbot.py
```

**Try:**
- "Hello"
- "Tell me about yourself"

---

### UI Configuration Note: Message Scroll Behavior

By default, Chainlit displays new messages at the top of the chat window. To change this to standard chat behavior (newest messages at bottom), edit `.chainlit/config.toml`:

```toml
[features]
# Set to false for standard chat behavior (new messages at bottom)
user_message_autoscroll = false
```

**Options:**
- `true` (default): New messages appear at top, older messages scroll down
- `false` (recommended): New messages appear at bottom, scroll down to see new content (like Slack, Discord, WhatsApp)

---

### Script 02: System Prompt (10 minutes)
**Concept:** Add business personality and context
- System prompt defines bot behavior
- Conversation memory
- Streaming responses

```bash
uv run chainlit run scripts/02_with_system_prompt.py
```

**Try:**
- "What are your hours?"
- "Where are you located?"
- "What did I just ask?" (tests memory)

---

### Script 03a: Input Guardrails (10 minutes)
**Concept:** Protect your business from inappropriate input
- Length validation
- Off-topic detection
- Spam protection

```bash
uv run chainlit run scripts/03a_input_guardrails.py
```

**Try:**
- "What's the weather?" (should reject - off-topic)
- Send a very long message (should reject - too long)
- "What pasta do you have?" (should accept)

---

### Script 03b: Output Guardrails (10 minutes)
**Concept:** Prevent hallucinations and handle escalations
- Never make up information
- Detect serious issues
- Escalate to humans appropriately

```bash
uv run chainlit run scripts/03b_output_guardrails.py
```

**Try:**
- "I got food poisoning!" (should escalate immediately)
- "I want a refund" (should escalate)
- "What time do you open?" (normal response)

---

### Script 04a: Availability Tool (15 minutes)
**Concept:** Take business actions with OpenAI function calling
- First tool: check table availability
- Agent decides when to call functions
- Conversational parameter collection

```bash
uv run chainlit run scripts/04a_tools_availability.py
```

**Try:**
- "Do you have a table for 4 on Friday at 7pm?"
- "Check availability for 2 people Saturday"

---

### Script 04b: Reservation Tool (15 minutes)
**Concept:** Multi-tool orchestration
- Create actual reservations
- Collect information conversationally
- Generate confirmation numbers

```bash
uv run chainlit run scripts/04b_tools_reservation.py
```

**Try:**
- "I'd like to make a reservation for 4 people Friday at 7pm"
- Let it ask for your name and phone

---

### Script 04c: Menu & Business Tools (15 minutes)
**Concept:** Query structured business data
- Load JSON data at startup
- Search and filter menus
- Provide business information

```bash
uv run chainlit run scripts/04c_tools_menu_business.py
```

**Try:**
- "What pasta dishes do you have?"
- "Do you have parking?"
- "Show me vegetarian options"

---

### Script 05: RAG Integration (20 minutes)
**Concept:** Answer detailed questions from knowledge base
- ChromaDB vector database
- Semantic search over documents
- Source citations

```bash
# First, set up the vector database
uv run scripts/utils/setup_vectordb.py

# Then run the script
uv run chainlit run scripts/05_rag_basic.py
```

**Try:**
- "Do you cater weddings?"
- "What wine pairs with carbonara?"
- "Tell me about your private dining"

---

### Script 06: Final Polished (15 minutes)
**Concept:** Production-ready with all features
- Custom branding
- Conversation starter buttons
- Session tracking
- Lead capture
- Professional UX

```bash
uv run chainlit run scripts/06_final_polished.py
```

**Try:**
- Use the quick action buttons
- Make a complete reservation
- Chat until VIP offer appears

---

## Customizing for Your Clients

This framework is designed to be easily customized for different businesses.

### Quick Customization Guide

1. **Change the Business** (5 minutes)
   - Edit system prompt in any script
   - Update business name, hours, location
   - Adjust tone and personality

2. **Update the Data** (10 minutes)
   - Edit `data/restaurant/business_info.json` with client's info
   - Update `data/restaurant/menu.json` with their services/products
   - Modify FAQ, catering docs, etc.

3. **Retrain Knowledge Base** (2 minutes)
   ```bash
   python scripts/utils/setup_vectordb.py
   ```

4. **Test & Deploy**
   ```bash
   python scripts/utils/validate_setup.py
   chainlit run scripts/06_final_polished.py
   ```

### Use Cases Beyond Restaurants

**Dental Office:**
- Appointment booking instead of reservations
- Services instead of menu
- Insurance info instead of catering

**Hair Salon:**
- Stylist availability checking
- Service catalog with pricing
- Booking appointments

**Law Firm:**
- Case type information
- Initial consultation scheduling
- FAQ about legal processes

**Real Estate:**
- Property availability
- Showing schedules
- Neighborhood information

---

## Business Opportunity

### Pricing Your Services

**Setup Fees:**
- Basic: $2,000 - $3,000
- Professional: $3,500 - $5,000
- Enterprise: $5,000 - $8,000

**Monthly Recurring:**
- Hosting + maintenance: $200 - $500/month
- Updates and optimizations: Included
- Integration fees: $500 - $1,500 per system

### ROI for Clients

**Time Savings:**
- 70%+ of routine inquiries handled automatically
- Staff can focus on high-value interactions
- 24/7 availability captures after-hours leads

**Revenue Impact:**
- Never miss an appointment/booking
- Faster response = higher conversion
- Lead capture builds marketing list

**Typical Payback:** 2-4 months

### Target Industries

1. **Restaurants & Cafes** - Reservations, menu questions, catering
2. **Salons & Spas** - Appointments, service info, availability
3. **Medical/Dental** - Scheduling, insurance, FAQs
4. **Professional Services** - Consultations, case intake, scheduling
5. **Local Retail** - Product info, hours, special orders

See `docs/CLIENT_PITCH_TEMPLATE.md` for a complete sales template.

---

## Going to Production

### Deployment Options

**Easiest (Recommended for Starting Out):**
1. [Railway.app](https://railway.app) - $5-20/month, dead simple
2. [Render](https://render.com) - Free tier available
3. [Heroku](https://heroku.com) - $7-25/month, mature platform

**Most Flexible:**
- AWS / GCP / Azure - Full control, varies by usage
- Self-hosted VPS - DigitalOcean, Linode, etc.

### Pre-Deployment Checklist

See `docs/PRODUCTION_CHECKLIST.md` for comprehensive deployment guide covering:
- Security hardening
- Data privacy compliance (GDPR, CCPA, HIPAA)
- Real integration setup
- Monitoring and logging
- Client handoff
- And much more!

---

## Testing

### Run Test Scenarios

```bash
python scripts/utils/test_queries.py
```

This displays test scenarios for each script. Run scripts manually and test with provided queries.

### Manual Testing Guide

1. Run a script: `chainlit run scripts/[SCRIPT_NAME]`
2. Open browser (usually `http://localhost:8000`)
3. Try test queries from `scripts/utils/test_queries.py`
4. Verify expected behavior
5. Check terminal for tool calls and logs

---

## Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
pip install -e .
# or
uv sync
```

**"ChromaDB not initialized":**
```bash
python scripts/utils/setup_vectordb.py
```

**OpenAI API errors:**
- Check `.env` file exists
- Verify API key is correct
- Check OpenAI account has credits

**Port already in use:**
```bash
# Use a different port
chainlit run scripts/01_bare_minimum_chatbot.py --port 8001
```

**Slow responses:**
- Check internet connection
- Consider using `gpt-3.5-turbo` instead of `gpt-4`
- Check OpenAI status page

### Get Help

- Review `docs/WORKSHOP_GUIDE.md` for detailed walkthroughs
- Check example conversations in `assets/conversation_examples.md`
- Run `python scripts/utils/validate_setup.py` to diagnose setup issues

---

## Resources

### Official Documentation
- [Chainlit Documentation](https://docs.chainlit.io)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [ChromaDB Documentation](https://docs.trychroma.com)

### Workshop Materials
- `docs/WORKSHOP_GUIDE.md` - Detailed instructor guide
- `docs/CLIENT_PITCH_TEMPLATE.md` - Sales template for prospects
- `docs/PRODUCTION_CHECKLIST.md` - Deployment guide
- `assets/conversation_examples.md` - Example dialogues

### Learning More
- [Chainlit Examples](https://github.com/Chainlit/chainlit/tree/main/examples)
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [RAG Best Practices](https://www.pinecone.io/learn/retrieval-augmented-generation/)

---

## Contributing

This workshop is designed to be a complete, standalone learning resource. If you find issues or have suggestions:

1. For bugs/errors: Open an issue
2. For improvements: Submit a pull request
3. For questions: Use discussions

---

## License

MIT License - Feel free to use this for workshops, client projects, or learning!

---

## Acknowledgments

Built with:
- [Chainlit](https://chainlit.io) - Beautiful chat interfaces
- [OpenAI](https://openai.com) - GPT models and function calling
- [ChromaDB](https://www.trychroma.com) - Vector database
- [Sentence Transformers](https://www.sbert.net) - Embeddings
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager

---

## What's Next?

After completing this workshop, you're ready to:

1. **Customize for a real client** - Pick a local business and adapt the code
2. **Deploy to production** - Use Railway, Render, or your preferred platform
3. **Add integrations** - Connect to real booking systems, CRMs, etc.
4. **Expand features** - Add phone support, multi-language, analytics, etc.
5. **Build a business** - Use the client pitch template to land your first customer

**The code you've built in this workshop is production-ready. Deploy it tonight!**

---

**Questions? Feedback? Share your success stories!**

Happy building! 🚀
