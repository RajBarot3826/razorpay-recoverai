from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime

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
    SCHEDULED = "SCHEDULED"
    EXECUTED = "EXECUTED"
    SKIPPED = "SKIPPED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"

class PaymentTransaction(BaseModel):
    id: str
    amount: float
    currency: str = "INR"
    method: str = "card"
    status: str = "failed"
    failure_reason: Optional[str] = None
    customer_id: str
    merchant_id: str
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)

class FailureClassification(BaseModel):
    failure_type: FailureType
    confidence_score: float
    features_used: List[str]
    raw_reason: Optional[str] = None

    @property
    def confidence(self) -> float:
        return self.confidence_score

class RootCauseAnalysis(BaseModel):
    root_cause: str
    explanation: str
    severity: Severity
    recommended_actions: List[ActionType]
    llm_model_used: Optional[str] = None

class RecoveryAction(BaseModel):
    id: str
    action_type: ActionType
    status: ActionStatus = ActionStatus.PENDING
    scheduled_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    details: Any = Field(default_factory=dict)
    outcome: Optional[str] = None
    guardrail_passed: bool = True
    blocked_reason: Optional[str] = None

class AuditEntry(BaseModel):
    id: str
    transaction_id: str
    timestamp: datetime
    agent_name: str
    action: str
    details: Dict[str, Any] = Field(default_factory=dict)
    outcome: str

class RecoveryResult(BaseModel):
    transaction_id: str
    original_amount: float
    failure_type: str
    confidence_score: float
    root_cause: str
    actions_taken: List[RecoveryAction]
    audit_trail: List[AuditEntry]
    success: bool
    recovered_amount: float = 0.0
    recovered_at: Optional[datetime] = None
    merchant_id: Optional[str] = None
    method: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RecoveryMetrics(BaseModel):
    total_processed: int = 0
    total_recovered: int = 0
    total_failed: int = 0
    recovery_rate: float = 0.0
    total_revenue_recovered: float = 0.0
    total_revenue_lost: float = 0.0
    by_failure_type: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    by_action_type: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    average_latency_ms: float = 0.0

class SimulateRequest(BaseModel):
    count: int = 10
    failure_types: Optional[List[FailureType]] = None
    payment_methods: Optional[List[PaymentMethod]] = None
