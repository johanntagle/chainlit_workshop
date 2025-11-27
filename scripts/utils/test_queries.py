"""
Test Queries
============
Automated testing script for workshop validation.
Tests each script's key features with sample queries.

Usage:
    python scripts/utils/test_queries.py

Note: This is a simplified tester for workshop demonstration.
In production, you'd use proper integration testing with pytest.
"""

from pathlib import Path
import json

# Test cases for each script
TEST_CASES = [
    {
        "script": "01_bare_minimum_chatbot.py",
        "description": "Bare minimum chatbot",
        "test_queries": [
            "Hello",
            "Tell me about yourself"
        ],
        "expected_behavior": "Should respond to basic messages with OpenAI completions"
    },
    {
        "script": "02_with_system_prompt.py",
        "description": "With system prompt and streaming",
        "test_queries": [
            "What are your hours?",
            "Where are you located?"
        ],
        "expected_behavior": "Should respond as Bella's restaurant with business context. Should mention hours: Tuesday-Sunday, 11am-10pm, closed Mondays"
    },
    {
        "script": "03a_input_guardrails.py",
        "description": "Input validation",
        "test_queries": [
            "What's the weather?",  # Off-topic - should reject
            "x" * 600,  # Too long - should reject
            "What time do you open?"  # Valid - should respond
        ],
        "expected_behavior": "Should reject off-topic (weather) and long messages. Should accept valid restaurant questions."
    },
    {
        "script": "03b_output_guardrails.py",
        "description": "Output safety and escalation",
        "test_queries": [
            "I got food poisoning!",  # Should escalate
            "What pasta dishes do you have?"  # Normal query
        ],
        "expected_behavior": "Should immediately escalate health emergency to manager. Should respond normally to menu questions."
    },
    {
        "script": "04a_tools_availability.py",
        "description": "Availability checking tool",
        "test_queries": [
            "Do you have a table for 4 on Friday at 7pm?",
            "Check availability for 2 people next Saturday at 6pm"
        ],
        "expected_behavior": "Should call check_availability tool and return availability information"
    },
    {
        "script": "04b_tools_reservation.py",
        "description": "Reservation creation",
        "test_queries": [
            "I'd like to make a reservation for 4 people on Friday at 7pm",
            # Then follow-up with: "John Smith"
            # Then: "555-0123"
        ],
        "expected_behavior": "Should check availability, then collect name and phone conversationally, then create reservation with confirmation number (BELLA-XXXXXX)"
    },
    {
        "script": "04c_tools_menu_business.py",
        "description": "Menu and business info tools",
        "test_queries": [
            "What pasta dishes do you have?",
            "Do you have parking?",
            "Tell me about your desserts"
        ],
        "expected_behavior": "Should use get_menu_info tool for menu questions and get_business_info for parking/hours questions"
    },
    {
        "script": "05_rag_basic.py",
        "description": "RAG with knowledge base",
        "test_queries": [
            "Do you cater weddings?",
            "What wine pairs with carbonara?",
            "Tell me about your catering options"
        ],
        "expected_behavior": "Should retrieve from knowledge base (FAQ, catering, wine list) and cite sources in responses"
    },
    {
        "script": "06_final_polished.py",
        "description": "Production-ready version",
        "test_queries": [
            "Make a reservation",
            "Show me the menu",
            "What are your hours?"
        ],
        "expected_behavior": "Should show welcome message with action buttons, handle all previous features, track metrics, offer VIP signup after multiple messages"
    }
]


def print_test_case(test_case: dict, index: int):
    """Print a formatted test case"""
    print(f"\n{'='*70}")
    print(f"Test {index}: {test_case['script']}")
    print(f"{'='*70}")
    print(f"\n📝 Description: {test_case['description']}")
    print(f"\n🧪 Test Queries:")
    for i, query in enumerate(test_case['test_queries'], 1):
        if len(query) > 100:
            display_query = query[:100] + "..."
        else:
            display_query = query
        print(f"   {i}. \"{display_query}\"")
    print(f"\n✅ Expected Behavior:")
    print(f"   {test_case['expected_behavior']}")


def main():
    """Main test runner"""
    print("="*70)
    print("Chainlit Workshop - Test Scenarios")
    print("="*70)
    print("\nThis script outlines test scenarios for each workshop script.")
    print("To test a script, run it with Chainlit and try the test queries:")
    print("\n   chainlit run scripts/[SCRIPT_NAME]")
    print("\nThen interact with the chatbot using the test queries below.\n")

    # Print all test cases
    for i, test_case in enumerate(TEST_CASES, 1):
        print_test_case(test_case, i)

    # Summary
    print(f"\n{'='*70}")
    print("Testing Guide")
    print(f"{'='*70}")
    print(f"\nTotal Scripts: {len(TEST_CASES)}")
    print("\n📋 Manual Testing Steps:")
    print("   1. Run a script: chainlit run scripts/[SCRIPT_NAME]")
    print("   2. Open the web interface (usually http://localhost:8000)")
    print("   3. Try each test query from the list above")
    print("   4. Verify the expected behavior occurs")
    print("   5. Check the terminal for any error messages")

    print("\n🔍 What to Look For:")
    print("   ✓ Responses are contextually appropriate")
    print("   ✓ Tools are called when expected (watch terminal)")
    print("   ✓ Guardrails reject inappropriate input")
    print("   ✓ Escalations happen for serious issues")
    print("   ✓ RAG provides source citations")
    print("   ✓ No errors in terminal output")

    print("\n⚠️  Common Issues:")
    print("   - ChromaDB not initialized → Run: python scripts/utils/setup_vectordb.py")
    print("   - OpenAI API errors → Check .env file has valid API key")
    print("   - Import errors → Run: pip install -e .")
    print("   - Port already in use → Stop other Chainlit instances")

    print("\n💡 Pro Tip:")
    print("   Run validate_setup.py first to ensure everything is configured:")
    print("   python scripts/utils/validate_setup.py")

    print("\n✅ All test scenarios documented!")

    # Save test cases to JSON for reference
    output_file = Path(__file__).parent.parent.parent / "docs" / "test_scenarios.json"
    output_file.parent.mkdir(exist_ok=True)

    try:
        with open(output_file, 'w') as f:
            json.dump(TEST_CASES, f, indent=2)
        print(f"\n📄 Test scenarios also saved to: {output_file}")
    except Exception as e:
        print(f"\n⚠️  Could not save test scenarios: {e}")


if __name__ == "__main__":
    main()
