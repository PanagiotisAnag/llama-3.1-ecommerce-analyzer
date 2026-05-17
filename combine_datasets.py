import json
import random

FILE1  = r"E:\Machine Learning\ecommerce_marketing_qa.jsonl"
FILE2  = r"E:\Machine Learning\product_analysis_qa.jsonl"
OUTPUT = r"E:\Machine Learning\combined_qa.jsonl"

# Balanced sample: 200K marketing + 200K analysis = 400K total
SAMPLE_MARKETING = 75000
SAMPLE_ANALYSIS  = 75000

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
print(f"Marketing dataset: {len(ds1):,} entries")
print(f"Analysis dataset:  {len(ds2):,} entries")

# Sample balanced subsets
sample1 = random.sample(ds1, min(SAMPLE_MARKETING, len(ds1)))
sample2 = random.sample(ds2, min(SAMPLE_ANALYSIS,  len(ds2)))

combined = sample1 + sample2
random.shuffle(combined)

with open(OUTPUT, "w", encoding="utf-8") as f:
    for entry in combined:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print(f"\nMarketing sampled: {len(sample1):,}")
print(f"Analysis sampled:  {len(sample2):,}")
print(f"Combined total:    {len(combined):,}")
print(f"Saved to: {OUTPUT}")
