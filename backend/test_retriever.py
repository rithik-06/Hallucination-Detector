from retriever import retrieve_evidence

results = retrieve_evidence("Einstein won Nobel Prize for Theory of Relativity")

for r in results:
    print(f"Source: {r['source']}")
    print(f"Relevance: {r['relevance']}")
    print(f"Text: {r['text']}\n")
