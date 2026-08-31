"""
Pydantic v2 data models for RecoverAI.
Defines all schemas used across the pipeline: transactions, classifications,
root cause analysis, recovery actions, audit entries, and metrics.
"""

from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime


# ─── Enums ──────────────────────────────────────────────────────────────────

class PaymentMethod(str, Enum):
    CARD = "card"
    UPI = "upi"
    NETBANKING = "netbanking"
    WALLET = "wallet"
    UNKNOWN = "unknown"


class TransactionStatus(str, Enum):
    CREATED = "created"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    REFUNDED = "refunded"
    FAILED = "failed"
    PENDING = "pending"


class FailureType(str, Enum):
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
    BANK_TIMEOUT = "BANK_TIMEOUT"
    INVALID_CARD = "INVALID_CARD"
    UPI_TIMEOUT = "UPI_TIMEOUT"
    NETWORK_ERROR = "NETWORK_ERROR"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    RISK_BLOCKED = "RISK_BLOCKED"
    EXPIRED_CARD = "EXPIRED_CARD"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"
    APP_NOT_RESPONDING = "APP_NOT_RESPONDING"
    INCORRECT_PIN = "INCORRECT_PIN"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    UNKNOWN = "UNKNOWN"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ActionType(str, Enum):
    SMART_RETRY = "SMART_RETRY"
    CUSTOMER_NUDGE = "CUSTOMER_NUDGE"
    ALTERNATIVE_METHOD = "ALTERNATIVE_METHOD"
    ESCALATION = "ESCALATION"


class ActionStatus(str, Enum):
    PENDING = "PENDING"
    EXECUTING = "EXECUTING"
    SCHEDULED = "SCHEDULED"
    SUCCESS = "SUCCESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    BLOCKED = "BLOCKED"


# ─── Core Models ────────────────────────────────────────────────────────────

class PaymentTransaction(BaseModel):
    """A single payment transaction (typically a failed one)."""
    id: str
    amount: float
    currency: str = "INR"
    method: str = "unknown"  # Using str for flexibility with simulator
    status: str = "failed"
    failure_reason: Optional[str] = None
    customer_id: str = ""
    merchant_id: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FailureClassification(BaseModel):
    """Result of ML failure classification."""
    transaction_id: str
    failure_type: str  # Using str for flexibility with classifier output
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    features: Dict[str, Any] = Field(default_factory=dict)


class RootCauseAnalysis(BaseModel):
    """LLM-powered root cause analysis result."""
    transaction_id: str
    root_cause: str
    explanation: str
    severity: str = "MEDIUM"  # Using str for flexibility
    recommended_actions: List[str] = Field(default_factory=list)


class RecoveryAction(BaseModel):
    """A single recovery action taken by an agent."""
    id: str
    transaction_id: str
    action_type: str  # Using str for flexibility
    status: str = "PENDING"
    details: Any = ""  # Can be string or dict
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    outcome: Optional[str] = None


class AuditEntry(BaseModel):
    """A single entry in the audit trail."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_name: str = ""
    action: str = ""
    reasoning: str = ""
    outcome: Optional[str] = None
    compliance_check: bool = True
    details: Dict[str, Any] = Field(default_factory=dict)


class RecoveryResult(BaseModel):
    """Result of the full recovery pipeline for one transaction."""
    transaction_id: str
    original_amount: float = 0.0
    recovered: bool = False
    success: bool = False
    failure_type: Optional[str] = None
    confidence_score: float = 0.0
    root_cause: Optional[str] = None
    recommended_action: Optional[RecoveryAction] = None
    executed_action: Optional[RecoveryAction] = None
    execution_details: Dict[str, Any] = Field(default_factory=dict)
    actions_taken: List[RecoveryAction] = Field(default_factory=list)
    audit_trail: List[AuditEntry] = Field(default_factory=list)
    error_message: Optional[str] = None
    original_transaction: Optional[PaymentTransaction] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RecoveryMetrics(BaseModel):
    """Aggregate metrics across all processed transactions."""
    total_transactions: int = 0
    total_processed: int = 0
    total_failures: int = 0
    total_recovered: int = 0
    total_failed: int = 0
    recovery_rate: float = 0.0
    amount_at_risk: float = 0.0
    amount_recovered: float = 0.0
    total_revenue_recovered: float = 0.0
    avg_recovery_time: float = 0.0
    by_failure_type: Dict[str, Any] = Field(default_factory=dict)
    by_action_type: Dict[str, Any] = Field(default_factory=dict)


# ─── Request/Response Models ────────────────────────────────────────────────

class SimulateRequest(BaseModel):
    """Request body for /api/simulate."""
    count: int = Field(default=10, ge=1, le=1000)


class BatchRecoverRequest(BaseModel):
    """Request body for /api/recover/batch."""
    transactions: List[PaymentTransaction]
