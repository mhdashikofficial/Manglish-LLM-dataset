import json
import re
from collections import Counter

def analyze():
    with open('conversational.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    broken_samples = []
    phonetic_patterns = Counter()
    
    for entry in data:
        for msg in entry['messages']:
            content = msg['content']
            
            # Check for broken mixed script
            if re.search(r'[\u0d00-\u0d7f][a-zA-Z]', content) or re.search(r'[a-zA-Z][\u0d00-\u0d7f]', content):
                broken_samples.append(content)
            
            # Check for over-phonetic markers
            # Look for double consonants that are often stylized badly
            style_matches = re.findall(r'[a-zA-Z]{2,}', content)
            for m in style_matches:
                if 'rr' in m.lower() or 'ttt' in m.lower() or 'dd' in m.lower():
                    phonetic_patterns[m.lower()] += 1

    with open('research_results.txt', 'w', encoding='utf-8') as f_out:
        f_out.write("--- BROKEN SAMPLES ---\n")
        f_out.write("\n".join(broken_samples[:20]))
        f_out.write("\n\n--- PHONETIC PATTERNS (TOP 50) ---\n")
        for p, count in phonetic_patterns.most_common(50):
            f_out.write(f"{p}: {count}\n")

if __name__ == "__main__":
    analyze()
