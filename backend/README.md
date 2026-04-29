---
title: Hallucination Detector
emoji: 🔍
colorFrom: red
colorTo: yellow
sdk: docker
pinned: false
---

# Hallucination Detector — VS Code Extension

Detects hallucinations in LLM-generated text directly inside VS Code.

## How It Works
1. Select any text in VS Code
2. Right click → "Check for Hallucination"
3. See colored underline + hover tooltip with evidence

## Color Codes
- 🔴 Red underline → Hallucinated (score > 70%)
- 🟡 Yellow underline → Uncertain (score 30-70%)
- 🟢 Green underline → Grounded (score < 30%)

## Setup

### Backend
git clone https://github.com/rithik-06/Hallucination-Detector
cd hallucination-detector/backend
pip install -r requirements.txt
uvicorn main:app --reload

### Extension
- Open hallucination-detector/hallucination-detector in VS Code
- Press F5 to launch

## Tech Stack
- FastAPI + DeBERTa NLI model
- Wikipedia + DuckDuckGo retrieval
- Sentence Transformers for ranking
- VS Code Extension API (TypeScript)

