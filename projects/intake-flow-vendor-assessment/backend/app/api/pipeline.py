"""Pipeline API stubs — wire up to DPM once agents are implemented."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()
