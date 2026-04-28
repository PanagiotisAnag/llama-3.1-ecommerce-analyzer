# Llama 3.1 E-Commerce Analyzer

A fine-tuned Llama 3.1 8B Instruct model for e-commerce product analysis and ad copy generation, paired with a Chrome extension that works on Amazon, AliExpress, eBay, and Walmart.

## What It Does

**Product Analysis** — paste or scrape a product listing and get:
- `WINNER / LOSER / RISKY` verdict
- Score out of 10
- Red flags from real customer reviews
- Market truth (what buyers actually experience)
- Invest / Avoid / Test with small budget recommendation

**Ad Copy Generation** — for WINNER products, automatically generates:
- 5 scroll-stopping hooks
- Headline
- Full primary text with emojis and CTA
- Ready for Meta Ads, TikTok, Google

## Model

Fine-tuned from `meta-llama/Meta-Llama-3.1-8B-Instruct` using QLoRA:
- 4-bit NF4 quantization (BitsAndBytes)
- LoRA rank 8, alpha 16
- Trained on 15,713 examples (product analysis + marketing copy)
- Training loss: 0.3579

HuggingFace: [PanosAnag/llama-3.1-ecommerce-analyzer](https://huggingface.co/PanosAnag/llama-3.1-ecommerce-analyzer)

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
3. Click the extension icon
4. Click **Analyze This Product**
5. Wait ~30 seconds for the verdict
6. If WINNER, ad copy is generated automatically

For Temu and Alibaba (block automated scraping), copy the product title, price, description, and a few reviews manually into the extension's text box.

## Files

| File | Purpose |
|------|---------|
| `api_server.py` | Flask API serving `/analyze` and `/adcopy` endpoints |
| `train.py` | QLoRA fine-tuning script |
| `combine_datasets.py` | Merges marketing + analysis datasets |
| `build_analysis_dataset.py` | Builds product analysis Q&A from Amazon reviews |
| `download_reviews.py` | Downloads Amazon reviews from HuggingFace |
| `scraper.py` | CLI scraper for product pages |
| `upload_model.py` | Uploads trained model to HuggingFace |
| `extension/` | Chrome extension (Manifest V3) |

## Dataset

- **Marketing dataset**: 10,713 ad copy Q&A examples
- **Analysis dataset**: 5,000 product analysis Q&A from Amazon reviews
- **Combined**: 15,713 shuffled entries → `combined_qa.jsonl`

## License

MIT
