import os
os.environ["HF_HOME"] = r"E:\huggingface_cache"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import json
import random
from huggingface_hub import hf_hub_download

EXISTING_FILE = r"E:\Machine Learning\raw_reviews_v2.json"
OUTPUT_FILE   = r"E:\Machine Learning\raw_reviews_v2.json"  # append and overwrite
CACHE_DIR     = r"E:\huggingface_cache\amazon_reviews"

EXTRA_PER_CATEGORY = 20000  # 20000 x 25 = 500,000 new → total ~1,000,000

CATEGORIES = [
    "All_Beauty", "Amazon_Fashion", "Appliances", "Arts_Crafts_and_Sewing",
    "Automotive", "Baby_Products", "Beauty_and_Personal_Care",
    "Cell_Phones_and_Accessories", "Clothing_Shoes_and_Jewelry", "Electronics",
    "Grocery_and_Gourmet_Food", "Handmade_Products", "Health_and_Household",
    "Health_and_Personal_Care", "Home_and_Kitchen", "Industrial_and_Scientific",
    "Musical_Instruments", "Office_Products", "Patio_Lawn_and_Garden",
    "Pet_Supplies", "Software", "Sports_and_Outdoors", "Tools_and_Home_Improvement",
    "Toys_and_Games", "Video_Games",
]

# --- Load existing reviews and build dedup index ---
print("Loading existing reviews...")
with open(EXISTING_FILE, "r", encoding="utf-8") as f:
    existing = json.load(f)
print(f"Existing reviews: {len(existing):,}")

global_seen = set()
for r in existing:
    global_seen.add(r["review"][:100].strip().lower())
print(f"Dedup index built: {len(global_seen):,} fingerprints\n")

new_reviews = []

for cat in CATEGORIES:
    print(f"  {cat}...", end=" ", flush=True)

    filename = f"raw/review_categories/{cat}.jsonl"
    try:
        local_path = hf_hub_download(
            repo_id="McAuley-Lab/Amazon-Reviews-2023",
            filename=filename,
            repo_type="dataset",
            local_dir=CACHE_DIR,
        )
    except Exception as e:
        print(f"DOWNLOAD FAILED: {e}")
        continue

    pos = []
    neg = []
    seen_this_cat = set()

    try:
        with open(local_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                text = obj.get("text", "") or ""
                rating = obj.get("rating", 0)

                if len(text) < 40 or rating not in (1.0, 2.0, 4.0, 5.0):
                    continue

                key = text[:100].strip().lower()

                # Skip if already in existing dataset or already collected this run
                if key in global_seen or key in seen_this_cat:
                    continue

                seen_this_cat.add(key)

                entry = {
                    "review": text[:1200],
                    "rating": 1 if rating <= 2 else 5,
                    "category": cat,
                }

                if entry["rating"] == 1:
                    neg.append(entry)
                else:
                    pos.append(entry)

                if len(pos) >= EXTRA_PER_CATEGORY and len(neg) >= EXTRA_PER_CATEGORY:
                    break

    except Exception as e:
        print(f"READ FAILED: {e}")
        continue

    half = EXTRA_PER_CATEGORY // 2
    sampled = random.sample(neg, min(half, len(neg))) + random.sample(pos, min(half, len(pos)))
    random.shuffle(sampled)

    # Add to global seen so cross-category dedup works
    for entry in sampled:
        global_seen.add(entry["review"][:100].strip().lower())

    new_reviews.extend(sampled)
    print(f"got {len(sampled):,} new reviews | new total: {len(new_reviews):,}")

# Combine and shuffle
all_reviews = existing + new_reviews
random.shuffle(all_reviews)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_reviews, f, ensure_ascii=False, indent=2)

print(f"\n{'='*55}")
print(f"Previous: {len(existing):,}")
print(f"Added:    {len(new_reviews):,}")
print(f"Total:    {len(all_reviews):,}")
print(f"Saved to: {OUTPUT_FILE}")
