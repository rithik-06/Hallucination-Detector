# Hallucination Detector

Detects hallucinations in LLM-generated text directly inside VS Code.

## Usage
1. Select any text in VS Code
2. Right click → "Check for Hallucination"
3. See colored underline + hover tooltip with evidence

## Color Codes
- 🔴 Red → Hallucinated (score > 70%)
- 🟡 Yellow → Uncertain (score 30-70%)
- 🟢 Green → Grounded (score < 30%)

## Requirements
Backend must be running — either locally or via HF Spaces.
