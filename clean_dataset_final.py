import json
import re
from collections import defaultdict

INPUT_FILE = "cleaned_conversational_v8.json"
OUTPUT_FILE = "master_conversational_final.json"
SYSTEM_PROMPT = "You are a friendly AI that speaks natural Malayalam and Manglish. Keep responses human-like, clear, and helpful."

PHONETIC_V9_MAP = {
    # Extra Normalizations explicitly requested
    r"\bphamgshan(\w*)": r"function\1",
    r"\bmatrrika\b": "mathrika",
    r"\bmathrika\b": "mathrika",
    r"\bkramikkarikk(\w+)": r"kramikk\1",
    r"\bdibagg\w*\b": "debug",
}

# Leakage drops
LEAKAGE_MARKERS = [
    "Instruction:", "Input:", "Output:", "###", "~~~",
]

# Textbook and low-value markers
TEXTBOOK_MARKERS = [
    "വിശദീകരിക്കുന്നു", "സംഗ്രഹിക്കുക", "വിലയിരുത്തുക", "kunnathaanu", "kkappedunnu", "visadeekarikkunnu"
]

def process_v9():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_data = []
    
    user_prompt_signatures = defaultdict(int)

    for entry in data:
        messages = entry.get("messages", [])
        is_valid = True
        new_messages = []
        is_trans_task = False
        is_translit_task = False

        user_text = ""
        assistant_text = ""
        
        for msg in messages:
            if msg["role"] == "user":
                user_text = msg["content"].lower()
                clean_u = re.sub(r'[^\w]', '', user_text)
                if any(x in user_text for x in ["engane parayum", "translate", "translation", "malayalam aakki"]):
                    is_trans_task = True
                if "manglishil" in user_text or "manglish aakki" in user_text:
                    is_translit_task = True
                    
            elif msg["role"] == "assistant":
                assistant_text = msg["content"]

        if not user_text.strip() or not assistant_text.strip():
            continue

        # 1. TRANSLATION / TRANSLITERATION MISMATCHES
        if is_trans_task or is_translit_task:
            if assistant_text.count('\n') >= 1 or len(assistant_text.split()) > len(user_text.split()) * 2 + 5:
                # Direct deletion if translation boundary breached
                continue
                
        # 2. HALLUCINATION & LOW VALUE CHECKS
        # Numeric without input context
        if re.match(r'^[\d\s\.\,\-]+$', assistant_text):
            # purely numeric answer
            if not any(char.isdigit() for char in user_text):
                continue
        # Tiny generic outputs without proper context
        if len(assistant_text) < 5 and assistant_text.lower() not in ["yes", "no", "athe", "alla", "illa", "ok", "hm"]:
            if len(user_text.split()) < 4:
                continue

        # 3. CONTEXT VALIDATION
        u_words = user_text.split()
        if len(u_words) < 3:
            has_q = any(q in user_text for q in ["entha", "ara", "evide", "eppol", "engane", "enthu", "aaraanu", "ethu", "aar", "what", "who", "where", "when", "how", "why"])
            if not has_q and user_text not in ["hi", "hello", "namaskaram", "sugamano", "sughamano", "enthokkeyund", "evideya", "undo"]:
                continue

        # 4. DUPLICATE LIMITING
        # Use simple alphanumeric extraction
        intent_sig = re.sub(r'[\W_]+', '', user_text.lower())[:35]
        user_prompt_signatures[intent_sig] += 1
        
        # Max limit is strict 2.
        if user_prompt_signatures[intent_sig] > 2:
            continue

        # Message-level checks (Leakage, Tone, Script, Spelling)
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")

            # enforce global system prompt
            if role == "system":
                new_messages.append({"role": "system", "content": SYSTEM_PROMPT})
                continue
                
            # INSTRUCTION LEAKAGE OVERRIDE --> Any presence = DEAD SAMPLE
            if any(leak in content for leak in LEAKAGE_MARKERS):
                is_valid = False
                break
                
            # TONE OVERRIDE --> Any presence = DEAD SAMPLE
            if role == "assistant" and any(tone in content.lower() for tone in TEXTBOOK_MARKERS):
                is_valid = False
                break

            # PHONETICS
            for bad, good in PHONETIC_V9_MAP.items():
                content = re.sub(bad, good, content, flags=re.IGNORECASE)
            
            # String cleaning
            content = content.replace("  ", " ").strip()
            new_messages.append({"role": role, "content": content})

        if is_valid and len(new_messages) >= 2:
            cleaned_data.append({"messages": new_messages})

    print(f"Total Kept in MASTER PIPELINE: {len(cleaned_data)} out of {len(data)}")
    if len(cleaned_data) < 10000:
        print("WARNING: Dataset strictly dropped below 10k margin.")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    process_v9()
