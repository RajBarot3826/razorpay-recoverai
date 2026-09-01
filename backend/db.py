import os
from pathlib import Path
from sqlalchemy import create_engine, Column, String, Float, DateTime, JSON, Boolean, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from contextlib import contextmanager

from .config import settings

_project_root = Path(__file__).resolve().parent.parent
_data_dir = _project_root / "data"
_data_dir.mkdir(parents=True, exist_ok=True)

_db_url = f"sqlite:///{_data_dir / 'recoverai.db'}"
engine = create_engine(_db_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DBTransaction(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    method = Column(String, nullable=False)
    status = Column(String, nullable=False)
    failure_reason = Column(String, nullable=True)
    customer_id = Column(String, nullable=False)
    merchant_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_ = Column("metadata", JSON, default={})

class DBClassification(Base):
    __tablename__ = "classifications"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transaction_id = Column(String, ForeignKey("transactions.id"))
    failure_type = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    features = Column(JSON, default={})

class DBRootCause(Base):
    __tablename__ = "root_causes"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transaction_id = Column(String, ForeignKey("transactions.id"))
    root_cause = Column(String, nullable=False)
    explanation = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    recommended_actions = Column(JSON, default=[])

class DBRecoveryAction(Base):
    __tablename__ = "recovery_actions"
    id = Column(String, primary_key=True, index=True)
    transaction_id = Column(String, ForeignKey("transactions.id"))
    action_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    details = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    outcome = Column(String, nullable=True)

class DBAuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transaction_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    agent_name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    reasoning = Column(String, nullable=False)
    outcome = Column(String, nullable=True)
    compliance_check = Column(Boolean, default=True)

def init_db():
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
