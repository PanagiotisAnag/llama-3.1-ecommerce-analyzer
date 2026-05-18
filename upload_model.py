import os
from huggingface_hub import HfApi, login

MODEL_DIR = r"E:\Machine Learning\combined_model"
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
    ignore_patterns=["*.tmp", "__pycache__", "*.pyc"],
)

print(f"\nDone! Model uploaded to:")
print(f"https://huggingface.co/{REPO_ID}")
