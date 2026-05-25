import os
os.environ["HF_HOME"] = r"E:\huggingface_cache"
os.environ["TRANSFORMERS_CACHE"] = r"E:\huggingface_cache"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

import json
import torch
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
from trl import SFTTrainer, SFTConfig

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

MODEL_NAME    = r"E:\Machine Learning\hf_cache\hub\models--meta-llama--Meta-Llama-3.1-8B-Instruct\snapshots\0e9e39f249a16976918f6564b8830bc894c89659"
DATA_FILE     = "combined_qa.jsonl"
OUTPUT_DIR    = "marketlens_model"

MAX_SEQ_LEN   = 512
LORA_RANK     = 16
BATCH_SIZE    = 1
GRAD_ACCUM    = 8      # effective batch = 8
EPOCHS        = 1
LEARNING_RATE = 2e-4

# ---------------------------------------------------------------------------
# STEP 1: CHECK GPU
# ---------------------------------------------------------------------------

print("=" * 60)
print("STEP 1: Checking GPU...")
print("=" * 60)
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

# ---------------------------------------------------------------------------
# STEP 2: LOAD MODEL IN 4-BIT
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("STEP 2: Loading model in 4-bit...")
print("=" * 60)

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto",
    low_cpu_mem_usage=True,
)

model = prepare_model_for_kbit_training(model)
model.gradient_checkpointing_enable()

lora_config = LoraConfig(
    r=LORA_RANK,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# ---------------------------------------------------------------------------
# STEP 3: LOAD DATASET
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("STEP 3: Loading dataset...")
print("=" * 60)

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

raw_data = load_jsonl(DATA_FILE)
print(f"Loaded {len(raw_data)} Q&A entries")

def format_entry(entry):
    messages = entry["messages"]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False,
    )
    return {"text": text}

formatted  = [format_entry(r) for r in raw_data]
dataset    = Dataset.from_list(formatted)
split      = dataset.train_test_split(test_size=1000, seed=42)
train_data = split["train"]
eval_data  = split["test"]

print(f"Train: {len(train_data)} | Eval: {len(eval_data)}")

# ---------------------------------------------------------------------------
# STEP 4: TRAIN
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("STEP 4: Starting training...")
print("=" * 60)

trainer = SFTTrainer(
    model=model,
    processing_class=tokenizer,
    train_dataset=train_data,
    eval_dataset=eval_data,
    args=SFTConfig(
        output_dir=OUTPUT_DIR,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM,
        warmup_steps=50,
        learning_rate=LEARNING_RATE,
        fp16=False,
        bf16=True,
        logging_steps=25,
        eval_strategy="steps",
        eval_steps=500,
        save_strategy="steps",
        save_steps=500,
        save_total_limit=2,
        load_best_model_at_end=True,
        report_to="none",
        dataset_text_field="text",
        max_length=MAX_SEQ_LEN,
        packing=True,
        seed=42,
        dataloader_pin_memory=False,
    ),
)

trainer_stats = trainer.train()
print(f"\nTraining loss: {trainer_stats.training_loss:.4f}")

# ---------------------------------------------------------------------------
# STEP 5: SAVE
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("STEP 5: Saving model...")
print("=" * 60)

model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"Saved to: {OUTPUT_DIR}/")

# ---------------------------------------------------------------------------
# STEP 6: QUICK TEST
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("STEP 6: Quick test...")
print("=" * 60)

model.eval()
test_messages = [
    {"role": "system", "content": "You are an expert e-commerce marketing AI."},
    {"role": "user",   "content": "Write 5 hooks for a portable blender."},
]

input_text = tokenizer.apply_chat_template(
    test_messages,
    tokenize=False,
    add_generation_prompt=True,
)
inputs = tokenizer(input_text, return_tensors="pt").input_ids.to("cuda")

with torch.no_grad():
    outputs = model.generate(
        input_ids=inputs,
        max_new_tokens=512,
        temperature=0.7,
        top_p=0.9,
        do_sample=True,
    )

response = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
print("\nTest response:")
print("-" * 40)
print(response)
print("-" * 40)
print("\nDONE! Model saved at:", OUTPUT_DIR)
