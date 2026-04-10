import json
import random
import re
from datasets import load_dataset
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

SYSTEM_PROMPT = "You are a friendly AI that speaks natural Malayalam and Manglish. Keep responses human-like, clear, and helpful."
TARGET_COUNT = 4000

PHONETIC_MAP = {
    r"\bphamgshan(\w*)": r"function\1",
    r"\bkantettuka\b": "kandethuka",
    r"\bprinr\w*\b": "print",
    r"\bdibagg\w*\b": "debug",
    r"\bsrrartt\w*\b": "start",
    r"\bmatrrka\w*\b": "mathrika",
    r"\butharavadithvam\w*\b": "utharavadithwam",
}

def to_manglish(text):
    if not text: return ""
    try:
        # Simplistic transliteration for data preparation
        res = transliterate(text, sanscript.MALAYALAM, sanscript.ITRANS).lower()
        # Fix some common artifacts of ITRANS for malayalam
        res = res.replace("zha", "zha").replace("ra", "ra") # standard
        return res
    except:
        return text

def parse_prompt(prompt_text):
    parts = re.split(r'### Instruction:|### Input:|### Response:', prompt_text)
    if len(parts) >= 3:
        instruction = parts[1].strip()
        response = parts[-1].strip()
        return instruction, response
    return None, None

def clean_text(text):
    # Remove leakage
    text = re.sub(r'Instruction:|Input:|Output:|###|~~~', '', text)
    # Apply phonetic map
    for bad, good in PHONETIC_MAP.items():
        text = re.sub(bad, good, text, flags=re.IGNORECASE)
    # Basic script isolation check (not mixing in same word - very hard with regex, handled by clean_dataset scripts earlier)
    return text.strip()

def is_good_task(inst, resp):
    # Length filter: Prefer concise responses
    if len(resp.split()) > 60: return False
    if len(inst.split()) > 50: return False
    # Content filter: Avoid very formal/academic markers (rough heuristic)
    formal_markers = ["വിശദീകരിക്കുന്നു", "സംഗ്രഹിക്കുക", "വിലയിരുത്തുക", "വിശകലനം"]
    if any(m in resp for m in formal_markers): return False
    return True

def main():
    print("Loading Alpaca dataset...")
    ds = load_dataset("VishnuPJ/Alpaca_Instruct_Malayalam", split="train")
    rows = list(ds)
    random.shuffle(rows)
    
    task_dataset = []
    
    for r in rows:
        if len(task_dataset) >= TARGET_COUNT:
            break
            
        inst, resp = parse_prompt(r['Prompt'])
        if inst and resp and is_good_task(inst, resp):
            # Naturalize user prompt randomly with Manglish
            user_text = clean_text(inst)
            if random.random() > 0.7:
                user_text = to_manglish(user_text)
            
            assistant_text = clean_text(resp)
            
            task_dataset.append({
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text},
                    {"role": "assistant", "content": assistant_text}
                ]
            })

    print(f"Extracted and cleaned {len(task_dataset)} tasks.")
    with open("extracted_tasks.json", "w", encoding="utf-8") as f:
        json.dump(task_dataset, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
