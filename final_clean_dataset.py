import json
import re

INPUT_FILE = "final_balanced_dataset.json"
OUTPUT_FILE = "final_balanced_dataset_v2.json"

PHONETIC_MAP = {
    r"\bphamgshan(\w*)": r"function\1",
    r"\bkantettuka\b": "kandethuka",
    r"\bprinr\w*\b": "print",
    r"\bdibagg\w*\b": "debug",
    r"\bsrrartt\w*\b": "start",
    r"\bmatrrka\w*\b": "mathrika",
    r"\butharavadithvam\w*\b": "utharavadithwam",
    r"srr": "rr", # Correcting the excessive r's
    r"ttt": "tt",
    r"rrr": "rr"
}

def clean_entry(entry):
    for msg in entry['messages']:
        content = msg['content']
        for bad, good in PHONETIC_MAP.items():
            content = re.sub(bad, good, content, flags=re.IGNORECASE)
        msg['content'] = content.strip()
    return entry

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        dataset = json.load(f)
    
    cleaned_dataset = [clean_entry(e) for e in dataset]
    
    # Save the final version
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_dataset, f, ensure_ascii=False, indent=2)
    
    print(f"Final cleaning complete. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
