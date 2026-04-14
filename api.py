from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Import our existing inference logic
from infer import find_recipes

app = FastAPI(title="Recipe Engine API", description="Avant-Garde Clustering Inference API")

# Allow requests from the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecipeQuery(BaseModel):
    ingredients: str
    top_n: int = 10

class RecipeItem(BaseModel):
    title: str
    similarity: float
    ingredients: List[str]
    ingredients_ner: List[str]
    directions: List[str]

class RecipeResponse(BaseModel):
    input: str
    entities: List[str]
    predicted_cluster: int
    cluster_label: str
    similar_recipes: List[RecipeItem]

@app.get("/")
def health_check():
    return {"status": "operational", "engine": "running"}

@app.post("/recommend", response_model=RecipeResponse)
def get_recommendations(query: RecipeQuery):
    try:
        # Wrap the existing find_recipes logic
        result = find_recipes(query.ingredients, top_n=query.top_n)
        return result
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Intelligence Error: {str(e)}")
