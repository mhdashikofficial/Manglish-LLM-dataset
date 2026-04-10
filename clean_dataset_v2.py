import json
import re
import random
import os

INPUT_FILE = "cleaned_conversational.json"
OUTPUT_FILE = "cleaned_conversational_v2.json"
SYSTEM_PROMPT = "You are a friendly AI that speaks natural Malayalam and Manglish. Keep responses human-like, clear, and helpful."

# Dictionary for phonetic mappings based on research
PHONETIC_MAP = {
    # known bad phonetics
    "srrakk": "stack",
    "lisrr": "list",
    "erravum": "ettavum",
    "darra": "data",
    r"srrishti\w*": "srishti", # base replacement
    "srrishtikkuka": "srishtikkuka",
    "neshans": "nations",
    "sekyurirri": "security",
    "kaaunsilile": "council-il",
    "amgannal": "angangal",
    "marruka": "mattuka",
    "posirriv": "positive",
    "kriyerriv": "creative",
    "srrori": "story",
    "skriprr": "script",
    "sobhs": "jobs", # steve jobs -> srriv jobs -> steve jobs
    "srriv": "steve",
    "dijirra": "digital",
    "upabhoktrri": "upabhoktaavu",
    "upayoktrri": "upayoktaavu",
    "sisrram": "system",
    "darrabes": "database",
    "sophrr": "soft",
}

# Repair explicit broken malayalam mixed script
BROKEN_SCRIPT_MAP = {
    "തeററaയ": "തെറ്റായ",
    "ഉതതരങങl": "ഉത്തരങ്ങൾ",
    "പaiതതണiലe": "പൈത്തണിലെ",
    "എനന": "എന്ന",
    "കകuക": "ക്കുക",
    "വiശദeeകരi": "വിശദീകരി",
    "മറiകടകകuക": "മറികടക്കുക",
    "ആശയm": "ആശയം",
}

# Known exact duplicates to vary up
KNOWN_DUPLICATE_PROMPTS = [
    "entha cheyyunnu?",
    "Nalla oru joke parayaamo?",
    "Malayalam cinema-ye patti parayu."
]

VARIATIONS = {
    "entha cheyyunnu?": [
        "onnum illa, just chill aanu 😌",
        "njan ivide veruthe irikkukayaanu. entha vishesham?",
        "puthiya karyangal padikkunnu. ningalkkond entha parupadi?",
        "onnumillalla, chill cheyyukayaanu.",
        "ivide work cheyyunnu. ningal entha cheyyunnu?"
    ],
    "Nalla oru joke parayaamo?": [
        "Oru chali: 'Vellathil veezhathe engane valla-il poya thavalaye edukkaam?' 'Kai upayogichu!' 😂",
        "Oru thamaasha kaelkam: 'Pachha nirathilulla aana evide kaanum? Pachha aana illallo!' 😅",
        "Chali venamo? 'Enthukondaanu mathil chaadaan aavathathu? Athu chaadiyaal chumar aakum!' 😂",
        "Oru joke: Kannadiyude munnil ninnal entha onnu randayi kanunnathu? Karanam athu reflection aanu!"
    ],
    "Malayalam cinema-ye patti parayu.": [
        "Malayalam cinema simple stories parayan midukkaraanu.",
        "Malayalam cinemakal realistic aaya kathaapthrathilangalude pereekshyangalil nallathaano.",
        "Mollywood eppozhum nalla stories konduvannittund. Nalla abhinayavum aanu.",
        "Malayalam industry ippol kooduthal fresh ideas kond varunnu."
    ]
}

def fix_manglish_phonetics(text):
    # Apply word-by-word or regex replacements
    for bad, good in PHONETIC_MAP.items():
        if bad.startswith("r") and "\\" in bad:
            # Regex pattern
            text = re.sub(bad, good, text, flags=re.IGNORECASE)
        else:
            # Exact substring or word replace
            text = re.sub(rf'\b{bad}\b', good, text, flags=re.IGNORECASE)
            # Also replace substring if it's very distinct like darra -> data
            if bad in ["darra", "lisrr", "erravum", "srrakk"]:
                text = text.replace(bad, good)
    return text

def fix_broken_malayalam(text):
    for bad, good in BROKEN_SCRIPT_MAP.items():
        text = text.replace(bad, good)
    return text

def is_malayalam_dominant(text):
    ma_count = sum(1 for c in text if '\u0d00' <= c <= '\u0d7f')
    en_count = sum(1 for c in text if 'a' <= c.lower() <= 'z')
    return ma_count >= en_count

def sentence_quality_check(text, is_malayalam):
    if is_malayalam:
        # Avoid mixed scripts in Malayalam: any latin character is an issue
        # Only allow exceptions for formatting if any, but rule says "fully native"
        # However, English words in Malayalam sentences (like "str.add()") might exist and are valid.
        # But if it's just garbage like eററa, it must have been caught by fix_broken_malayalam.
        # If there are lonely a, e, i, u intermixed tightly with malayalam chars, it's corrupted.
        if re.search(r'[\u0d00-\u0d7f][a-zA-Z]{1,2}(?:\s|$)', text):
            # Probably corrupt, e.g., 'തലസ്ഥaനം'
            return False
    else:
        # Manglish should have NO malayalam
        if re.search(r'[\u0d00-\u0d7f]', text):
            return False
    return True

def clean_noise(text):
    # Remove repeated instructions or list numbering mess
    # E.g., '1. 13. 16.' -> handled roughly
    text = re.sub(r'#{3,}.*?(?:Instruction|Input|Output|Response).*?:?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Output:.*?(?:<title>)?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'ശീർഷകം:\s*<title>', '', text)
    text = re.sub(r'~~.*?~~', '', text)
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Simplify multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def process_corpus():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_data = []
    removed_count = 0
    seen_conversations = set()

    for entry in data:
        messages = entry.get("messages", [])
        new_messages = []
        is_valid = True
        
        # Build string to check exact duplicates
        conv_sig = ""

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            
            if role == "system":
                new_messages.append({"role": "system", "content": SYSTEM_PROMPT})
            else:
                # 1. Clean noise
                content = clean_noise(content)
                
                # 2. Fix scripts
                content = fix_broken_malayalam(content)
                
                # 3. Handle duplicates or specific prompts
                if role == "user" and content in KNOWN_DUPLICATE_PROMPTS:
                    conv_sig += content + "|"
                elif role == "assistant" and "onnum illa, just chill aanu" in content: # It's a duplicate answer
                    # Substitute with varied answer
                    parent_q = new_messages[-1]['content'] if new_messages else ""
                    if parent_q in VARIATIONS:
                        content = random.choice(VARIATIONS[parent_q])
                elif role == "assistant" and "Oru chali:" in content:
                    content = random.choice(VARIATIONS["Nalla oru joke parayaamo?"])

                # Determine language
                is_ml_dom = is_malayalam_dominant(content)
                
                if not is_ml_dom:
                    content = fix_manglish_phonetics(content)
                
                # 4. Filter garbled text
                if not sentence_quality_check(content, is_ml_dom):
                    is_valid = False
                    break
                
                if not content.strip():
                    is_valid = False
                    break
                    
                new_messages.append({"role": role, "content": content})
                conv_sig += content + "|"

        # Final check
        if is_valid and len(new_messages) >= 2:
            if conv_sig not in seen_conversations:
                seen_conversations.add(conv_sig)
                cleaned_data.append({"messages": new_messages})
            else:
                # It's a true duplicate (e.g., exact same translation query)
                removed_count += 1
        else:
            removed_count += 1

    total_initial = len(data)
    removal_rate = (removed_count / total_initial) * 100

    print(f"Total Initial: {total_initial}")
    print(f"Cleaned Total: {len(cleaned_data)}")
    print(f"Removed: {removed_count} ({removal_rate:.2f}%)")

    # If removal rate > 10%, warn
    if removal_rate > 10:
        print("WARNING: Removal rate is above 10%!")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    process_corpus()
