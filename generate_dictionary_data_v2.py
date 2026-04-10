import json
import random
import re
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

OUTPUT_FILE = "dictionary_training_data_enriched.json"
VOCAB_FILE = "enriched_vocab_final.json"
SYSTEM_PROMPT = "You are a friendly AI that speaks natural Malayalam and Manglish. Keep responses human-like, clear, and helpful."
TARGET_SIZE = 6000

def to_manglish(text):
    if not text: return ""
    try:
        # Using ITRANS for consistent romanization
        res = transliterate(text, sanscript.MALAYALAM, sanscript.ITRANS).lower()
        # Clean up some common ITRANS artifacts for better 'natural' feel
        res = res.replace("zha", "zha").replace("aa", "a").replace("ii", "i").replace("uu", "u")
        return res
    except:
        return text

def main():
    with open(VOCAB_FILE, "r", encoding="utf-8") as f:
        vocab = json.load(f)
    
    print(f"Loaded {len(vocab)} words for enrichment.")

    templates_m2m = [
        "'{word}' enna vakyathinte malayalam entha?",
        "how to say '{word}' in malayalam script?",
        "'{word}' malayalam font-il type cheyyamo?",
        "malayalam for '{word}'",
        "'{word}' engane malayalam aksharangalil ezhuthum?"
    ]
    
    templates_mal2man = [
        "'{word}' manglish-il ezhuthamo?",
        "type '{word}' in manglish",
        "how to write '{word}' in english letters?",
        "'{word}' adiyamo manglishil?",
        "manglish translation for '{word}'"
    ]

    final_dataset = []
    seen_prompts = set()
    
    # Generate pairs
    word_pairs = []
    for w in vocab:
        man = to_manglish(w)
        if man and w:
            word_pairs.append((man, w))
            
    # Mix in original anchors for quality
    anchors = [
        ("entha", "എന്താ"), ("poyi", "പോയി"), ("varunnu", "വരുന്നു"),
        ("sukhamaano", "സുഖമാണോ"), ("evide", "എവിടെ")
    ]
    word_pairs.extend(anchors)

    # 1. Manglish -> Malayalam (3000)
    while len(final_dataset) < 3000:
        man, mal = random.choice(word_pairs)
        temp = random.choice(templates_m2m).format(word=man)
        if temp not in seen_prompts:
            final_dataset.append({
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": temp},
                    {"role": "assistant", "content": mal}
                ]
            })
            seen_prompts.add(temp)

    # 2. Malayalam -> Manglish (3000)
    while len(final_dataset) < 6000:
        man, mal = random.choice(word_pairs)
        temp = random.choice(templates_mal2man).format(word=mal)
        if temp not in seen_prompts:
            final_dataset.append({
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": temp},
                    {"role": "assistant", "content": man}
                ]
            })
            seen_prompts.add(temp)

    random.shuffle(final_dataset)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_dataset, f, ensure_ascii=False, indent=2)
    
    print(f"Generated {len(final_dataset)} truly enriched dictionary entries.")

if __name__ == "__main__":
    main()
