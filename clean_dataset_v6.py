import json
import re
from collections import defaultdict

INPUT_FILE = "cleaned_conversational_v5.json"
OUTPUT_FILE = "cleaned_conversational_v6.json"

ALLOWED_SHORT_PROMPTS = [
    "hi", "hello", "namaskaram", "entha", "sugamano", "sughamano", "enthokkeyund",
    "parayu", "hai", "heyy", "evideya", "undo"
]

def clean_utf8(text):
    # Remove Zero-Width and invisible characters
    text = re.sub(r'[\u200b\u200c\u200d\u200e\u200f\ufeff]', '', text)
    return text.strip()

def process_v6():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_data = []
    
    user_prompt_signatures = defaultdict(int)

    for entry in data:
        messages = entry.get("messages", [])
        is_valid = True
        new_messages = []
        is_trans_task = False

        user_text = ""
        assistant_text = ""
        
        for msg in messages:
            if msg["role"] == "user":
                user_text = clean_utf8(msg["content"])
                if any(x in user_text.lower() for x in ["engane parayum", "manglish", "translate", "translation", "english sentence"]):
                    is_trans_task = True
            elif msg["role"] == "assistant":
                assistant_text = clean_utf8(msg["content"])

        if not user_text or not assistant_text:
            continue

        # 1. Translation Mismatch Override
        # If asked for a translation, the response should be brief. It shouldn't be an essay or list.
        if is_trans_task:
            u_len = len(user_text)
            a_len = len(assistant_text)
            # If assistant response is completely out of proportion to prompt, it's an explanation.
            # E.g. Prompt (50 chars), Response (300 chars).
            if a_len > (u_len * 2.5) + 50 or "\n" in assistant_text:
                continue

        # 2. Hallucinated / Low-value Outputs
        # Purely numeric or highly abstract short garbage (under 4 chars) without meaning
        if re.match(r'^[\d\W_]+$', assistant_text):
            continue
        if len(assistant_text) < 4 and assistant_text.lower() not in ["yes", "no", "athe", "alla", "illa", "ok", "hm"]:
            continue

        # 3. Incomplete Prompts
        # Prompts that are too short to have context, e.g. "What", "Is it", "14"
        if len(user_text) < 8:
            clean_word = re.sub(r'[^\w]', '', user_text).lower()
            if clean_word not in ALLOWED_SHORT_PROMPTS:
                continue

        # 4. Strict Duplicates Check (Max 2 hits per intent)
        # We strip non-alphanumeric to create an intent signature of the first ~40 characters
        intent_sig = re.sub(r'[\W_]+', '', user_text.lower())[:40]
        user_prompt_signatures[intent_sig] += 1
        
        # Max limit is strict 2.
        if user_prompt_signatures[intent_sig] > 2:
            continue

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")

            if role == "system":
                new_messages.append(msg)
                continue
                
            content = clean_utf8(content)
            
            # Additional minor spelling fixes if any leak
            content = content.replace("vrikshavum", "vriksham")

            new_messages.append({"role": role, "content": content})

        if is_valid and len(new_messages) >= 2:
            cleaned_data.append({"messages": new_messages})

    print(f"Total Kept in FINAL V6: {len(cleaned_data)} out of {len(data)}")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    process_v6()
