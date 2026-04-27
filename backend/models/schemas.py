from pydantic import BaseModel
from typing import List, Optional

#  What comes IN 
class ClaimRequest(BaseModel):
    claim: str                  
    domain: Optional[str] = "general"  

#  A single piece of evidence 
class EvidenceItem(BaseModel):
    source: str                   # "Wikipedia", "DuckDuckGo"
    text: str                     
    verdict: str                  
    relevance: float              

#  A single decomposed claim
class SubClaim(BaseModel):
    text: str                    
    score: float                 
    verdict: str                 

#  What goes OUT
class ClaimResponse(BaseModel):
    original_claim: str           # echo back what was sent
    score: float                  
    label: str                    
    confidence: str               
    sub_claims: List[SubClaim]    
    evidence: List[EvidenceItem]  
    explanation: str              