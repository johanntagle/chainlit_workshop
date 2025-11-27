# Conversation Examples
## Realistic Dialogue Flows for Bella's Italian Restaurant Chatbot

These examples demonstrate the chatbot's capabilities across different scenarios.

---

## Example 1: Simple Reservation (Happy Path)

**User:** Hi, do you have a table for 4 this Friday at 7pm?

**Bot:** Buongiorno! I'd be happy to check availability for you. Let me see what we have for Friday evening.

*[Uses check_availability tool]*

**Bot:** Great news! We have tables available this Friday at 7:00 PM for 4 guests. Would you like me to make a reservation for you?

**User:** Yes please

**Bot:** Wonderful! I'll need a few details to complete your reservation. What name should I put this under?

**User:** Sarah Martinez

**Bot:** Thank you, Sarah! And what's the best phone number to reach you?

**User:** 555-0192

*[Uses create_reservation tool]*

**Bot:** Perfect! Your reservation is confirmed:

- **Confirmation #:** BELLA-384756
- **Name:** Sarah Martinez
- **Date:** Friday, November 29th, 2024
- **Time:** 7:00 PM
- **Party Size:** 4 guests
- **Phone:** (555) 555-0192

We'll see you Friday! If you need to modify or cancel, please call us at (555) 123-4567 with your confirmation number.

---

## Example 2: Menu Question with Dietary Restrictions

**User:** What vegetarian pasta options do you have?

**Bot:** Let me show you our delicious vegetarian pasta dishes!

*[Uses get_menu_info tool with category="pasta", dietary_filter="vegetarian"]*

**Bot:** We have several wonderful vegetarian pasta options:

🍝 **Fettuccine Alfredo** - $17
Fresh fettuccine in a rich cream and parmesan sauce

🍝 **Penne Arrabbiata** - $16
Penne in a spicy tomato sauce with garlic and red chili peppers (also vegan!)

🍝 **Ravioli di Ricotta e Spinaci** - $18
House-made ravioli filled with ricotta and spinach in sage butter sauce

All our pasta is made fresh daily! Would you like to hear wine pairing suggestions for any of these dishes?

**User:** What wine goes with the ravioli?

**Bot:** Excellent choice! For our Ravioli di Ricotta e Spinaci, I'd recommend a crisp Pinot Grigio.

*[Retrieved from RAG - wine_list.md]*

We have two wonderful options:
- **Santa Margherita Pinot Grigio** ($42 bottle / $12 glass) - Crisp and light with citrus notes
- **Livio Felluga Pinot Grigio** ($38 bottle / $10 glass) - Mineral-driven with stone fruit

Both pair beautifully with the creamy ricotta and delicate sage butter. Would you like to make a reservation?

---

## Example 3: Catering Inquiry (RAG Retrieval)

**User:** Do you cater weddings?

**Bot:** Yes, we'd love to cater your wedding! Congratulations!

*[Retrieved from RAG - catering.md]*

We offer several wedding catering options:

**Plated Service** (Starting at $65/person)
- Cocktail hour with passed appetizers
- Choice of salad or soup
- Two entree options (guest's choice or duet-style)
- Wedding cake service
- Full professional waitstaff

**Buffet Service** ($35-45/person)
- More casual but still elegant
- Multiple pasta and protein options
- Perfect for larger weddings

We can accommodate 20-200 guests and offer complimentary menu tastings for weddings over $2,000.

Would you like me to have our catering coordinator call you to discuss your specific needs?

**User:** Yes please, my number is 555-0234

**Bot:** Perfect! I'll have our catering team call you at (555) 555-0234. They typically respond within 24 hours, or you can call them directly at (555) 123-4568.

May I ask what date you're planning for? Just so they have that information when they call.

**User:** June 15th next year, around 120 guests

**Bot:** Wonderful - June weddings are beautiful! I've noted:
- Date: June 15, 2025
- Guest Count: ~120
- Contact: (555) 555-0234

Our catering team will reach out soon. In the meantime, you can view our full catering menu at www.bellasitalian.com/catering.

Best wishes on your upcoming wedding! 🎉

---

## Example 4: Hours & Location Question

**User:** What time do you close?

*[Uses get_business_info tool]*

**Bot:** Our hours vary by day:

⏰ **Regular Hours:**
- **Tuesday-Thursday:** 11:00 AM - 10:00 PM
- **Friday:** 11:00 AM - 11:00 PM
- **Saturday:** 10:00 AM - 11:00 PM (Brunch 10am-2pm)
- **Sunday:** 10:00 AM - 9:00 PM (Brunch 10am-2pm)
- **Monday:** Closed

We're located at 123 Main Street, Downtown, CA 90210. We validate parking at Main Street Garage (2 hours free with dining).

Would you like to make a reservation?

---

## Example 5: Complaint Escalation

**User:** I ordered takeout last night and the food arrived cold and the wrong order!

*[Escalation trigger detected]*

**Bot:** I'm very sorry to hear about your experience - that's definitely not the quality we aim for, and I want to make sure this is handled properly.

This situation needs immediate attention from our management team. Please call us right away at (555) 123-4567 so we can address this correctly, or give me your phone number and I'll have a manager call you back within the hour.

We truly apologize and want to make this right.

**User:** Have them call me at 555-9876

**Bot:** Thank you. I've escalated your concern to our management team, and they'll call you at (555) 555-9876 within the hour.

Again, I apologize for the poor experience. Your satisfaction is very important to us.

*[Logs escalation for management review]*

---

## Example 6: Off-Topic Rejection

**User:** What's the weather going to be like this weekend?

*[Input guardrail triggered]*

**Bot:** I'm here to help with Bella's Italian Restaurant - reservations, menu questions, and more. For weather information, you might want to check a weather service.

Can I help you with anything about our restaurant? Perhaps you're planning to dine with us this weekend?

---

## Example 7: After-Hours Availability

**User:** Can I come in at 11pm on Saturday?

*[Tool checks business hours]*

**Bot:** On Saturdays, we're open from 10:00 AM to 11:00 PM, so 11pm would be right at closing time. Our kitchen typically stops taking orders around 10:30 PM.

Would you like to make a reservation for an earlier time on Saturday? We have great availability between 5-9 PM!

---

## Example 8: Party Too Large

**User:** Table for 12 people tomorrow at 7pm?

*[Tool detects party size >= 8]*

**Bot:** For parties of 12, I recommend our private dining room to ensure you have a wonderful experience!

Please call us directly at (555) 123-4567 to arrange this special booking. Our team can discuss menu options and setup that would work best for your group.

You can also email events@bellasitalian.com. Would you like me to note anything specific about your party (celebration, business dinner, etc.)?

---

## Example 9: Wine Pairing Question (RAG)

**User:** I'm ordering the Spaghetti Carbonara, what wine should I get?

**Bot:** Excellent choice! Our Spaghetti Carbonara is one of our most popular dishes.

*[Checks menu.json for wine pairing + retrieves from wine_list.md]*

For Carbonara, I recommend **Pinot Grigio** - the crisp, light character complements the rich, creamy sauce beautifully.

Specifically, our **Santa Margherita Pinot Grigio** ($42 bottle / $12 glass) from Alto Adige is perfect. It has notes of citrus and green apple with a clean, refreshing finish that cuts through the richness of the pancetta and eggs.

Would you like to add that to your order, or would you like other wine suggestions?

---

## Example 10: Multi-Turn Conversation with Memory

**User:** Do you have outdoor seating?

*[Retrieved from FAQ]*

**Bot:** Yes! Our patio seats 20 guests and is open weather permitting from April through October. It's first-come, first-served for walk-ins, but you can request patio seating when making reservations (subject to availability).

**User:** Can I bring my dog?

**Bot:** On our patio, well-behaved dogs are absolutely welcome! We'll even bring them water. 🐕

Service animals are welcome throughout the restaurant, of course.

Would you like to request patio seating for a reservation?

**User:** Yes, for 2 people Saturday at 6pm

**Bot:** Perfect! Let me check patio availability for Saturday at 6:00 PM for 2 guests.

*[Uses check_availability]*

**Bot:** Great news! We have patio seating available Saturday at 6:00 PM for 2 (and your pup is welcome!).

What name should I put the reservation under?

*[Continues reservation process...]*

---

## Example 11: Gluten-Free Question

**User:** Do you have gluten free options?

**Bot:** Yes, we have several gluten-free options!

*[Retrieved from FAQ]*

We offer gluten-free pasta for most of our pasta dishes at no extra charge, and we also have gluten-free pizza crust available.

Some of our naturally gluten-free dishes include:
- Grilled Salmon with seasonal vegetables
- Bistecca alla Fiorentina (T-bone steak)
- Caprese Salad
- Many of our seafood and meat entrees

**Important:** While we take precautions to avoid cross-contamination, our kitchen is not a dedicated gluten-free facility. Please let us know if you have celiac disease so we can take extra care.

Would you like to see specific gluten-free menu items, or make a reservation?

---

## Example 12: Closed Monday

**User:** Reservation for Monday at 7pm

*[Tool detects Monday - closed]*

**Bot:** We're closed on Mondays to give our team a well-deserved rest!

We're open Tuesday through Sunday:
- Tuesday-Thursday: 11am-10pm
- Friday: 11am-11pm
- Saturday: 10am-11pm
- Sunday: 10am-9pm

Would you like to make a reservation for Tuesday evening instead? Or perhaps this coming weekend?

---

## Example 13: VIP List Signup (After Multiple Messages)

*[After 5+ messages in conversation]*

**Bot:** By the way, would you like to join our VIP list for exclusive offers and event invitations? We occasionally host wine tastings, cooking classes, and special chef's dinners!

**User:** Sure!

**Bot:** Wonderful! What email address should I use?

**User:** sarah@email.com

**Bot:** Perfect! I've added sarah@email.com to our VIP list. You'll receive our monthly newsletter with special offers, new menu items, and exclusive event invitations.

Thank you for being a Bella's VIP! 🌟

*[Saves to leads.json]*

---

## Example 14: Complex Menu Question (RAG + Tools)

**User:** I'm allergic to shellfish. What can I eat?

**Bot:** Thank you for letting me know about your shellfish allergy - we take allergies very seriously!

*[Retrieved from FAQ + searches menu]*

We have many delicious options that are shellfish-free:

**Pasta:**
- Spaghetti Carbonara
- Fettuccine Alfredo
- Pappardelle Bolognese
- And most other pasta dishes (except Linguine alle Vongole and Frutti di Mare)

**Pizza:** All our pizzas are shellfish-free

**Entrees:**
- Chicken Parmigiana
- Veal Marsala
- Osso Buco
- Bistecca alla Fiorentina
- Salmon (fish, not shellfish)

**Important:** Please inform your server when you arrive so our kitchen can take extra precautions to avoid cross-contamination. They can also guide you through the full menu with your allergy in mind.

Would you like to make a reservation? We'll note your allergy.

---

These examples demonstrate:
✅ Tool usage (availability, reservations, menu, business info)
✅ RAG retrieval (FAQ, catering, wine list)
✅ Guardrails (off-topic, closed days, party size)
✅ Escalation (complaints, serious issues)
✅ Multi-turn conversations with memory
✅ Natural, helpful responses
✅ Business value (lead capture, bookings, information)
