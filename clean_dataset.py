import json
import re
import unicodedata
import os

# Configuration
INPUT_FILE = "conversational.json"
OUTPUT_FILE = "cleaned_conversational.json"
SYSTEM_PROMPT = "You are a friendly AI that speaks natural Malayalam and Manglish. Keep responses human-like, clear, and helpful."

# Mapping for common Malayalam chars that appear in "Manglish" output
TRANSLIT_MAPPING = {
    '~': '',
    'ൻ': 'n',
    'ർ': 'r',
    'ൽ': 'l',
    'ൾ': 'l',
    'ൺ': 'n',
    'ാ': 'a',
    'ി': 'i',
    'ീ': 'ee',
    'ു': 'u',
    'ൂ': 'oo',
    'െ': 'e',
    'േ': 'e',
    'ൈ': 'ai',
    'ൊ': 'o',
    'ോ': 'o',
    'ൗ': 'au',
    'ം': 'm',
    '്': '',
    'ൗ': 'au',
    'ർ': 'r',
    'ൾ': 'l',
    'ൺ': 'n',
    'ൽ': 'l',
    'ൻ': 'n'
}

def remove_accents(text):
    # Normalizes to decomposed form and removes non-spacing marks (accents)
    nkfd_form = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nkfd_form if not unicodedata.combining(c)])

def clean_manglish(text):
    if not text: return ""
    
    # 1. Remove accents (è, ò, etc)
    text = remove_accents(text)
    
    # 2. Map native chars in manglish text
    for char, mapped in TRANSLIT_MAPPING.items():
        text = text.replace(char, mapped)
    
    # 3. Final cleaning of weird symbols (~, `, etc)
    text = re.sub(r'[~`#\*]', '', text)
    
    # 4. Standardize common words (best effort regex)
    # This is a bit risky but good for common patterns
    text = re.sub(r'\b(an)\b', 'aanu', text) # common short form of aanu
    text = re.sub(r'\bnjan\b', 'njan', text) # ensure njan
    
    return text.strip()

def contains_malayalam_script(text):
    # Malayalam Unicode block is 0D00-0D7F
    return any('\u0d00' <= c <= '\u0d7f' for c in text)

def clean_sentence(text):
    if not text: return ""
    
    # Remove obvious noise like ~~~ blocks
    text = re.sub(r'~~.*?~~', '', text)
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    
    # Determine if it's a Malayalam script sentence or Manglish
    # Count Malayalam chars vs Latin chars
    malayalam_count = sum(1 for c in text if '\u0d00' <= c <= '\u0d7f')
    latin_count = sum(1 for c in text if 'a' <= c.lower() <= 'z')
    
    if malayalam_count > latin_count:
        # Malayalam Script Sentence: Keep as is but remove stray ~ or #
        return re.sub(r'[~#]', '', text).strip()
    else:
        # Manglish Sentence: Full cleaning
        return clean_manglish(text)

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    print(f"Loading {INPUT_FILE}...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Cleaning {len(data)} entries...")
    cleaned_data = []
    
    for entry in data:
        messages = entry.get("messages", [])
        new_messages = []
        
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            
            if role == "system":
                new_messages.append({"role": "system", "content": SYSTEM_PROMPT})
            else:
                cleaned_content = clean_sentence(content)
                if cleaned_content: # Filter out empty responses
                    new_messages.append({"role": role, "content": cleaned_content})
        
        if len(new_messages) >= 2: # Ensure we at least have user/assistant
            cleaned_data.append({"messages": new_messages})

    print(f"Saving {len(cleaned_data)} entries to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

    print("Cleaning complete.")

if __name__ == "__main__":
    main()
