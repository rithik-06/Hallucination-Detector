from pipeline import run_pipeline
import json

claims = [
    "Einstein won Nobel Prize for Theory of Relativity",
    "The iPhone was invented by Bill Gates in 2007",
]

for claim in claims:
    result = run_pipeline(claim)
    print(f"\n{'='*60}")
    print(f"Claim:      {result.original_claim}")
    print(f"Score:      {result.score}")
    print(f"Label:      {result.label}")
    print(f"Confidence: {result.confidence}")
    print(f"\nSub-claims:")
    for sc in result.sub_claims:
        print(f"  → {sc.text}")
        print(f"     Score: {sc.score} | {sc.verdict}")
    print(f"\nExplanation: {result.explanation}")