import json
import re

INPUT_FILE = "unsloth_ready_dataset.json"
OUTPUT_FILE = "unsloth_ready_dataset.json"

PHONETIC_FINAL_MAP = {
    r"\bsrrarttapp\w*\b": "startup",
    r"\bsrrartt\w*\b": "start",
    r"\bstarrtapp\w*\b": "startup",
}

def quick_final_clean():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_data = []

    for entry in data:
        messages = entry.get("messages", [])
        is_valid = True
        new_messages = []
        
        user_text = ""
        assistant_text = ""
        
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            
            if role == "user":
                user_text = content.lower()
            elif role == "assistant":
                content_lower = content.lower()
                
                # Check for refusing/unwanted artifacts
                if any(x in content_lower for x in ["i cannot", "im sorry", "i am sorry", "as an ai", "ethoru ai"]):
                    is_valid = False
                    break
                    
                # Pure hallucinated short numbers
                if re.match(r'^[\d\s\.\,\-]+$', content_lower) and not any(char.isdigit() for char in user_text):
                    is_valid = False
                    break

            for bad, good in PHONETIC_FINAL_MAP.items():
                content = re.sub(bad, good, content, flags=re.IGNORECASE)
                
            new_messages.append({"role": role, "content": content})

        if is_valid and len(new_messages) >= 2:
            cleaned_data.append({"messages": new_messages})

    print(f"Total Kept in FINAL OVERRIDE: {len(cleaned_data)} out of {len(data)}")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    quick_final_clean()
