import wikipediaapi
from ddgs import DDGS
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict

# ── Load embedding model once at startup ───────
# This model converts text → vectors for similarity comparison
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# ── Wikipedia setup ────────────────────────────
wiki = wikipediaapi.Wikipedia(
    language="en",
    user_agent="hallucination-detector/1.0"
)


def search_wikipedia(query: str) -> List[Dict]:
    """Search Wikipedia and return passages."""
    passages = []

    page = wiki.page(query)
    if page.exists():
        # split into sentences, take first 20
        sentences = page.summary.split(". ")[:20]
        for sentence in sentences:
            if len(sentence) > 30:   # skip very short sentences
                passages.append({
                    "source": "Wikipedia",
                    "text": sentence.strip()
                })

    return passages


def search_duckduckgo(query: str) -> List[Dict]:
    """Search DuckDuckGo and return passages."""
    passages = []

    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)
            for r in results:
                if r.get("body"):
                    passages.append({
                        "source": "DuckDuckGo",
                        "text": r["body"]
                    })
    except Exception as e:
        print(f"DuckDuckGo search failed: {e}")

    return passages


def rank_passages(claim: str, passages: List[Dict], top_k: int = 5) -> List[Dict]:
    """Rank passages by relevance to the claim using embeddings."""

    if not passages:
        return []

    # convert claim and all passages to vectors
    claim_embedding = embedder.encode(claim, convert_to_tensor=True)
    passage_texts = [p["text"] for p in passages]
    passage_embeddings = embedder.encode(passage_texts, convert_to_tensor=True)

    # compute cosine similarity between claim and each passage
    scores = util.cos_sim(claim_embedding, passage_embeddings)[0]

    # attach relevance score to each passage
    for i, passage in enumerate(passages):
        passage["relevance"] = round(float(scores[i]), 4)

    # sort by relevance, return top_k
    ranked = sorted(passages, key=lambda x: x["relevance"], reverse=True)
    return ranked[:top_k]


def retrieve_evidence(claim: str) -> List[Dict]:
    """Main function — search both sources and return ranked evidence."""

    # convert full claim to short search query
    # take first 5 words as keyword query
    short_query = " ".join(claim.split()[:5])

    print(f"🔍 Retrieving evidence for: {claim}")
    print(f"🔎 Search query: {short_query}")

    wiki_passages = search_wikipedia(short_query)
    ddg_passages  = search_duckduckgo(claim)

    all_passages = wiki_passages + ddg_passages
    print(f"📚 Found {len(all_passages)} total passages")

    ranked = rank_passages(claim, all_passages, top_k=5)
    print(f"✅ Returning top {len(ranked)} passages")

    return ranked