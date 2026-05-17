import os
os.environ["HF_HOME"] = r"E:\huggingface_cache"
os.environ["TRANSFORMERS_CACHE"] = r"E:\huggingface_cache"

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
from flask import Flask, request, jsonify
from flask_cors import CORS

BASE_MODEL = r"E:\Machine Learning\hf_cache\hub\models--meta-llama--Meta-Llama-3.1-8B-Instruct\snapshots\0e9e39f249a16976918f6564b8830bc894c89659"
LORA_MODEL = r"E:\Machine Learning\marketlens_model"

ANALYZE_PROMPT = """You are a cynical e-commerce product auditor. Your job is to analyze product specs and customer reviews to determine if a product is worth investing in for dropshipping or white label.

Rules:
- Ignore 5-star reviews that sound like marketing copy
- Focus on 1-star and 3-star reviews — they reveal real problems
- Look for patterns: quality issues, shipping problems, misleading descriptions, high return rates
- Be brutally honest. No sugarcoating.
- Always output your verdict in this exact format:

VERDICT: [WINNER / LOSER / RISKY]

SCORE: [X/10]

RED FLAGS:
- [list real problems found in reviews]

MARKET TRUTH:
[What customers actually experience vs what the listing promises]

RECOMMENDATION:
[Invest / Avoid / Test with small budget — and why]"""

ADCOPY_PROMPT = """You are an expert e-commerce marketing AI specializing in creating high-converting ad copy for Meta Ads, TikTok, Google, and all major social media platforms.

Given a product, generate complete ad copy in this exact format:

HOOKS:
1. "[hook 1]"
2. "[hook 2]"
3. "[hook 3]"
4. "[hook 4]"
5. "[hook 5]"

HEADLINE:
"[best headline]"

PRIMARY TEXT:
[full primary text with emojis, benefits, CTA]

CTA: [call to action]"""

app = Flask(__name__)
CORS(app)

model = None
tokenizer = None


def load_model():
    global model, tokenizer
    print("Loading model...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(LORA_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        low_cpu_mem_usage=True,
    )
    model = PeftModel.from_pretrained(model, LORA_MODEL)
    model.eval()
    print("Model ready. Server running on http://localhost:5000")


def generate(system_prompt, user_message, max_tokens=600, temperature=0.2):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").input_ids.to("cuda")
    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
            do_sample=True,
            repetition_penalty=1.1,
        )
    return tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model_loaded": model is not None})


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    if not data or "product_data" not in data:
        return jsonify({"error": "Missing product_data field"}), 400

    product_data = data["product_data"].strip()
    if not product_data:
        return jsonify({"error": "product_data is empty"}), 400

    result = generate(ANALYZE_PROMPT, product_data, max_tokens=600, temperature=0.2)

    verdict = "UNKNOWN"
    score = ""
    if "VERDICT: WINNER" in result:
        verdict = "WINNER"
    elif "VERDICT: LOSER" in result:
        verdict = "LOSER"
    elif "VERDICT: RISKY" in result:
        verdict = "RISKY"

    for line in result.split("\n"):
        if line.startswith("SCORE:"):
            score = line.replace("SCORE:", "").strip()
            break

    return jsonify({
        "verdict": verdict,
        "score": score,
        "full_analysis": result,
    })


@app.route("/adcopy", methods=["POST"])
def adcopy():
    data = request.json
    if not data or "product_data" not in data:
        return jsonify({"error": "Missing product_data field"}), 400

    product_data = data["product_data"].strip()
    if not product_data:
        return jsonify({"error": "product_data is empty"}), 400

    result = generate(ADCOPY_PROMPT, f"Write complete ad copy for this product:\n\n{product_data}", max_tokens=700, temperature=0.7)

    return jsonify({
        "ad_copy": result,
    })


if __name__ == "__main__":
    load_model()
    app.run(host="127.0.0.1", port=5000, debug=False)
