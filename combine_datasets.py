import json
import random
import os

FILE1 = r"E:\Machine Learning\ecommerce_marketing_qa.jsonl"
FILE2 = r"E:\Machine Learning\product_analysis_qa.jsonl"
OUTPUT = r"E:\Machine Learning\combined_qa.jsonl"

def load_jsonl(path):
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records

print("Loading datasets...")
ds1 = load_jsonl(FILE1)
ds2 = load_jsonl(FILE2)
print(f"Marketing dataset: {len(ds1)} entries")
print(f"Analysis dataset:  {len(ds2)} entries")

combined = ds1 + ds2
random.shuffle(combined)

with open(OUTPUT, "w", encoding="utf-8") as f:
    for entry in combined:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print(f"\nCombined: {len(combined)} entries")
print(f"Saved to: {OUTPUT}")
