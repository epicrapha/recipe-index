# Recipe Recommender

A recipe recommendation system that takes a list of ingredients and returns the most similar recipes from the RecipeNLG dataset (2.2M recipes).

## How It Works

1. Input ingredients are preprocessed (lowercased, bigram phrases detected, lemmatized)
2. Each ingredient is looked up in a trained Word2Vec model to get its vector
3. Vectors are averaged into a single embedding representing the query
4. PCA reduces the embedding to 50 dimensions
5. A K-Means cluster is predicted to narrow the search space
6. Cosine similarity is computed against all recipes in that cluster
7. The top N most similar recipes are returned as JSON

## Project Structure

```
recipe-model/
├── recipe_model/                # Trained model artifacts
│   ├── recipe_engine.kv         # Word2Vec model (KeyedVectors)
│   ├── recipe_clusterer.joblib  # K-Means clustering model
│   ├── recipe_pca.joblib        # PCA dimensionality reduction model
│   ├── bigram_model.pkl         # Bigram phrase model (Gensim Phraser)
│   ├── recipe_search_index.npy  # Pre-computed recipe embeddings
│   ├── recipes_ui.csv           # Recipe dataset (title, ingredients, directions, cluster)
│   └── recipe-model.ipynb       # Training notebook (run on Kaggle)
├── infer.py                     # Inference script
├── main.py                      # Entry point
└── pyproject.toml               # Project dependencies
```

## Setup

Requires [uv](https://github.com/astral-sh/uv).

```bash
uv sync
```

Also download the required spaCy model (one-time):

```bash
uv run python -m spacy download en_core_web_sm
```

## Usage

### Run the example queries

```bash
uv run infer.py
```

### Run via main.py

```bash
uv run main.py
```

This runs a query and saves the result to `result.json`.

### Use in your own script

```python
from infer import find_recipes

result = find_recipes("chicken garlic soy sauce vinegar", top_n=5)
print(result)
```

### Output format

```json
{
  "input": "chicken garlic soy sauce vinegar",
  "entities": ["chicken", "garlic", "soy", "sauce", "vinegar"],
  "predicted_cluster": 1,
  "cluster_label": "savory/main dishes",
  "similar_recipes": [
    {
      "title": "Chicken adobo",
      "similarity": 1.0,
      "ingredients": ["1 kg chicken", "1 head garlic", "100 ml soy sauce", "100 ml vinegar"],
      "ingredients_ner": ["chicken", "garlic", "soy sauce", "vinegar"],
      "directions": ["Saute garlic until golden brown", "Add the chicken", "..."]
    }
  ]
}
```

## Clusters

| Cluster | Label               | Description                        |
|---------|---------------------|------------------------------------|
| 0       | Desserts / Baking   | Sugar, butter, egg-heavy recipes   |
| 1       | Savory / Main Dishes| Meat, vegetable, and savory recipes|
