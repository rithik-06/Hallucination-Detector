from retriever import retrieve_evidence
from nli_scorer import score_all_passages, compute_hallucination_score

claim = "Einstein won Nobel Prize for Theory of Relativity"

# Step 1 — retrieve real evidence
passages = retrieve_evidence(claim)

# Step 2 — score each passage
scored = score_all_passages(claim, passages)

# Step 3 — compute final score
result = compute_hallucination_score(scored)

for p in scored:
    print(f"\nSource:  {p['source']}")
    print(f"Text:    {p['text'][:80]}")
    print(f"Verdict: {p['verdict']}")
    print(f"Scores:  {p['scores']}")

print(f"\n{'='*50}")
print(f"Final Score:  {result['score']}")
print(f"Label:        {result['label']}")
print(f"Confidence:   {result['confidence']}")