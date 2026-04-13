import pandas as pd
import numpy as np
import os

MODEL_DIR = "recipe_model"
SAMPLED_DIR = "recipe_model_lite"

print("Loading original massive data...")
recipes_df = pd.read_csv(f"{MODEL_DIR}/recipes_ui.csv")
embeddings = np.load(f"{MODEL_DIR}/recipe_search_index.npy")

# We slice the first 50,000 to keep it easily under 100MB and Streamlit's 1GB RAM limit
LIMIT = 50000

print(f"Truncating to {LIMIT} records...")
lite_df = recipes_df.iloc[:LIMIT]
lite_embeddings = embeddings[:LIMIT]

os.makedirs(SAMPLED_DIR, exist_ok=True)
lite_df.to_csv(f"{SAMPLED_DIR}/recipes_ui_lite.csv", index=False)
np.save(f"{SAMPLED_DIR}/recipe_search_index_lite.npy", lite_embeddings)

print(f"Success! New CSV size: {os.path.getsize(f'{SAMPLED_DIR}/recipes_ui_lite.csv') / (1024*1024):.2f} MB")
print(f"Success! New NPY size: {os.path.getsize(f'{SAMPLED_DIR}/recipe_search_index_lite.npy') / (1024*1024):.2f} MB")
print("You can now update infer.py to use these _lite files, which will safely push to GitHub and run on Streamlit Free Tier without OOM crashing!")
