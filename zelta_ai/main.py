import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from zelta_ai.brain.bayse.stress_signal import monitor

DEBUG = os.getenv("DEBUG", "true").lower() == "true"


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: connect Bayse WebSocket for live stress signal.
    Shutdown: cancel background task cleanly.
    """
    print("[ZELTA Brain] Starting Bayse stress monitor...")
    task = asyncio.create_task(monitor.start())

    try:
        yield
    finally:
        print("[ZELTA Brain] Shutting down...")
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="ZELTA AI Brain",
    description=(
        "Stateless Behavioral Quantitative Intelligence Engine. "
        "Called by ZELTA backend only. Not exposed to frontend directly."
    ),
    version="1.0.0",
    lifespan=lifespan,
    # Hide docs in production
    docs_url="/docs" if DEBUG else None,
    redoc_url=None,
)


# ── CORS ──────────────────────────────────────────────────────────────────────
# IMPORTANT: Brain only accepts requests from the backend
# Frontend must NEVER call this service directly
ALLOWED_ORIGINS = (
    [
        "http://localhost:8001",   # local backend
        "http://127.0.0.1:8001",
    ]
    if DEBUG else
    [
        os.getenv("BACKEND_URL", "https://your-backend.run.app"),
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(router)


# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "service":  "ZELTA AI Brain",
        "status":   "running",
        "type":     "stateless-ai-engine",
        "note":     (
            "This service is called by the ZELTA backend only. "
            "Frontend does not call this directly."
        ),
    }


# ── Dev entry point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        reload=DEBUG,
    )