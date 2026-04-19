import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from brain.bayse.stress_signal import monitor

DEBUG = os.getenv("DEBUG", "true").lower() == "true"
PORT  = int(os.getenv("PORT", "8080"))


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Start Bayse WebSocket monitor in background.
    App starts and binds port FIRST, then connects Bayse.
    This prevents Cloud Run startup timeout.
    """
    print("[ZELTA Brain] Starting up...")

    # Start Bayse monitor safely in background
    # App does NOT wait for it — port binds immediately
    async def safe_start():
        try:
            print("[ZELTA Brain] Connecting to Bayse WebSocket...")
            await monitor.start()
        except Exception as e:
            print(f"[ZELTA Brain] Bayse monitor error: {e}")
            print("[ZELTA Brain] Running with default stress signal")

    task = asyncio.create_task(safe_start())
    print("[ZELTA Brain] Ready. Bayse monitor starting in background.")

    yield  # App is running and serving requests

    print("[ZELTA Brain] Shutting down...")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


# ── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="ZELTA AI Brain",
    description="Behavioral Quantitative Financial Intelligence",
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
app.include_router(router)


# ── Root health check ─────────────────────────────────────────────────────────
# Cloud Run pings this to check if app is alive
# MUST respond in milliseconds — no ML calls here
@app.get("/")
def root():
    return {
        "service": "ZELTA AI Brain",
        "status":  "running",
        "version": "1.0.0",
        "bayse_connected": monitor.ws.connected,
        "stress_score":    monitor.current_signal.get("score", 50),
    }


# ── Dev entry point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=DEBUG,
    )