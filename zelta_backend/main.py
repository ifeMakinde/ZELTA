import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routes
from routes.intelligence import router as intelligence_router
from routes.wallet       import router as wallet_router
from routes.simulation   import router as simulation_router
from routes.copilot      import router as copilot_router
from routes.portfolio    import router as portfolio_router
from routes.profile      import router as profile_router

# Config
from config.settings import settings

DEBUG = settings.DEBUG
PORT  = settings.PORT


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: verify AI Brain is reachable.
    Shutdown: clean up connections.
    """
    print("[ZELTA Backend] Starting up...")
    print(f"[ZELTA Backend] AI Brain URL: {settings.AI_BRAIN_URL}")
    print(f"[ZELTA Backend] Debug mode:   {DEBUG}")

    # Quick brain health check on startup
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{settings.AI_BRAIN_URL}/")
            if r.status_code == 200:
                print("[ZELTA Backend] ✅ AI Brain connected")
            else:
                print(f"[ZELTA Backend] ⚠️ AI Brain returned {r.status_code}")
    except Exception as e:
        print(f"[ZELTA Backend] ⚠️ AI Brain not reachable: {e}")
        print("[ZELTA Backend] Will retry on first request")

    yield

    print("[ZELTA Backend] Shutting down...")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="ZELTA Backend API",
    description="Behavioral Quantitative Financial Intelligence — Backend",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if DEBUG else None,
    redoc_url=None,
)


# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten after hackathon
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(intelligence_router)
app.include_router(wallet_router)
app.include_router(simulation_router)
app.include_router(copilot_router)
app.include_router(portfolio_router)
app.include_router(profile_router)


# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "service":    "ZELTA Backend API",
        "status":     "running",
        "version":    "1.0.0",
        "brain_url":  settings.AI_BRAIN_URL,
        "debug":      DEBUG,
    }


@app.get("/health")
def health():
    return {
        "status":  "ok",
        "service": "ZELTA Backend",
    }


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=DEBUG,
    )