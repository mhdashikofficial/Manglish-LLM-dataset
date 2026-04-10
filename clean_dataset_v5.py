import json
import re
import random

INPUT_FILE = "cleaned_conversational_v4.json"
OUTPUT_FILE = "cleaned_conversational_v5.json"

PHONETIC_V5_MAP = {
    # Final Manglish Quality Fixes
    r"\bphamgshan(\w*)": r"function\1",
    r"\bkantettuka\b": "kandethuka",
    r"\bprinr\w*\b": "print",
    r"\bsaplai cheyin manejmenr\b": "supply chain management",
    r"\bdatabesilekk\w*\b": "database-lekku",
    r"\bbes\b": "base",
    r"\bsaplai\b": "supply",
    r"\bmanejmenr\b": "management",
    r"\bprinri\w*\b": "printing",
}

# Substrings that immediately disqualify an entry
BANNED_STRINGS = [
    "14 ആഴ്ച",                  # Hallucinated answer
    "കാലക്രമ ഘടന",              # Generic bad response
    "യുഎൻ രക്ഷാസമിതി",         # Outdated UN list
    "നിർദ്ദേശം",                 # Malayalam Instruction
    "ഇൻപുട്ട്",                 # Malayalam Input
    "ഔട്ട്പുട്ട്",               # Malayalam Output
]

def clean_v5_phonetics(text):
    for bad, good in PHONETIC_V5_MAP.items():
        text = re.sub(bad, good, text, flags=re.IGNORECASE)
    return text

def is_malayalam_dominant(text):
    ma_count = sum(1 for c in text if '\u0d00' <= c <= '\u0d7f')
    en_count = sum(1 for c in text if 'a' <= c.lower() <= 'z')
    return ma_count >= en_count

def process_v5():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_data = []
    
    # Track jokes strictly
    joke_count = 0
    translation_count = 0
    casual_count = 0

    for entry in data:
        messages = entry.get("messages", [])
        is_valid = True
        new_messages = []
        is_trans_task = False

        # Gather context
        user_text = ""
        assistant_text = ""
        
        for msg in messages:
            if msg["role"] == "user":
                user_text = msg["content"].lower()
                if any(x in user_text for x in ["engane parayum", "manglish", "translate", "translation", "english sentence"]):
                    is_trans_task = True
            elif msg["role"] == "assistant":
                assistant_text = msg["content"]

        # Validate Translation Outputs
        # If it's a translation task, the assistant should just provide the translated phrase.
        # If the assistant text is overly long, has bullets or numbering (e.g., explains), drop it.
        if is_trans_task:
            if len(assistant_text.split('\n')) > 2 or re.search(r'^\d+\.', assistant_text, flags=re.MULTILINE) or "-" in assistant_text[:5]:
                # Looks like a list or explanation
                continue

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")

            if role == "system":
                new_messages.append(msg)
                continue

            # Hard banned strings
            if any(b in content for b in BANNED_STRINGS):
                is_valid = False
                break
                
            # Interspersed Script Ban (e.g. നerrവർക്ക്ക്)
            # Regex catches sequences of [Malayalam][English][Malayalam] tightly grouped together
            if re.search(r'[\u0d00-\u0d7f]+[a-zA-Z]+[\u0d00-\u0d7f]+', content):
                is_valid = False
                break

            # Phonetic cleanup
            content = clean_v5_phonetics(content)

            new_messages.append({"role": role, "content": content})

        if not is_valid or len(new_messages) < 2:
            continue

        # Joke duplicate culling (max 3 allowed)
        if "joke parayaamo" in user_text or "chali venamo" in user_text:
            joke_count += 1
            if joke_count > 3:
                continue

        # Balance tasks: Downsample translation another 15%
        if is_trans_task:
            if random.random() < 0.15:
                continue
            translation_count += 1
        else:
            casual_count += 1

        cleaned_data.append({"messages": new_messages})

    print(f"Total Kept in V5: {len(cleaned_data)} out of {len(data)}")
    print(f"Final Spread -> Conversational: {casual_count}, Processing/Translating: {translation_count}")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    process_v5()
