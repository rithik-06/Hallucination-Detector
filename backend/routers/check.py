from fastapi import APIRouter, HTTPException
from models.schemas import ClaimRequest, ClaimResponse
from retriever import retrieve_evidence
from nli_scorer import score_all_passages, compute_hallucination_score
from models.schemas import EvidenceItem

router = APIRouter()

@router.post("/check", response_model=ClaimResponse)
def check_claim(request: ClaimRequest):
    try:
        # Step 1 — retrieve evidence
        passages = retrieve_evidence(request.claim)

        if not passages:
            return ClaimResponse(
                original_claim = request.claim,
                score          = 0.5,
                label          = "uncertain",
                confidence     = "low",
                sub_claims     = [],
                evidence       = [],
                explanation    = "No evidence found for this claim."
            )

        # Step 2 — score passages
        scored = score_all_passages(request.claim, passages)

        # Step 3 — compute final score
        result = compute_hallucination_score(scored)

        # Step 4 — build evidence items
        evidence_items = [
            EvidenceItem(
                source    = p["source"],
                text      = p["text"],
                verdict   = p["verdict"],
                relevance = p.get("relevance", 0.0)
            )
            for p in scored
        ]

        # Step 5 — generate explanation
        contradicting = [p for p in scored if p["verdict"] == "CONTRADICTS"]
        supporting    = [p for p in scored if p["verdict"] == "SUPPORTS"]

        if result["label"] == "hallucinated" and contradicting:
            explanation = f"Found {len(contradicting)} contradicting source(s). Strongest: '{contradicting[0]['text'][:100]}'"
        elif result["label"] == "grounded" and supporting:
            explanation = f"Found {len(supporting)} supporting source(s). Strongest: '{supporting[0]['text'][:100]}'"
        else:
            explanation = f"Mixed evidence — {len(contradicting)} contradicting, {len(supporting)} supporting."

        return ClaimResponse(
            original_claim = request.claim,
            score          = result["score"],
            label          = result["label"],
            confidence     = result["confidence"],
            sub_claims     = [],
            evidence       = evidence_items,
            explanation    = explanation
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))