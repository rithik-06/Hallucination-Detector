from decomposer import decompose_claim

claims = [
    "Einstein won Nobel Prize for Theory of Relativity",
    "The iPhone was invented by Bill Gates in 2007",
    "Python was created by Guido van Rossum and released in 1991"
]

for claim in claims:
    print(f"\nOriginal: {claim}")
    sub_claims = decompose_claim(claim)
    print(f"Decomposed into {len(sub_claims)} sub-claims:")
    for i, sc in enumerate(sub_claims, 1):
        print(f"  {i}. {sc}")