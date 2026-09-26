<div align="center">

# 🧠 Lost & Found: ML Matching Service

**A lightweight FastAPI microservice that finds the most likely match for a lost or found item, using TF-IDF vectorization and cosine similarity.**

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)
![Render](https://img.shields.io/badge/Deployed_on_Render-46E3B7?style=for-the-badge&logo=render&logoColor=black)

[**Web app repo →**](https://github.com/Rakesh-Bhagat/Lost-Found)

</div>

---

## Overview

This service is the matching engine behind **[Lost & Found](https://github.com/Rakesh-Bhagat/Lost-Found)**, a full-stack platform (Next.js, Prisma, PostgreSQL) that reunites people with their lost belongings.

When someone posts a lost or found item, the web app sends the new post and the active posts of the opposite type to this service. The service returns the best match, if one is similar enough. The web app then emails both parties.

It is a standalone Python service, so the ML logic can change, scale and deploy without touching the web app.

## How it works

```
 Web app (Next.js)                         This service (FastAPI)
┌──────────────────┐   POST /match   ┌────────────────────────────────────┐
│ New item posted  │ ──────────────▶ │ 1. Collect descriptions            │
│ + opposite-type  │                 │ 2. Fit TF-IDF over all texts       │
│ existing items   │                 │ 3. Cosine similarity: new vs each  │
└──────────────────┘                 │ 4. Take best score, apply threshold│
         ▲                           └───────────────┬────────────────────┘
         │      { match_found, matched_item, score } │
         └───────────────────────────────────────────┘
                   ↓
        Nodemailer emails both users
```

1. **Vectorize.** The new item's description and every candidate description are converted to TF-IDF vectors. TF-IDF weights distinctive words ("Casio", "cracked", "blue") above common ones ("the", "lost"), so specific details drive the match.
2. **Compare.** Cosine similarity between the new item's vector and each candidate's vector measures how close the texts are. It is length-independent, so a short post can still match a long one.
3. **Decide.** The highest-scoring candidate is returned only if its score is at least **0.5**. Below that, the service reports no match, which favors precision over noisy false positives.

## API

### `POST /match`

**Request**

```json
{
  "new_item": {
    "id": "a1",
    "title": "Lost black wallet",
    "description": "Black leather wallet with a red stripe, lost near the library",
    "email": "owner@example.com"
  },
  "existing_items": [
    {
      "id": "b7",
      "title": "Found wallet",
      "description": "Found a black leather wallet with red stripe outside the library",
      "email": "finder@example.com"
    }
  ]
}
```

**Response, match found** (the score shown is illustrative)

```json
{
  "match_found": true,
  "matched_item": {
    "id": "b7",
    "title": "Found wallet",
    "description": "Found a black leather wallet with red stripe outside the library",
    "email": "finder@example.com",
    "similarity_score": 0.78
  }
}
```

**Response, no match**

```json
{ "match_found": false }
```

FastAPI also serves interactive docs at `/docs` (Swagger UI) with no extra setup.

## Tech stack

| Layer | Choice |
| --- | --- |
| API framework | FastAPI, with Pydantic request validation |
| ML | scikit-learn `TfidfVectorizer` and `cosine_similarity` |
| Server | Uvicorn (ASGI) |
| Deployment | Render, defined as code in `render.yaml` |

## Run locally

```bash
git clone https://github.com/Rakesh-Bhagat/L-F-ML-model.git
cd L-F-ML-model

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

uvicorn main:app --reload --port 8000
```

Then open <http://localhost:8000/docs> to try the endpoint, or:

```bash
curl -X POST http://localhost:8000/match \
  -H "Content-Type: application/json" \
  -d '{
    "new_item": {"id":"1","title":"Lost keys","description":"silver house keys with a blue keychain","email":"a@x.com"},
    "existing_items": [{"id":"2","title":"Found keys","description":"found silver keys with blue keychain","email":"b@x.com"}]
  }'
```

## Deployment

The repo ships with a Render blueprint (`render.yaml`). Connect the repository on [Render](https://render.com) and it installs the dependencies and starts Uvicorn automatically.

## Design decisions

| Decision | Why |
| --- | --- |
| **Separate microservice** | Keeps the Python/ML stack independent of the Node web app, so each can be deployed and scaled on its own. |
| **TF-IDF + cosine similarity** | Fast, deterministic and explainable. It needs no GPU, no model download and no training data, and it responds in milliseconds on a free-tier host. |
| **Stateless service** | The web app sends the candidates with each request, so the service holds no database and any instance can serve any request. |
| **Similarity threshold (0.5)** | An email that says "we found your item" must be right. A stricter cutoff trades a few missed matches for far fewer wrong ones. |
| **Typed request models** | Pydantic rejects malformed payloads before they reach the ML code. |

## Roadmap

- [ ] Return the top-N ranked matches with scores instead of a single best match
- [ ] Match on `title` and `description` together, not `description` alone
- [ ] Semantic matching with sentence embeddings, so "backpack" also matches "rucksack"
- [ ] Configurable threshold through an environment variable
- [ ] Unit tests and CI for the matching logic
- [ ] Image similarity matching for uploaded photos

## Related

- **[Lost & Found web app](https://github.com/Rakesh-Bhagat/Lost-Found)**: the Next.js frontend and backend that calls this service.

---

<div align="center">

Built by [Rakesh Bhagat](https://github.com/Rakesh-Bhagat)

</div>
