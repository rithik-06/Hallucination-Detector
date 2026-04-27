from fastapi import FastAPI
from routers import check
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Hallucination Detector",
    description="Detects hallucinations in LLM-generated text",
    version= "1.0.0"
)

# ── Allow VS Code extension to call this API ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # any origin for now, tighten later
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Register routes ────────────────────────────
app.include_router(check.router, prefix="/api")

# ── Health check ───────────────────────────────
@app.get("/")
def root():
    return {"status": "running", "message": "Hallucination Detector API"}