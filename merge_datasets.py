import json
import random

FILE_1 = "unsloth_ready_dataset.json"
FILE_2 = "dictionary_training_data.json"
OUTPUT_FILE = "final_manglish_llama3_dataset.json"

def merge_datasets():
    print("Loading datasets...")
    with open(FILE_1, "r", encoding="utf-8") as f1:
        data1 = json.load(f1)
        
    with open(FILE_2, "r", encoding="utf-8") as f2:
        data2 = json.load(f2)
        
    print(f"Dataset 1: {len(data1)} items.")
    print(f"Dataset 2: {len(data2)} items.")
    
    combined = data1 + data2
    
    # Shuffle so dictionary entries aren't all clumped at the end during training
    random.shuffle(combined)
    
    print(f"Total Combined Output: {len(combined)} items.")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump(combined, out, ensure_ascii=False, indent=2)
        
    print(f"Saved successfully to {OUTPUT_FILE}!")

if __name__ == "__main__":
    merge_datasets()
