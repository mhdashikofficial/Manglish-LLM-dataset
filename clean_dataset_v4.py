import json
import re
import random
import os
from collections import defaultdict

INPUT_FILE = "cleaned_conversational_v3.json"
OUTPUT_FILE = "cleaned_conversational_v4.json"

PHONETIC_V4_MAP = {
    # New user requested fixes
    r"\bdibagg\w*": "debug",
    r"\bkyuvum\b": "queue-um",
    r"\bkyu\b": "queue",
    r"\bvttiksha\w*": "vriksha",
    r"\bvrriksha\w*": "vriksha",
    
    # "phamgshanre" -> "functioninte"
    r"\bphamgshanre\b": "functioninte",
    r"\bphamgshan\w*": "function",
    
    # Catching additional artifacts
    r"\berravum\b": "ettavum",
    r"\bkrritrima\w*": "kritrima",
}

def clean_instruction_leakage(text):
    # Remove instructional labels that leaked into the assistant or user response
    text = re.sub(r'(?im)^(?:\#+\s*)?(?:Instruction|Input|Output|Response|Q|A)[:\.]\s*', '', text)
    text = re.sub(r'(?i)\b(?:Instruction|Input|Output|Response)[:\.]\s+', '', text)
    
    # Fix broken numbering lists like "13. 13. 16." -> convert inline mess to simple
    # If we see multiple identical numbers in a row, compress them
    text = re.sub(r'\b(\d+\.)(\s*\1)+\s*', r'\1 ', text)
    
    # Remove hanging empty list items
    text = re.sub(r'(?m)^\d+\.\s*$', '', text)
    
    # Simplify extra newlines caused by removing tags
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def polish_manglish_phonetics(text):
    for bad_pattern, good in PHONETIC_V4_MAP.items():
        text = re.sub(bad_pattern, good, text, flags=re.IGNORECASE)
        
    def secondary_rr_fix(match):
        word = match.group(0)
        # Avoid breaking legitimate words
        if word.lower() in ["current", "error", "carrot", "arrow", "sorry", "tomorrow", "array"]:
            return word
        # For general Manglish words ending in malayalam suffixes, convert rr->tt
        if word.endswith(('uka', 'nnu', 'um', 'al', 'il', 'an')):
            return word.replace("rr", "tt").replace("RR", "tt")
        return word
        
    text = re.sub(r'\b[A-Za-z]+rr[A-Za-z]*\b', secondary_rr_fix, text)
    
    return text

def is_malayalam_dominant(text):
    ma_count = sum(1 for c in text if '\u0d00' <= c <= '\u0d7f')
    en_count = sum(1 for c in text if 'a' <= c.lower() <= 'z')
    return ma_count >= en_count

def process_v4():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_data = []
    seen_conversations = set()
    user_prompt_counts = defaultdict(int)

    tasks_count = {"transl": 0, "conversational": 0}

    for entry in data:
        messages = entry.get("messages", [])
        is_valid = True
        new_messages = []
        
        # We uniquely identify a conversation by user text and assistant text combined.
        conv_sig = ""
        user_text_clean = ""
        is_trans_task = False

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")

            if role == "system":
                new_messages.append(msg)
                continue

            # LEAKAGE FIX
            content = clean_instruction_leakage(content)

            # SCRIPT DISCOVERY & TRANSLATION CLASSIFICATION
            is_ml = is_malayalam_dominant(content)
            
            if role == "user":
                user_text_clean = content.strip().lower()
                # Determine if it's a Translation or Transliteration Task
                if any(x in user_text_clean for x in ["engane parayum", "manglish", "translate", "translation", "english sentence"]):
                    is_trans_task = True
            
            if is_ml:
                # Basic sanity
                if len(re.findall(r'[A-Za-z]{3,}', content)) > 1 and not is_trans_task:
                    is_valid = False
            else:
                # Manglish/English side
                if re.search(r'[\u0d00-\u0d7f]', content):
                    # Strict isolation: Manglish words shouldn't be near Malayalam blocks
                    # Sometimes quotes contain Malayalam. But the user asked for strict "no mixing".
                    # We will drop the sample if it inherently mixes scripts to be very safe.
                    is_valid = False
                else:
                    content = polish_manglish_phonetics(content)

            if not content.strip():
                is_valid = False
                
            new_messages.append({"role": role, "content": content})
            conv_sig += content.strip().lower() + "|"

        if not is_valid or len(new_messages) < 2:
            continue

        # TASK BIAS REDUCTION
        # We roughly downsample translation tasks by 25% to make conversational ones more prominent.
        if is_trans_task:
            if random.random() < 0.25:
                continue
            tasks_count["transl"] += 1
        else:
            tasks_count["conversational"] += 1

        # DEDUPLICATION: Restrict identical user prompts mapping to identical/similar answers
        # If user exactly asks the same thing, allow up to 3 variations, then drop
        if conv_sig in seen_conversations:
            continue
            
        user_prompt_counts[user_text_clean] += 1
        if user_prompt_counts[user_text_clean] > 3:
            # We already have 3 answers for this exact prompt, ignore further repetitions to boost diversity
            continue

        seen_conversations.add(conv_sig)
        cleaned_data.append({"messages": new_messages})

    print(f"Total Kept in V4: {len(cleaned_data)} out of {len(data)}")
    print(f"Task Types retained -> Conversational: {tasks_count['conversational']}, Translation/Transliteration: {tasks_count['transl']}")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    process_v4()
