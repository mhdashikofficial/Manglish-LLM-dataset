import json
import random
import re
from collections import defaultdict

CONV_FILE = "unsloth_ready_dataset.json"
TASK_FILE = "extracted_tasks.json"
DICT_FILE = "dictionary_training_data_enriched.json"
OUTPUT_FILE = "final_balanced_dataset.json"

TARGET_CONV_COUNT = 10000
TARGET_TASK_COUNT = 4000
TARGET_DICT_COUNT = 6000

SYSTEM_PROMPT = "You are a friendly AI that speaks natural Malayalam and Manglish. Keep responses human-like, clear, and helpful."

def get_intent_sig(text):
    # Normalize for fuzzy duplicate detection - less aggressive
    return re.sub(r'[\W_]+', '', text.lower())[:100]

def filter_and_sample(data, target_count, label="data", strict_dedup=True):
    # Fuzzy deduplication
    unique_data = []
    seen_intents = set()
    
    # Shuffle first to get arbitrary high-quality samples
    random.shuffle(data)
    
    for item in data:
        user_content = item['messages'][1]['content']
        sig = get_intent_sig(user_content) if strict_dedup else user_content
        if sig not in seen_intents:
            unique_data.append(item)
            seen_intents.add(sig)
            
    print(f"[{label}] Unique count: {len(unique_data)} (out of {len(data)})")
    
    if len(unique_data) < target_count:
        print(f"WARNING: Underflow for {label}. Using all {len(unique_data)} items.")
        return unique_data
    
    return unique_data[:target_count]

def main():
    # 1. Load Conversational
    with open(CONV_FILE, "r", encoding="utf-8") as f:
        conv_raw = json.load(f)
    
    # Filter out potential tasks that might have leaked into conv set
    # (Based on keywords in user prompt)
    task_keywords = [r'translate', r'transliterate', r'parayum', r'ezhuthum', r'akki', r'how to', r'write', r'what is', r'explain']
    pure_conv = []
    leaked_tasks = []
    for item in conv_raw:
        if any(re.search(p, item['messages'][1]['content'].lower()) for p in task_keywords):
            leaked_tasks.append(item)
        else:
            pure_conv.append(item)
            
    dataset_conv = filter_and_sample(pure_conv, TARGET_CONV_COUNT, label="Conversational")

    # 2. Load Tasks
    with open(TASK_FILE, "r", encoding="utf-8") as f:
        tasks_raw = json.load(f)
    # Combine with leaked tasks for diversity
    # (Task pool: 4000 fresh + ~650 leaked)
    dataset_task = filter_and_sample(tasks_raw + leaked_tasks, TARGET_TASK_COUNT, label="Task")

    # 3. Load Dictionary
    with open(DICT_FILE, "r", encoding="utf-8") as f:
        dict_raw = json.load(f)
    # Dictionary data has many similar templates, so use less strict dedup
    dataset_dict = filter_and_sample(dict_raw, TARGET_DICT_COUNT, label="Dictionary", strict_dedup=False)

    # 4. Final Merge
    combined_dataset = dataset_conv + dataset_task + dataset_dict
    
    # Ensure all have the standardized system prompt
    for item in combined_dataset:
        item['messages'][0]['content'] = SYSTEM_PROMPT

    # Global Intense Shuffle
    random.shuffle(combined_dataset)
    random.shuffle(combined_dataset) # Two passes for good measure

    print(f"Final Combined Count: {len(combined_dataset)}")
    
    # Simple ratio verification
    print(f"Ratios -> Conv: {len(dataset_conv)}, Task: {len(dataset_task)}, Dict: {len(dataset_dict)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(combined_dataset, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
