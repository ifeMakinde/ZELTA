"""
ZELTA Backend — Behavioral Quantitative Financial Intelligence
FastAPI + Firebase + Vertex AI

Entry point: initializes Firebase, registers all routes, and starts the server.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from core.firebase import initialize_firebase
from middleware.cors import setup_cors
from routes import intelligence, wallet, simulation, copilot, portfolio, profile

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ─── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize Firebase on startup."""
    logger.info("ZELTA Backend starting up...")
    initialize_firebase()
    logger.info("Firebase initialized. BQ Brain ready.")
    yield
    logger.info("ZELTA Backend shutting down.")


# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="ZELTA Backend",
    description=(
        "Behavioral Quantitative Financial Intelligence for Nigerian university students. "
        "Powered by Bayse Markets crowd intelligence, Bayesian inference, and Kelly Criterion allocation."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── Middleware ────────────────────────────────────────────────────────────────
setup_cors(app)

# ─── Routes ───────────────────────────────────────────────────────────────────
app.include_router(intelligence.router)
app.include_router(wallet.router)
app.include_router(simulation.router)
app.include_router(copilot.router)
app.include_router(portfolio.router)
app.include_router(profile.router)


# ─── Health Check ─────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "ZELTA Backend",
        "version": "1.0.0",
        "status": "operational",
        "description": "Behavioral Quantitative Financial Intelligence",
        "powered_by": ["Bayse Markets", "Gemini Pro", "Vertex AI", "FastAPI"],
    }


@app.get("/health", tags=["Health"])
async def health():
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "service": "zelta-backend"},
    )


# ─── Global Exception Handler ─────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An unexpected error occurred.",
            "detail": str(exc),
        },
    )


# ─── Dev Server ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    from config.settings import settings

    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_env == "development",
        log_level="info",
    )