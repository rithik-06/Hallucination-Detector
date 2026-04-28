from fastapi import APIRouter
from models.schemas import ClaimRequest, ClaimResponse

router = APIRouter()

@router.post("/check", response_model=ClaimResponse)
def check_claim(request: ClaimRequest):

    #    Dummy response for now
    #  replace each part with real logic later
    return ClaimResponse(
        original_claim=request.claim,
        score=0.5,
        label="uncertain",
        confidence="low",
        sub_claims=[],
        evidence=[],
        explanation="Pipeline not yet connected — dummy response"
    )