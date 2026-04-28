from decomposer import decompose_claim
from retriever import retrieve_evidence
from nli_scorer import score_all_passages, compute_hallucination_score
from models.schemas import ClaimResponse, SubClaim, EvidenceItem
from typing import List


def generate_explanation(label: str, scored_passages: list, sub_claims: list) -> str:
    """Generate a human readable explanation of the result."""

    contradicting = [p for p in scored_passages if p["verdict"] == "CONTRADICTS"]
    supporting    = [p for p in scored_passages if p["verdict"] == "SUPPORTS"]

    if label == "hallucinated":
        if contradicting:
            return (
                f"Found {len(contradicting)} piece(s) of evidence that contradict this claim. "
                f"Strongest contradiction: '{contradicting[0]['text'][:100]}...'"
            )
        return "Claim could not be verified against available evidence."

    elif label == "grounded":
        if supporting:
            return (
                f"Found {len(supporting)} piece(s) of evidence that support this claim. "
                f"Strongest support: '{supporting[0]['text'][:100]}...'"
            )
        return "Claim appears consistent with available evidence."

    else:
        return (
            f"Evidence is mixed or insufficient. "
            f"{len(contradicting)} contradicting, {len(supporting)} supporting passages found."
        )


def run_pipeline(claim: str, domain: str = "general") -> ClaimResponse:
    """
    Full hallucination detection pipeline.
    
    Steps:
    1. Decompose claim into sub-claims
    2. Retrieve evidence for each sub-claim
    3. Score evidence against each sub-claim
    4. Aggregate into final score
    5. Return structured response
    """

    print(f"\n{'='*60}")
    print(f"Running pipeline for: {claim}")
    print(f"{'='*60}")

    # ── Step 1: Decompose ──────────────────────────────────────
    print("\n Step 1: Decomposing claim...")
    sub_claim_texts = decompose_claim(claim)
    print(f"   → {len(sub_claim_texts)} sub-claims found")

    # ── Step 2 & 3: Retrieve + Score each sub-claim ────────────
    print("\n Step 2 & 3: Retrieving evidence + scoring...")
    all_scored_passages = []
    sub_claim_results   = []

    for sc_text in sub_claim_texts:
        print(f"\n   Sub-claim: {sc_text}")

        # retrieve evidence for this specific sub-claim
        passages = retrieve_evidence(sc_text)

        if not passages:
            print(f"   ⚠️ No evidence found for: {sc_text}")
            sub_claim_results.append(SubClaim(
                text    = sc_text,
                score   = 0.5,
                verdict = "uncertain"
            ))
            continue

        # score passages against this sub-claim
        scored = score_all_passages(sc_text, passages)
        result = compute_hallucination_score(scored)

        # collect all passages for final evidence list
        all_scored_passages.extend(scored)

        sub_claim_results.append(SubClaim(
            text    = sc_text,
            score   = result["score"],
            verdict = result["label"]
        ))

        print(f"   → Score: {result['score']} | Label: {result['label']}")

    # ── Step 4: Aggregate final score ─────────────────────────
    print("\n Step 4: Aggregating final score...")

    if sub_claim_results:
        # final score = average of all sub-claim scores
        final_score = sum(sc.score for sc in sub_claim_results) / len(sub_claim_results)
        final_score = round(final_score, 4)
    else:
        final_score = 0.5

    # determine final label
    if final_score >= 0.7:
        label = "hallucinated"
    elif final_score <= 0.3:
        label = "grounded"
    else:
        label = "uncertain"

    # determine confidence
    if all_scored_passages:
        avg_conf = sum(p["confidence"] for p in all_scored_passages) / len(all_scored_passages)
        confidence = "high" if avg_conf >= 0.85 else "medium" if avg_conf >= 0.65 else "low"
    else:
        confidence = "low"

    # ── Step 5: Build response ─────────────────────────────────
    print("\n Step 5: Building response...")

    # deduplicate evidence — keep top 5 by relevance
    seen   = set()
    unique = []
    for p in sorted(all_scored_passages, key=lambda x: x.get("relevance", 0), reverse=True):
        if p["text"] not in seen:
            seen.add(p["text"])
            unique.append(p)
        if len(unique) == 5:
            break

    evidence_items = [
        EvidenceItem(
            source    = p["source"],
            text      = p["text"],
            verdict   = p["verdict"],
            relevance = p.get("relevance", 0.0)
        )
        for p in unique
    ]

    explanation = generate_explanation(label, all_scored_passages, sub_claim_results)

    return ClaimResponse(
        original_claim = claim,
        score          = final_score,
        label          = label,
        confidence     = confidence,
        sub_claims     = sub_claim_results,
        evidence       = evidence_items,
        explanation    = explanation
    )