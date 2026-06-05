"""
Plum OPD Claim Adjudication Tool — FastAPI Application
Main entry point for the backend server.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import CORS_ORIGINS, UPLOAD_DIR
from app.database import connect_db, close_db
from app.routers import claims, members, policy


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown events."""
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="Plum OPD Claim Adjudication API",
    description="AI-powered OPD insurance claim adjudication system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory for serving documents
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(claims.router)
app.include_router(members.router)
app.include_router(policy.router)


@app.get("/")
async def root():
    return {
        "name": "Plum OPD Claim Adjudication API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "claims": "/api/claims",
            "members": "/api/members",
            "policy": "/api/policy",
            "stats": "/api/claims/stats"
        }
    }


@app.get("/health")
async def health_check():
    from app.database import get_db
    db = get_db()
    try:
        await db.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy",
        "database": db_status,
        "version": "1.0.0"
    }
