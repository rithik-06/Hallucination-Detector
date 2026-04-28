from transformers import pipeline
from typing import List , Dict

# load the nli model once at startup
##  this model will take 2-3 seconds to load then saves itself in memory

nli_model = pipeline(
    "zero_shot_classification",
    model="cross-encoder/nli-deberta-v3-small",

    device = -1  # device -1 means use cpu

)
print("NLI model loaded and ready to use")

def score_passage(claim:str , passage:str) -> Dict:
    """ score a single passage against thr claim"""

    result = nli_model(
        passage,
        candidate_labels=[claim],
        hypothesis_template="{}",
    )

    # deberta gives us entailment/contradiction/neutral scores
    raw = nli_model.model(
        **nli_model.tokenizer(
            passage, claim,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )
    )


    import torch
    probs = torch.softmax(raw.logits, dim=1).tolist()[0] # convert to probabilities
    # label order for this model: contradiction, neutral, entailment
    contradiction = probs[0]
    neutral       = probs[1]
    entailment    = probs[2]

    # pick the strongest label
    scores = {
        "CONTRADICTS": contradiction,
        "NEUTRAL":     neutral,
        "SUPPORTS":    entailment
    }
    verdict = max(scores, key=scores.get)

    return {
        "verdict":      verdict,
        "contradiction": round(contradiction, 4),
        "neutral":       round(neutral,       4),
        "entailment":    round(entailment,    4),
        "confidence":    round(max(probs),    4)
    }

def score_all_passages(claim: str, passages: List[Dict]) -> List[Dict]:
    """Score every passage and attach verdict to each."""

    scored = []
    for passage in passages:
        print(f" Scoring: {passage['text'][:60]}...")
        result = score_passage(claim, passage["text"])

        scored.append({
            **passage,               # keep source, text, relevance
            "verdict":    result["verdict"],
            "confidence": result["confidence"],
            "scores":     {
                "contradiction": result["contradiction"],
                "neutral":       result["neutral"],
                "entailment":    result["entailment"]
            }
        })

    return scored

def compute_hallucination_score(scored_passages: List[Dict]) -> Dict:
    """
    Aggregate all passage verdicts into one final score.

    Logic:
    - Each CONTRADICTS passage pushes score UP
    - Each SUPPORTS passage pushes score DOWN
    - Each NEUTRAL passage has little effect
    - Weighted by relevance of the passage
    """

    if not scored_passages:
        return {
            "score":      0.5,
            "confidence": "low",
            "label":      "uncertain"
        }

    total_weight    = 0.0
    weighted_score  = 0.0

    for p in scored_passages:
        relevance = p.get("relevance", 0.5)
        verdict   = p["verdict"]

        # convert verdict to hallucination contribution
        if verdict == "CONTRADICTS":
            contribution = 1.0   # strong hallucination signal
        elif verdict == "SUPPORTS":
            contribution = 0.0   # strong grounded signal
        else:
            contribution = 0.5   # neutral — no strong signal

        weighted_score += contribution * relevance
        total_weight   += relevance

    final_score = weighted_score / total_weight if total_weight > 0 else 0.5
    final_score = round(final_score, 4)

    # determine label
    if final_score >= 0.7:
        label = "hallucinated"
    elif final_score <= 0.3:
        label = "grounded"
    else:
        label = "uncertain"

# determine confidence based on evidence strength
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