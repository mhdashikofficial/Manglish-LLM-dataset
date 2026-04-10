import json
import random
import os
import re
from datasets import load_dataset
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

# Configuration
TARGET_TOTAL = 25000
CATEGORIES = {
    "casual": 12500,        # 50%
    "transliteration": 6250, # 25%
    "translation": 5000,    # 20%
    "misc": 1250            # 5%
}

def to_manglish(text):
    if not text: return ""
    try:
        return transliterate(text, sanscript.MALAYALAM, sanscript.ITRANS).lower()
    except:
        return text

def parse_prompt(prompt_text):
    # Extracts instruction and response from the Alpaca Prompt format
    instruction = ""
    response = ""
    
    # Split by the markers
    parts = re.split(r'### Instruction:|### Input:|### Response:', prompt_text)
    
    if len(parts) >= 3:
        instruction = parts[1].strip()
        # If there's an input, it might be in parts[2]
        # For simplicity, we'll take the response from the last part
        response = parts[-1].strip()
    
    return instruction, response

def main():
    final_dataset = []
    print("Loading Alpaca dataset and parsing prompts...")
    
    try:
        # Load the dataset
        ds = load_dataset("VishnuPJ/Alpaca_Instruct_Malayalam", split="train")
        rows = list(ds)
        random.shuffle(rows)
        
        parsed_rows = []
        for r in rows:
            inst, resp = parse_prompt(r['Prompt'])
            if inst and resp:
                parsed_rows.append((inst, resp))
        
        print(f"Parsed {len(parsed_rows)} valid rows.")

        # 1. Casual (50% - 12.5k)
        for i in range(CATEGORIES["casual"]):
            inst, resp = parsed_rows[i]
            user_text = inst
            # Randomly mix Manglish into user text
            if random.random() > 0.6:
                user_text = to_manglish(user_text)

            final_dataset.append({
                "messages": [
                    {"role": "system", "content": "You are a friendly assistant who speaks naturally in Malayalam and Manglish. Keep the tone casual and helpful."},
                    {"role": "user", "content": user_text},
                    {"role": "assistant", "content": resp}
                ]
            })

        # 2. Transliteration (25% - 6.25k)
        offset = CATEGORIES["casual"]
        for i in range(CATEGORIES["transliteration"]):
            inst, resp = parsed_rows[offset + i]
            snippet = inst[:150]
            final_dataset.append({
                "messages": [
                    {"role": "system", "content": "You are a linguistics expert. Help the user by translating between Malayalam script and Manglish (Roman script) or vice-versa."},
                    {"role": "user", "content": f"Transliterate to Manglish: {snippet}"},
                    {"role": "assistant", "content": to_manglish(snippet)}
                ]
            })

        # 3. Translation (20% - 5k)
        offset += CATEGORIES["transliteration"]
        for i in range(CATEGORIES["translation"]):
            inst, resp = parsed_rows[offset + i]
            final_dataset.append({
                "messages": [
                    {"role": "system", "content": "You are a professional translator. Translate perfectly between English and Malayalam/Manglish as requested."},
                    {"role": "user", "content": f"Translate this request to Malayalam: {inst}"},
                    {"role": "assistant", "content": resp}
                ]
            })

        # 4. Misc (5% - 1.25k)
        misc_prompts = [
            ("entha cheyyunnu?", "onnum illa, just chill aanu 😌"),
            ("Nalla oru joke parayaamo?", "Oru chali: 'Vellathil veezhathe engane valla-il poya thavalaye edukkaam?' 'Kai upayogichu!' 😂"),
            ("Malayalam cinema-ye patti parayu.", "Malayalam cinema simple stories parayan midukkaraanu.")
        ]
        for i in range(CATEGORIES["misc"]):
            u, a = random.choice(misc_prompts)
            final_dataset.append({
                "messages": [
                    {"role": "system", "content": "You are a versatile AI assistant fluent in Malayalam culture and language."},
                    {"role": "user", "content": u},
                    {"role": "assistant", "content": a}
                ]
            })

    except Exception as e:
        print(f"Error: {e}")

    # Final Shuffle and Save
    random.shuffle(final_dataset)
    final_dataset = final_dataset[:TARGET_TOTAL]

    with open("conversational.json", "w", encoding="utf-8") as f:
        json.dump(final_dataset, f, ensure_ascii=False, indent=2)

    print(f"Final Count: {len(final_dataset)}")
    print("Completed successfully.")

if __name__ == "__main__":
    main()
