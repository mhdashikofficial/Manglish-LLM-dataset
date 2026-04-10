import json
import re
from collections import defaultdict

INPUT_FILE = "cleaned_conversational_v7.json"
OUTPUT_FILE = "cleaned_conversational_v8.json"

PHONETIC_V8_MAP = {
    # Deep scrub for remaining manglish
    r"\bmatrrka\w*\b": "mathrika",
    r"\bmathrrka\w*\b": "mathrika",
    r"\bmatrika\b": "mathrika",
    r"\bmathrikayaya\b": "mathrikayaya",
    r"\butharavadithvam\w*\b": "utharavadithwam",
}

def deep_phonetic_clean_v8(text):
    for bad, good in PHONETIC_V8_MAP.items():
        text = re.sub(bad, good, text, flags=re.IGNORECASE)
    return text

def process_v8():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_data = []

    for entry in data:
        messages = entry.get("messages", [])
        is_valid = True
        new_messages = []
        is_trans_task = False

        user_text = ""
        assistant_text = ""
        
        for msg in messages:
            if msg["role"] == "user":
                user_text = msg["content"].lower()
                if any(x in user_text for x in ["engane parayum", "manglish", "translate", "translation", "english sentence"]):
                    is_trans_task = True
            elif msg["role"] == "assistant":
                assistant_text = msg["content"]

        if not user_text.strip() or not assistant_text.strip():
            continue

        # 1. TRANSLATION STRICTNESS: 
        # If the user prompt asks for translation, it should be highly restricted output.
        if is_trans_task:
            if assistant_text.count('\n') >= 1 or len(assistant_text.split()) > len(user_text.split()) * 2 + 3:
                continue

        # 2. CONTEXT-LESS SAMPLES
        user_words = user_text.split()
        if len(user_words) < 3:
            # Short prompt. Let's see if there's any question markers.
            has_q = any(q in user_text for q in ["entha", "ara", "evide", "eppol", "engane", "enthu", "aaraanu", "ethu", "aar", "what", "who", "where", "when", "how", "why"])
            if not has_q:
                # If there is no question, then a lengthy response is hallucinated/context-less
                if len(assistant_text.split()) > 10:
                    continue

        # 3. HALLUCINATION OUTLIERS
        # Purely numeric or strange outputs
        if re.match(r'^[\d\s\.\,\-]+$', assistant_text):
            continue
            
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")

            if role == "system":
                new_messages.append(msg)
                continue
                
            content = deep_phonetic_clean_v8(content)
            
            # General string cleaning
            content = content.replace("  ", " ").strip()
            
            new_messages.append({"role": role, "content": content})

        if is_valid and len(new_messages) >= 2:
            cleaned_data.append({"messages": new_messages})

    print(f"Total Kept in FINAL V8: {len(cleaned_data)} out of {len(data)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    process_v8()
