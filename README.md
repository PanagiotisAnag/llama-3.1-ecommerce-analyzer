# MarketLens — AI Product Intelligence

A fine-tuned Llama 3.1 8B Instruct model for e-commerce product intelligence: product analysis and ad copy generation. Includes a Chrome extension that works on Amazon, AliExpress, eBay, and Walmart.

## What It Does

**Product Analysis** — analyze any product listing and get:
- `WINNER / LOSER / RISKY` verdict
- Score out of 10
- Red flags from real customer reviews
- Market truth (what buyers actually experience vs what the listing promises)
- Invest / Avoid / Test with small budget recommendation

**Ad Copy Generation** — for WINNER products, automatically generates:
- 5 scroll-stopping hooks
- Headline
- Full primary text with emojis and CTA
- Ready for Meta Ads, TikTok, Google

## Model

Fine-tuned from `meta-llama/Meta-Llama-3.1-8B-Instruct` using QLoRA:
- 4-bit NF4 quantization (BitsAndBytes)
- LoRA rank 16, alpha 32
- Trained on **150,000 examples** (75K product analysis + 75K marketing copy)
- Dataset: [McAuley-Lab/Amazon-Reviews-2023](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023) — 25 categories, 135,235 real products with reviews

HuggingFace: [PanosAnag/llama-3.1-ecommerce-analyzer](https://huggingface.co/PanosAnag/llama-3.1-ecommerce-analyzer)

## Dataset

Built from **McAuley-Lab/Amazon-Reviews-2023** — one of the largest Amazon review datasets:

| Source | Entries | Description |
|--------|---------|-------------|
| Product Analysis Q&A | 75,000 | Real product listings + reviews → WINNER/LOSER/RISKY verdicts |
| Marketing Q&A | 75,000 | Real product titles/features → hooks, headlines, ad copy |
| **Combined** | **150,000** | Shuffled and balanced |

### Categories covered
Electronics, Home & Kitchen, Beauty & Personal Care, Sports & Outdoors, Clothing, Automotive, Pet Supplies, Toys & Games, Tools & Home Improvement, Health & Household, Office Products, Baby Products, Grocery, Musical Instruments, and more (25 total).

### What each training example contains
```
PRODUCT: [real product title]
CATEGORY: [category]
PRICE: [price]
AVERAGE RATING: [X/5] (N reviews)
DESCRIPTION: [real product description]
FEATURES: [real product features]
CUSTOMER REVIEWS:
[★☆☆☆☆] [real review text]
[★★★★★] [real review text]
...
→ VERDICT: WINNER/LOSER/RISKY + full analysis
```

## Setup

### Requirements
- Python 3.10+
- CUDA GPU with 8GB+ VRAM
- Chrome browser

### Install dependencies
```bash
pip install torch transformers peft bitsandbytes flask flask-cors accelerate
```

### Run the API server
```bash
python api_server.py
```
The server loads the model and starts at `http://localhost:5000`.

### Load the Chrome extension
1. Open Chrome → `chrome://extensions`
2. Enable **Developer mode**
3. Click **Load unpacked**
4. Select the `extension/` folder

## Usage

1. Start `api_server.py`
2. Navigate to any product page (Amazon, AliExpress, eBay, Walmart)
3. Click the **MarketLens** extension icon
4. Click **Analyze This Product**
5. Wait ~30 seconds for the verdict
6. If WINNER, ad copy is generated automatically with a copy button

For Temu and Alibaba (block automated scraping), paste the product title, price, description, and reviews manually.

## Files

| File | Purpose |
|------|---------|
| `api_server.py` | Flask API — `/analyze` and `/adcopy` endpoints |
| `train.py` | QLoRA fine-tuning script |
| `combine_datasets.py` | Merges and samples marketing + analysis datasets |
| `build_analysis_dataset.py` | Builds product analysis Q&A from real product+review data |
| `qa_generator.py` | Builds marketing Q&A from real product data |
| `download_amazon_reviews.py` | Downloads reviews from Amazon Reviews 2023 |
| `download_extra_reviews.py` | Downloads additional reviews (deduped) |
| `download_full_dataset.py` | Downloads product metadata and joins with reviews |
| `scraper.py` | CLI scraper for product pages |
| `upload_model.py` | Uploads trained model to HuggingFace |
| `extension/` | Chrome extension (Manifest V3) |

## License

MIT
