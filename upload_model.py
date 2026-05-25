import os
from huggingface_hub import HfApi, login

MODEL_DIR = r"E:\Machine Learning\marketlens_model\checkpoint-17000"
REPO_ID = "PanosAnag/llama-3.1-ecommerce-analyzer"

print("Logging in to HuggingFace...")
login()

api = HfApi()

print(f"Creating repo: {REPO_ID}")
api.create_repo(repo_id=REPO_ID, exist_ok=True, private=False)

print(f"Uploading model from: {MODEL_DIR}")
print("This may take a while depending on file sizes...")

api.upload_folder(
    folder_path=MODEL_DIR,
    repo_id=REPO_ID,
    repo_type="model",
    ignore_patterns=["*.tmp", "__pycache__", "*.pyc", "optimizer.pt", "rng_state.pth", "scaler.pt", "scheduler.pt", "trainer_state.json", "training_args.bin"],
)

# Upload our custom README on top
from pathlib import Path
api.upload_file(
    path_or_fileobj=str(Path(r"E:\Machine Learning\marketlens_model\README.md")),
    path_in_repo="README.md",
    repo_id=REPO_ID,
    repo_type="model",
)

print(f"\nDone! Model uploaded to:")
print(f"https://huggingface.co/{REPO_ID}")
