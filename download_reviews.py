import os
os.environ["HF_HOME"] = r"E:\huggingface_cache"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import json
import random
from datasets import load_dataset

OUTPUT_DIR = r"E:\Machine Learning"
TARGET_PER_LABEL = 2500  # 2500 negative + 2500 positive = 5000 total

print("Downloading Amazon reviews (fancyzhx/amazon_polarity)...")
print("This dataset has real Amazon reviews with negative/positive labels.")
print("Streaming — will stop once we have enough.\n")

ds = load_dataset("fancyzhx/amazon_polarity", split="train", streaming=True)

negative = []  # label=0
positive = []  # label=1

for item in ds:
    label = item.get("label", -1)
    title = (item.get("title") or "").strip()
    content = (item.get("content") or "").strip()

    if not content or len(content) < 30:
        continue

    full_review = f"{title}. {content}" if title else content

    entry = {
        "rating": 1 if label == 0 else 5,
        "review": full_review[:400],
    }

    if label == 0 and len(negative) < TARGET_PER_LABEL:
        negative.append(entry)
    elif label == 1 and len(positive) < TARGET_PER_LABEL:
        positive.append(entry)

    if len(negative) % 500 == 0 and len(negative) > 0 and len(negative) <= TARGET_PER_LABEL:
        print(f"  Negative: {len(negative)} | Positive: {len(positive)}")

    if len(negative) >= TARGET_PER_LABEL and len(positive) >= TARGET_PER_LABEL:
        break

all_reviews = negative + positive
random.shuffle(all_reviews)

output_path = os.path.join(OUTPUT_DIR, "raw_reviews.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_reviews, f, ensure_ascii=False, indent=2)

print(f"\nDone!")
print(f"Negative reviews: {len(negative)}")
print(f"Positive reviews: {len(positive)}")
print(f"Total: {len(all_reviews)}")
print(f"Saved to: {output_path}")
