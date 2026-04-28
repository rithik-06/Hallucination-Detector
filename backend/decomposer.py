from groq import Groq
from typing import List
import json
import os
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env file


client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def decompose_claim(claim: str) -> List[str]:
    """
    Split a complex claim into atomic sub-claims.
    
    Example:
    Input:  "Einstein won Nobel Prize in 1921 for Theory of Relativity"
    Output: [
        "Einstein won the Nobel Prize",
        "Einstein won the Nobel Prize in 1921",
        "The Nobel Prize was for Theory of Relativity"
    ]
    """

    prompt = f"""You are a fact-checking assistant. 
Your job is to break down a complex claim into simple, atomic sub-claims that can each be verified independently.

Rules:
- Each sub-claim must be a single verifiable fact

- Keep sub-claims short and specific
- Extract 2-4 sub-claims maximum
- Return ONLY a JSON array of strings, nothing else
- No preamble, no explanation, just the JSON array

Claim: "{claim}"

Return format: ["sub-claim 1", "sub-claim 2", "sub-claim 3"]"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,   # low temperature = consistent outputs
        max_tokens=200
    )

    raw = response.choices[0].message.content.strip()

    # parse JSON response
    try:
        sub_claims = json.loads(raw)
        # make sure it's a list of strings
        if isinstance(sub_claims, list):
            return [str(s) for s in sub_claims]
    except json.JSONDecodeError:
        print(f"⚠️ Could not parse decomposition: {raw}")
        # fallback — return original claim as single item
        return [claim]

    return [claim]