#!/usr/bin/env python3
"""Database layer for Forge Pipeline - supports SQLite and PostgreSQL."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path

from sqlalchemy import create_engine, Column, Text, DateTime, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool

# Database URL - supports both SQLite and PostgreSQL
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    f"sqlite:///{Path(__file__).parent / 'storage' / 'forge-pipeline.db'}"
)

# Detect database type
IS_POSTGRES = DATABASE_URL.startswith("postgresql")
IS_SQLITE = DATABASE_URL.startswith("sqlite")

# Engine configuration
if IS_SQLITE:
    # SQLite configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    # PostgreSQL configuration with connection pooling
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        pool_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    
    # Run migrations
    if IS_SQLITE:
        # SQLite: manually add columns if missing
        with engine.connect() as conn:
            try:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN risk_state TEXT NOT NULL DEFAULT 'none'"))
            except Exception:
                pass  # Column exists
            conn.commit()


def get_session():
    """Get a database session."""
    return SessionLocal()


# Models
class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text, default="")
    notes = Column(Text, default="")
    status = Column(Text, default="not-started")
    tags_json = Column(Text, default="[]")
    updated_at = Column(Text, nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description or "",
            "notes": self.notes or "",
            "status": self.status,
            "tags": json.loads(self.tags_json or "[]"),
            "updatedAt": self.updated_at,
        }


class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    status = Column(Text, default="todo")
    priority = Column(Text, default="medium")
    risk_state = Column(Text, default="none")
    due_date = Column(Text, default="")
    tags_json = Column(Text, default="[]")
    notes = Column(Text, default="")
    updated_at = Column(Text, nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "priority": self.priority,
            "riskState": self.risk_state,
            "dueDate": self.due_date,
            "tags": json.loads(self.tags_json or "[]"),
            "notes": self.notes or "",
            "updatedAt": self.updated_at,
        }


class Event(Base):
    __tablename__ = "events"
    
    id = Column(Text, primary_key=True)
    kind = Column(Text, nullable=False)
    created_at = Column(Text, nullable=False)
    payload_json = Column(Text, default="{}")
    
    def to_dict(self):
        return {
            "id": self.id,
            "kind": self.kind,
            "createdAt": self.created_at,
            "payload": json.loads(self.payload_json or "{}"),
        }


import json