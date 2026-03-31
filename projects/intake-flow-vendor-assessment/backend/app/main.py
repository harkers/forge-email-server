"""
FastAPI application entry point — OE-PRIV-IFV-001 Intake Flow Vendor Assessment
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import engine, get_db, Base
from app.redis import close_redis
from app.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await close_redis()
    await engine.dispose()


app = FastAPI(
    title="Intake Flow — Vendor Assessment API",
    description="OE-PRIV-IFV-001 — Multi-agent ProPharma vendor assessment pipeline",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "service": "ifv-backend", "version": "0.1.0"}


# Mount API routes
from app.api import assessments, vendors, pipeline, cloak

app.include_router(assessments.router, prefix="/api/assessments", tags=["assessments"])
app.include_router(vendors.router, prefix="/api/vendors", tags=["vendors"])
app.include_router(pipeline.router, prefix="/api/pipeline", tags=["pipeline"])
app.include_router(cloak.router, prefix="/api/cloak", tags=["cloak"])
