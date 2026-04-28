from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import List, Dict

# ── Load model directly ────────────────────────
print("⏳ Loading NLI model...")
MODEL_NAME = "cross-encoder/nli-deberta-v3-small"
tokenizer  = AutoTokenizer.from_pretrained(MODEL_NAME)
model      = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.eval()
print("✅ NLI model loaded")

# label order for this specific model
# 0 = contradiction, 1 = entailment, 2 = neutral
LABELS = {0: "CONTRADICTS", 1: "SUPPORTS", 2: "NEUTRAL"}


def score_passage(claim: str, passage: str) -> Dict:
    """
    Score a single passage against the claim.
    
    NLI convention:
    - premise   = the evidence (what we know is true)
    - hypothesis = the claim (what we're checking)
    """

    inputs = tokenizer(
        passage,        # premise — the evidence
        claim,          # hypothesis — the claim to verify
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    with torch.no_grad():
        outputs = model(**inputs)

    probs = torch.softmax(outputs.logits, dim=-1)[0].tolist()

    contradiction = probs[0]
    entailment    = probs[1]
    neutral       = probs[2]

    scores = {
        "CONTRADICTS": contradiction,
        "SUPPORTS":    entailment,
        "NEUTRAL":     neutral
    }

    verdict = max(scores, key=scores.get)

    return {
        "verdict":       verdict,
        "contradiction": round(contradiction, 4),
        "neutral":       round(neutral,       4),
        "entailment":    round(entailment,    4),
        "confidence":    round(max(probs),    4)
    }


def score_all_passages(claim: str, passages: List[Dict]) -> List[Dict]:
    """Score every passage and attach verdict to each."""

    scored = []
    for passage in passages:
        print(f"🔬 Scoring: {passage['text'][:60]}...")
        result = score_passage(claim, passage["text"])

        scored.append({
            **passage,
            "verdict":    result["verdict"],
            "confidence": result["confidence"],
            "scores": {
                "contradiction": result["contradiction"],
                "neutral":       result["neutral"],
                "entailment":    result["entailment"]
            }
        })

    return scored


def compute_hallucination_score(scored_passages: List[Dict]) -> Dict:
    """Aggregate all passage verdicts into one final score."""

    if not scored_passages:
        return {
            "score":      0.5,
            "confidence": "low",
            "label":      "uncertain"
        }

    total_weight   = 0.0
    weighted_score = 0.0

    for p in scored_passages:
        relevance = p.get("relevance", 0.5)
        verdict   = p["verdict"]

        if verdict == "CONTRADICTS":
            contribution = 1.0
        elif verdict == "SUPPORTS":
            contribution = 0.0
        else:
            contribution = 0.5

        weighted_score += contribution * relevance
        total_weight   += relevance

    final_score = weighted_score / total_weight if total_weight > 0 else 0.5
    final_score = round(final_score, 4)

    if final_score >= 0.7:
        label = "hallucinated"
    elif final_score <= 0.3:
        label = "grounded"
    else:
        label = "uncertain"

    avg_confidence = sum(p["confidence"] for p in scored_passages) / len(scored_passages)
    if avg_confidence >= 0.85:
        confidence = "high"
    elif avg_confidence >= 0.65:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "score":      final_score,
        "label":      label,
        "confidence": confidence
    }