import json
import re

INPUT_FILE = "master_conversational_final.json"
OUTPUT_FILE = "unsloth_ready_dataset.json"

# Refusal Triggers
REFUSAL_TRIGGERS = [
    "as an ai", "i cannot", "i'm sorry", "i am sorry", 
    "njan oru ai", "njan oru artificial intelligence", 
    "oru ai aanu", "oru ai model aanu",
    "enikku athu cheyyan", "enik ath cheyyan",
    "sadhyamalla", "ethoru ai"
]

# Random Hallucinated Fragments
HALLUCINATED_FRAGMENTS = [
    "25 പേർ", "125", "10", "25 per"
]

def process_micro_clean():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_data = []

    for entry in data:
        messages = entry.get("messages", [])
        is_valid = True
        
        user_text = ""
        
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            
            if role == "user":
                user_text = content.lower()

            if role == "assistant":
                content_lower = content.lower()
                
                # 1. AI Refusal drops
                if any(refusal in content_lower for refusal in REFUSAL_TRIGGERS):
                    is_valid = False
                    break
                    
                # 2. Strict Hallucination Numbers
                # Drop responses that are entirely digits or exactly matching generic bad items 
                # (like "25 per") if no contextual word exists in user prompt identifying exactly 25.
                if content_lower in HALLUCINATED_FRAGMENTS or re.match(r'^[\d\.\s\,\-]+$', content):
                    if not any(char.isdigit() for char in user_text):
                        is_valid = False
                        break
                        
                if "25 പേർ" in content or "125" in content:
                    if "25" not in user_text and "125" not in user_text:
                        # Definite hallucination
                        is_valid = False
                        break

        if is_valid:
            cleaned_data.append(entry)

    print(f"Total Kept in FINAL MICRO CLEAN: {len(cleaned_data)} out of {len(data)}")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    process_micro_clean()
