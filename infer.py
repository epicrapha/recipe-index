# =============================================================================
# Recipe Recommender — Inference Script
#
# Given a list of ingredients, this script finds the most similar recipes
# from the RecipeNLG dataset using Word2Vec embeddings and K-Means clustering.
#
# Usage:
#   uv run infer.py
#
# How it works:
#   1. Your ingredients are preprocessed (lowercased, bigram phrases, lemmatized)
#   2. Each ingredient word is looked up in a trained Word2Vec model to get its vector
#   3. The vectors are averaged into a single embedding representing your query
#   4. PCA reduces the embedding to 50 dimensions
#   5. A K-Means cluster is predicted to narrow down the search space
#   6. Cosine similarity is computed against all recipes in that cluster
#   7. The top N most similar recipes are returned as JSON
# =============================================================================

import json
import logging

import joblib
import numpy as np
import pandas as pd
import spacy
from gensim.models import KeyedVectors

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(message)s")
logger = logging.getLogger(__name__)
logging.getLogger("gensim").setLevel(logging.WARNING)


MODEL_DIR = "recipe_model"
TOP_N     = 5

CLUSTER_LABELS = {
    0: "desserts/baking",
    1: "savory/main dishes",
}

logger.info("Loading models...")
w2v    = KeyedVectors.load(f"{MODEL_DIR}/recipe_engine.kv", mmap="r")
kmeans = joblib.load(f"{MODEL_DIR}/recipe_clusterer.joblib")
pca    = joblib.load(f"{MODEL_DIR}/recipe_pca.joblib")

if not hasattr(kmeans, "_n_threads"):
    kmeans._n_threads = 1

bigram_model = None
try:
    bigram_model = joblib.load(f"{MODEL_DIR}/bigram_model.pkl")
    logger.info("Bigram model loaded.")
except FileNotFoundError:
    logger.info("No bigram model found, skipping bigram phrases.")

logger.info("Loading recipe data and embeddings...")
recipes_df = pd.read_csv("recipe_model_lite/recipes_ui_lite.csv")
embeddings = np.load("recipe_model_lite/recipe_search_index_lite.npy")

logger.info(f"Ready. {len(recipes_df):,} recipes loaded.")


import en_core_web_sm
nlp = en_core_web_sm.load(disable=["parser"])

_pca_cache = None
_cluster_cache = None


def _get_all_clusters():
    global _pca_cache, _cluster_cache
    if _pca_cache is None:
        _pca_cache = pca.transform(embeddings)
        _cluster_cache = kmeans.predict(_pca_cache)
    return _cluster_cache, _pca_cache


def preprocess(text):
    """
    Clean and tokenize input text to match the training pipeline.

    Steps:
      - Lowercase
      - Split into tokens
      - Apply bigram phrases (if model exists)
      - Lemmatize each token via spaCy
    """
    tokens = text.lower().replace(",", " ").split()

    if bigram_model:
        tokens = bigram_model[tokens]

    lemmatized = []
    for token in tokens:
        if not token:
            continue
        if "_" in token:
            parts = [p for p in token.split("_") if p]
            lemmatized_parts = []
            for part in parts:
                doc = nlp(part)
                if len(doc) > 0:
                    lemmatized_parts.append(doc[0].lemma_)
            if lemmatized_parts:
                lemmatized.append("_".join(lemmatized_parts))
        else:
            doc = nlp(token)
            if len(doc) > 0:
                lemmatized.append(doc[0].lemma_)

    return lemmatized


def get_embedding(text):
    """
    Convert text into a single vector by averaging its Word2Vec word vectors.

    Returns:
        (embedding, known_tokens)
        - embedding    : numpy array of shape (100,)
        - known_tokens : list of tokens that were found in the Word2Vec vocabulary
    """
    tokens     = preprocess(text)
    known      = [t for t in tokens if t in w2v]
    valid_vecs = [w2v[t] for t in known]

    if not valid_vecs:
        raise ValueError(
            f"None of the words in '{text}' were found in the vocabulary. "
            "Try using more common ingredient names."
        )

    return np.mean(valid_vecs, axis=0), known


def find_recipes(query_ingredients, top_n=TOP_N):
    """
    Find the most similar recipes given a string of ingredients.

    Args:
        query_ingredients (str) : ingredients to search with,
                                  e.g. "chicken garlic soy sauce vinegar"
        top_n             (int) : number of recipes to return (default: 5)

    Returns:
        dict with keys:
            input             - original query
            entities          - recognized ingredient words from the query
            predicted_cluster - cluster index assigned to the query
            cluster_label     - human-readable cluster name
            similar_recipes   - list of top N matching recipes (with similarity scores)
    """
    query_vec, entities = get_embedding(query_ingredients)
    query_vec_2d        = query_vec.reshape(1, -1)

    query_pca = pca.transform(query_vec_2d)
    cluster   = int(kmeans.predict(query_pca)[0])

    all_clusters, _ = _get_all_clusters()
    cluster_mask    = all_clusters == cluster
    cluster_indices = np.where(cluster_mask)[0]
    cluster_embeds  = embeddings[cluster_indices]

    query_norm   = query_vec_2d / (np.linalg.norm(query_vec_2d) + 1e-9)
    cluster_norm = cluster_embeds / (np.linalg.norm(cluster_embeds, axis=1, keepdims=True) + 1e-9)
    scores       = (cluster_norm @ query_norm.T)[:, 0]

    top_local  = np.argsort(scores)[::-1][:top_n]
    top_global = cluster_indices[top_local]

    similar_recipes = []
    for rank, idx in enumerate(top_global):
        row = recipes_df.iloc[idx]
        similar_recipes.append({
            "title":           row["title"],
            "similarity":      round(float(scores[top_local[rank]]), 4),
            "ingredients":     _parse_list(row["ingredients"]),
            "ingredients_ner": _parse_list(row["NER"]),
            "directions":      _parse_list(row["directions"]),
        })

    return {
        "input":             query_ingredients,
        "entities":          entities,
        "predicted_cluster": cluster,
        "cluster_label":     CLUSTER_LABELS.get(cluster, f"cluster {cluster}"),
        "similar_recipes":   similar_recipes,
    }


def _parse_list(value):
    """Parse a JSON array string from the CSV into a Python list."""
    try:
        return json.loads(value)
    except Exception:
        return [value]


if __name__ == "__main__":
    queries = [
        "chocolate butter sugar eggs flour",
        "salmon lemon dill cream",
        "chicken garlic soy sauce vinegar",
    ]

    for query in queries:
        result = find_recipes(query, top_n=3)
        print(json.dumps(result, indent=2))
        print()
