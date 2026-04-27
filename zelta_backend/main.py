"""
ZELTA Backend — Behavioral Quantitative Financial Intelligence
FastAPI + Firebase + Vertex AI

Entry point: initializes Firebase, registers all routes, and starts the server.
"""

import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from config.settings import settings
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
    try:
        initialize_firebase()
        logger.info("Firebase initialized. BQ Brain ready.")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        # Depending on criticality, you might want to raise e here to stop startup
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
async def global_exception_handler(request: Request, exc: Exception):
    # If the error is a standard FastAPI/Starlette HTTPException (like 404 or 401),
    # return its intended status code and message instead of a generic 500.
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "message": exc.detail},
        )

    # Log the actual stack trace for real internal server errors
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An unexpected error occurred.",
            "detail": str(exc) if settings.DEBUG else "Internal Server Error",
        },
    )


# ─── Dev Server ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Ensure the file is named main.py for the string import to work
    port = int(os.environ.get("PORT", 8080))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=True if settings.DEBUG else False
    )
