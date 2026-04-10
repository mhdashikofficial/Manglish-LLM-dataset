import json
import re

INPUT_FILE = "cleaned_conversational_v6.json"
OUTPUT_FILE = "cleaned_conversational_v7.json"

PHONETIC_V7_MAP = {
    # Deep scrub for manglish typing styles requested
    r"\bphamgshan(\w*)": r"function\1",
    r"\bkantettuka\b": "kandethuka",
    r"\bprinr\w*\b": "print",
    r"\bdibagg\w*\b": "debug",
    r"\bsaplai\b": "supply",
    r"\bmanejmenr\b": "management",
    r"\bprinri\w*\b": "printing",
}

# Heavily rigid, textbook-style formal words indication.
FORMAL_MALAYALAM_TRIGGERS = [
    "പ്പെടുന്നു", "ക്കുന്നതാണ്", "വിശദീകരിക്കുന്നു", "സംഗ്രഹിക്കുക", "വിലയിരുത്തുക",
]
FORMAL_MANGLISH_TRIGGERS = [
    "kunnathaanu", "kkappedunnu", "ppettu", "appettu", "visadeekarikkunnu"
]

QUESTION_WORDS_ML = ["entha", "ara", "evide", "eppol", "engane", "enthu", "aaraanu", "ethu", "aar"]
QUESTION_WORDS_EN = ["what", "who", "where", "when", "how", "why", "which"]

def deep_phonetic_clean(text):
    for bad, good in PHONETIC_V7_MAP.items():
        text = re.sub(bad, good, text, flags=re.IGNORECASE)
    return text

def is_unnatural_formal(text, is_ml):
    text_lower = text.lower()
    if is_ml:
        if any(term in text for term in FORMAL_MALAYALAM_TRIGGERS):
            return True
    else:
        if any(term in text_lower for term in FORMAL_MANGLISH_TRIGGERS):
            # Check length: if it's very long and formal, it's definitely a textbook dump.
            if len(text.split()) > 10:
                return True
    return False

def process_v7():
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

        # 1. TRANSLATION STRICTNESS: Translation tasks MUST return 1-2 lines.
        if is_trans_task:
            if assistant_text.count('\n') >= 2 or len(assistant_text.split()) > len(user_text.split()) * 2 + 5:
                # Response is too long for a basic translation mapping.
                continue

        # 2. CONTEXT-LESS SAMPLES
        user_words = user_text.split()
        if len(user_words) < 4:
            has_q = any(q in user_text for q in QUESTION_WORDS_ML + QUESTION_WORDS_EN)
            if not has_q:
                # Context-less short prompt. If response is unnaturally long, drop it.
                if len(assistant_text.split()) > 15:
                    continue

        # 3. HALLUCINATION & TONE FILTER
        # Dropping deeply formal or structurally weird sentences to keep it ELITE
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")

            if role == "system":
                new_messages.append(msg)
                continue
                
            # Tone Optimization
            ma_count = sum(1 for c in content if '\u0d00' <= c <= '\u0d7f')
            en_count = sum(1 for c in content if 'a' <= c.lower() <= 'z')
            is_ml = ma_count >= en_count

            if role == "assistant":
                if is_unnatural_formal(content, is_ml):
                    is_valid = False
                    break

            content = deep_phonetic_clean(content)
            new_messages.append({"role": role, "content": content})

        if is_valid and len(new_messages) >= 2:
            cleaned_data.append({"messages": new_messages})

    print(f"Total Kept in ELITE V7: {len(cleaned_data)} out of {len(data)}")
    
    # Dataset limits warning
    if len(cleaned_data) < 10000:
        print("WARNING: Dataset strictly dropped below 10k margin.")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    process_v7()
