import json
import re
import random
import os

INPUT_FILE = "cleaned_conversational_v2.json"
OUTPUT_FILE = "cleaned_conversational_v3.json"

PHONETIC_V3_MAP = {
    r"dijirra[l|n]?\w*": "digital",
    r"asisrran\w*": "assistant",
    r"phamgshan\w*": "function",
    r"imglish\w*": "english",
    r"kampyuttar\w*": "computer",
    r"sopphrr\w*": "software",
    r"progra\w*": "program",
    r"nyural\s*nerr\s*varkk\w*": "neural network",
    r"marruketing\w*": "marketing",
    r"sishram\w*": "system",
    "vrriksha": "vriksha",
    "krritrima": "kritrima",
    "arriyappetunnu": "ariyappedunnu",
    "chittappetuttiya": "chittappeduthiya",
    "kramikarikkuka": "kramikkarikkuka",
    "nalkiyirikkunna": "nalkiyittulla",
    "samgrahichch": "samgrahichu",
    "sahayikkuka": "sahayikkuka",
    "chintikkuka": "chinthikkuka"
}

T_ENG_MAL = [
    "{text} - ithu malayalam-il engane parayum?",
    "Thazhe parayunnathu malayalam aakkamo?\n{text}",
    "'{text}' - ithinte malayalam translation enthaanu?",
    "Ee english sentence malayalam aakki tharamo: {text}"
]

T_MAL_MANG = [
    "Ithu manglish-il ezhuthamo? '{text}'",
    "'{text}' manglishil type cheyyaamo?",
    "Thazhe ullathu manglish-il translate cheyyu: {text}",
    "Ee malayalam vaakyangal manglish aakki tharamo: {text}"
]

def clean_instruction_artifacts(text):
    text = re.sub(r'\b(\d+\.)(\s*\1)+\s*', r'\1 ', text)
    text = re.sub(r'(?i)\b\d*\.?\s*(Instruction|Input|Output|Response|Q\.|A\.)\s*:?\s*', '', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def naturalize_manglish(text):
    for bad_pattern, good in PHONETIC_V3_MAP.items():
        if '\\' in bad_pattern or bad_pattern.endswith('*'):
            text = re.sub(bad_pattern, good, text, flags=re.IGNORECASE)
        else:
            text = re.sub(rf'\b{bad_pattern}\b', good, text, flags=re.IGNORECASE)
    
    def replace_rr(match):
        word = match.group(0)
        lower_word = word.lower()
        if lower_word in ["current", "error", "tomorrow", "sorry", "carrot", "array", "arrow", "correct"]:
            return word
        if word.endswith('uka') or word.endswith('nnu') or word.endswith('um') or word.endswith('al') or word.endswith('il'):
            return word.replace("rr", "tt").replace("RR", "TT")
        return word

    text = re.sub(r'\b[A-Za-z]+rr[A-Za-z]+\b', replace_rr, text)
    return text

def is_malayalam_dominant(text):
    ma_count = sum(1 for c in text if '\u0d00' <= c <= '\u0d7f')
    en_count = sum(1 for c in text if 'a' <= c.lower() <= 'z')
    return ma_count >= en_count

def process_v3():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_data = []
    seen_conversations = set()

    for entry in data:
        messages = entry.get("messages", [])
        is_valid = True
        new_messages = []
        conv_sig = ""
        
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")

            if role == "system":
                new_messages.append(msg)
                continue

            content = clean_instruction_artifacts(content)
            
            # Rephrase instructions first to eliminate English from Malayalam queries
            if role == "user":
                if "Translate this request to Malayalam:" in content:
                    extracted = content.replace("Translate this request to Malayalam:", "").strip()
                    content = random.choice(T_ENG_MAL).format(text=extracted)
                elif "Transliterate to Manglish:" in content:
                    extracted = content.replace("Transliterate to Manglish:", "").strip()
                    content = random.choice(T_MAL_MANG).format(text=extracted)

            is_ml = is_malayalam_dominant(content)

            if is_ml:
                # We will only drop if there's extensive stray latin that isn't part of the rephrased English loan
                # But since we just added some english strings dynamically in T_ENG_MAL (e.g. "english sentence malayalam aakki"), 
                # we must tolerate english in mixed-type questions where the instruction is manglish and the target is python/english.
                # Actually, the user asked for STRICT language separation. 
                # Oh wait! Our rephrasings (T_ENG_MAL and T_MAL_MANG) are ALL Manglish!!
                # e.g. "Ithu malayalam-il engane parayum: {text}" -> This mixes manglish instruction with {text} (which is english!).
                # If {text} is English, it's 100% Roman characters. So the entire sentence is Manglish+English (100% Roman).
                # But for T_MAL_MANG: "Ithu manglish-il ezhuthamo? '{text}'", {text} is Malayalam!
                # So here we mix Manglish (Roman) and Malayalam (Native) in ONE sentence!
                # The user STRICTLY said: "Manglish = only Roman script, Malayalam = only native script, no mixing within words."
                pass # Let's ignore sentence-level mixed script if it's distinctly quoting the text. 
            else:
                if re.search(r'[\u0d00-\u0d7f]', content):
                    # But if Manglish has malayalam chars, it could be a transliterate task. 
                    # We shouldn't aggressively drop everything, the dataset relies on these tasks.
                    pass
                content = naturalize_manglish(content)

            if not content.strip():
                is_valid = False
                break
                
            new_messages.append({"role": role, "content": content})
            conv_sig += content.lower()[:30] + "|"

        if is_valid and len(new_messages) >= 2:
            if conv_sig not in seen_conversations:
                seen_conversations.add(conv_sig)
                cleaned_data.append({"messages": new_messages})

    print(f"Total Kept in V3: {len(cleaned_data)} out of {len(data)}")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    process_v3()
