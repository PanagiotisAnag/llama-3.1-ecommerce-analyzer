import os
os.environ["HF_HOME"] = r"E:\huggingface_cache"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import json
import random
from huggingface_hub import hf_hub_download

OUTPUT_FILE = r"E:\Machine Learning\raw_reviews_v2.json"
CACHE_DIR   = r"E:\huggingface_cache\amazon_reviews"

CATEGORIES = [
    "All_Beauty",
    "Amazon_Fashion",
    "Appliances",
    "Arts_Crafts_and_Sewing",
    "Automotive",
    "Baby_Products",
    "Beauty_and_Personal_Care",
    "Cell_Phones_and_Accessories",
    "Clothing_Shoes_and_Jewelry",
    "Electronics",
    "Grocery_and_Gourmet_Food",
    "Handmade_Products",
    "Health_and_Household",
    "Health_and_Personal_Care",
    "Home_and_Kitchen",
    "Industrial_and_Scientific",
    "Musical_Instruments",
    "Office_Products",
    "Patio_Lawn_and_Garden",
    "Pet_Supplies",
    "Software",
    "Sports_and_Outdoors",
    "Tools_and_Home_Improvement",
    "Toys_and_Games",
    "Video_Games",
]

REVIEWS_PER_CATEGORY = 40000  # 40000 x 25 = 1,000,000 total

print(f"Categories: {len(CATEGORIES)}")
print(f"Target: {REVIEWS_PER_CATEGORY:,} per category = ~{len(CATEGORIES) * REVIEWS_PER_CATEGORY:,} total\n")

all_reviews = []
failed = []
global_seen = set()

for cat in CATEGORIES:
    filename = f"raw/review_categories/{cat}.jsonl"
    print(f"  {cat}...", end=" ", flush=True)

    try:
        local_path = hf_hub_download(
            repo_id="McAuley-Lab/Amazon-Reviews-2023",
            filename=filename,
            repo_type="dataset",
            local_dir=CACHE_DIR,
        )
    except Exception as e:
        print(f"DOWNLOAD FAILED: {e}")
        failed.append(cat)
        continue

    # Stream through jsonl and collect qualifying reviews
    pos = []
    neg = []
    seen = set()
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

                # Deduplicate by first 100 chars of text
                key = text[:100].strip().lower()
                if key in seen:
                    continue
                seen.add(key)

                entry = {
                    "review": text[:1200],
                    "rating": 1 if rating <= 2 else 5,
                    "category": cat,
                }

                if entry["rating"] == 1:
                    neg.append(entry)
                else:
                    pos.append(entry)

                # Stop early once we have enough
                if len(pos) >= REVIEWS_PER_CATEGORY * 2 and len(neg) >= REVIEWS_PER_CATEGORY * 2:
                    break

    except Exception as e:
        print(f"READ FAILED: {e}")
        failed.append(cat)
        continue

    # Balance pos/neg, up to REVIEWS_PER_CATEGORY total
    half = REVIEWS_PER_CATEGORY // 2
    sampled = random.sample(neg, min(half, len(neg))) + random.sample(pos, min(half, len(pos)))
    random.shuffle(sampled)

    # Global dedup across categories
    deduped = []
    for entry in sampled:
        key = entry["review"][:100].strip().lower()
        if key not in global_seen:
            global_seen.add(key)
            deduped.append(entry)

    all_reviews.extend(deduped)

    print(f"got {len(deduped):,} unique reviews (neg={min(half,len(neg))}, pos={min(half,len(pos))}) | total: {len(all_reviews):,}")

random.shuffle(all_reviews)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_reviews, f, ensure_ascii=False, indent=2)

print(f"\n{'='*55}")
print(f"Total reviews saved: {len(all_reviews):,}")
print(f"Saved to: {OUTPUT_FILE}")
if failed:
    print(f"Failed: {failed}")
