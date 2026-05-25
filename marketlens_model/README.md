---
library_name: peft
base_model: meta-llama/Meta-Llama-3.1-8B-Instruct
tags:
- lora
- sft
- transformers
- trl
- e-commerce
- text-generation
pipeline_tag: text-generation
license: mit
---

# MarketLens — AI Product Intelligence

Fine-tuned from `meta-llama/Meta-Llama-3.1-8B-Instruct` using QLoRA for two e-commerce tasks:

1. **Product Analysis** — WINNER / LOSER / RISKY verdicts with red flags, market truth, and investment recommendation
2. **Ad Copy Generation** — hooks, headlines, primary text, and CTA for Meta Ads, TikTok, Google

## Training

- Base model: `meta-llama/Meta-Llama-3.1-8B-Instruct`
- Method: QLoRA (4-bit NF4, LoRA rank 16, alpha 32)
- Precision: bf16
- Dataset: 150,000 examples (75K product analysis + 75K marketing copy)
- Source: [McAuley-Lab/Amazon-Reviews-2023](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023) — 25 categories, 135,235 real products with reviews
- Training loss: ~0.78 | Token accuracy: ~0.84

## What each training example contains

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
→ VERDICT: WINNER/LOSER/RISKY + full analysis
```

## Usage

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
import torch

BASE_MODEL = "meta-llama/Meta-Llama-3.1-8B-Instruct"
LORA_MODEL = "PanosAnag/llama-3.1-ecommerce-analyzer"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
)

tokenizer = AutoTokenizer.from_pretrained(LORA_MODEL)
model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, quantization_config=bnb_config, device_map="auto")
model = PeftModel.from_pretrained(model, LORA_MODEL)
model.eval()
```

## GitHub

[https://github.com/PanagiotisAnag/llama-3.1-ecommerce-analyzer](https://github.com/PanagiotisAnag/llama-3.1-ecommerce-analyzer)

## Framework Versions

- PEFT 0.19.1
- TRL 0.24.0
- Transformers 5.5.0
- PyTorch 2.6.0+cu124
