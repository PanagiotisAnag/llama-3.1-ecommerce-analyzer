import os
os.environ["HF_HOME"] = r"E:\huggingface_cache"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import json
import random
from collections import defaultdict
from huggingface_hub import hf_hub_download

REVIEWS_FILE = r"E:\Machine Learning\raw_reviews_v2.json"
OUTPUT_FILE  = r"E:\Machine Learning\raw_products_with_reviews.json"
CACHE_DIR    = r"E:\huggingface_cache\amazon_reviews"

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

# --- Step 1: Load existing reviews and group by asin ---
print("Loading existing reviews from raw_reviews_v2.json...")
with open(REVIEWS_FILE, "r", encoding="utf-8") as f:
    raw_reviews = json.load(f)
print(f"Loaded {len(raw_reviews):,} reviews")

# The existing reviews don't have asin — we need to re-read from jsonl for the join
# So we build a set of known review texts to avoid duplicates later
known_review_texts = set()
for r in raw_reviews:
    known_review_texts.add(r["review"][:80].strip().lower())

print(f"Built dedup index: {len(known_review_texts):,} unique review fingerprints\n")

# --- Step 2: For each category, load meta + match reviews from jsonl ---
all_products = []
global_seen_asins = set()

for cat in CATEGORIES:
    print(f"[{cat}]")

    # Load product metadata
    print(f"  Metadata...", end=" ", flush=True)
    meta_by_asin = {}
    try:
        meta_path = hf_hub_download(
            repo_id="McAuley-Lab/Amazon-Reviews-2023",
            filename=f"raw/meta_categories/meta_{cat}.jsonl",
            repo_type="dataset",
            local_dir=CACHE_DIR,
        )
        with open(meta_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                asin = obj.get("parent_asin", "")
                title = obj.get("title", "") or ""
                if not asin or len(title) < 5:
                    continue
                meta_by_asin[asin] = {
                    "title": title,
                    "description": " ".join(obj.get("description", []) or [])[:500],
                    "features": " | ".join(obj.get("features", []) or [])[:500],
                    "price": obj.get("price"),
                    "average_rating": obj.get("average_rating"),
                    "rating_number": obj.get("rating_number", 0),
                    "store": obj.get("store", "") or "",
                    "category": cat,
                    "details": str(obj.get("details", "") or "")[:300],
                }
        print(f"{len(meta_by_asin):,} products", end=" | ", flush=True)
    except Exception as e:
        print(f"FAILED: {e}")
        continue

    # Match reviews from the already-downloaded jsonl using only reviews
    # that exist in our raw_reviews_v2.json (i.e. within our 499K set)
    print(f"Matching reviews...", end=" ", flush=True)
    reviews_by_asin = defaultdict(list)
    try:
        review_path = hf_hub_download(
            repo_id="McAuley-Lab/Amazon-Reviews-2023",
            filename=f"raw/review_categories/{cat}.jsonl",
            repo_type="dataset",
            local_dir=CACHE_DIR,
        )
        with open(review_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                asin = obj.get("parent_asin", "")
                text = obj.get("text", "") or ""
                rating = obj.get("rating", 0)
                if not asin or len(text) < 30 or rating not in (1.0, 2.0, 4.0, 5.0):
                    continue
                # Only use reviews that are already in our downloaded set
                key = text[:80].strip().lower()
                if key not in known_review_texts:
                    continue
                reviews_by_asin[asin].append({
                    "text": text[:600],
                    "rating": int(rating),
                })
        print(f"{sum(len(v) for v in reviews_by_asin.values()):,} matched reviews")
    except Exception as e:
        print(f"FAILED: {e}")
        continue

    # Join: keep products that have at least 2 matched reviews
    joined = []
    for asin, meta in meta_by_asin.items():
        if asin in global_seen_asins:
            continue
        revs = reviews_by_asin.get(asin, [])
        if len(revs) < 2:
            continue
        pos = [r for r in revs if r["rating"] >= 4]
        neg = [r for r in revs if r["rating"] <= 2]
        selected = (
            random.sample(neg, min(2, len(neg))) +
            random.sample(pos, min(3, len(pos)))
        )
        random.shuffle(selected)
        meta["reviews"] = selected[:5]
        joined.append((asin, meta))

    random.shuffle(joined)
    for asin, product in joined:
        global_seen_asins.add(asin)
        all_products.append(product)

    print(f"  -> {len(joined):,} products joined | running total: {len(all_products):,}")

random.shuffle(all_products)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_products, f, ensure_ascii=False, indent=2)

print(f"\n{'='*55}")
print(f"Total products with reviews: {len(all_products):,}")
print(f"Saved to: {OUTPUT_FILE}")
