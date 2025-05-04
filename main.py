from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

class Item(BaseModel):
    id: str
    title: str
    description: str
    email: str

class MatchRequest(BaseModel):
    new_item: Item
    existing_items: List[Item]

@app.post("/match")
async def match_items(request: MatchRequest):
    new_item = request.new_item
    existing_items = request.existing_items

    # Collect all descriptions
    descriptions = [new_item.description] + [item.description for item in existing_items]

    # Compute TF-IDF vectors
    vectorizer = TfidfVectorizer().fit_transform(descriptions)
    vectors = vectorizer.toarray()

    # Compute cosine similarity between new_item and existing items
    similarities = cosine_similarity([vectors[0]], vectors[1:])[0]

    # Find the best match above a threshold (e.g., 0.5)
    threshold = 0.5
    best_match_index = similarities.argmax()
    best_score = similarities[best_match_index]

    if best_score >= threshold:
        matched_item = existing_items[best_match_index]
        return {
            "match_found": True,
            "matched_item": {
                "id": matched_item.id,
                "title": matched_item.title,
                "description": matched_item.description,
                "email": matched_item.email,
                "similarity_score": float(best_score)
            }
        }

    return {"match_found": False}
