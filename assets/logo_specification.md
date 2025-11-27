# Bella's Italian Restaurant Logo Specification

## Design Requirements

Since this is a workshop example, you can create a simple logo or use a placeholder. Here are the specifications if you want to create an actual logo:

### File Format
- **Filename:** `bella_logo.png`
- **Size:** 512x512 pixels
- **Format:** PNG with transparent background
- **Color Mode:** RGB

### Design Concept

**Option 1: Minimalist Monogram**
- Large letter "B" in an elegant serif font (like Playfair Display or Bodoni)
- Italian flag colors (green, white, red) as accent stripe
- Simple, clean, modern

**Option 2: Classic Italian Restaurant**
- Chef's hat icon
- Fork and knife crossed beneath
- Text: "Bella's" in script font
- Warm colors: burgundy, gold, cream

**Option 3: Typography-Based**
- "Bella's" in elegant Italian-style script
- Small tagline: "Since 1985"
- Olive branch or wheat decoration
- Earth tones: terracotta, olive green, cream

### Color Palette

**Primary Colors:**
- Burgundy: #8B1538
- Gold: #D4AF37
- Cream: #F5E6D3

**Accent Colors (Italian Flag):**
- Green: #008C45
- White: #FFFFFF
- Red: #CD212A

### Usage in Chainlit

The logo will be displayed:
- In the chat welcome screen
- As the chat widget icon
- In the header of the chat interface

### Quick Implementation

**For Workshop Purposes:**

You can use a simple placeholder or emoji:
- 🇮🇹 (Italian flag emoji)
- 🍝 (Pasta emoji)
- Or find a free logo from:
  - Canva (free templates)
  - Logomaker.com
  - Or use text-only branding

**In Chainlit Code:**
```python
# If you have a logo file
cl.user_session.set("avatar", cl.Image(path="./assets/bella_logo.png"))

# Or use emoji as simple alternative
# (No special code needed - just use emoji in messages)
```

### Alternative: Text-Only Branding

If you don't want to create a logo, use text-based branding:

```
🇮🇹 BELLA'S
   ITALIAN RESTAURANT
   Since 1985
```

This works perfectly well for a workshop demonstration!
