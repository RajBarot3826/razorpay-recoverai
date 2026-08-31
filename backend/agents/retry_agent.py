import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from backend.models.schemas import PaymentTransaction, FailureClassification, RecoveryAction
from backend.compliance.guardrails import ComplianceGuardrails

logger = logging.getLogger(__name__)

class SmartRetryAgent:
    """
    Determines optimal retry timing and executes retries.
    """
    def __init__(self, guardrails: ComplianceGuardrails = None):
        self.guardrails = guardrails or ComplianceGuardrails()

    async def execute(self, transaction: PaymentTransaction, classification: FailureClassification) -> RecoveryAction:
        """
        Plan and execute a smart retry.
        """
        proposed_action = RecoveryAction(
            id=f"retry_{int(datetime.now(timezone.utc).timestamp()*1000)}",
            transaction_id=transaction.id,
            action_type="SMART_RETRY",
            status="PENDING",
            details="Determining optimal retry window...",
            created_at=datetime.now(timezone.utc)
        )

        allowed, reason = self.guardrails.check(transaction, proposed_action)
        if not allowed:
            proposed_action.status = "BLOCKED"
            proposed_action.outcome = f"Blocked by guardrails: {reason}"
            proposed_action.completed_at = datetime.now(timezone.utc)
            return proposed_action

        # Logic for smart timing
        failure_type = str(classification.failure_type).upper()
        now = datetime.now(timezone.utc)
        retry_time = now + timedelta(hours=2) # Default 2 hours

        if "NETWORK" in failure_type:
            retry_time = now + timedelta(minutes=15)
        elif "INSUFFICIENT_FUNDS" in failure_type:
            # Simple heuristic: try on next day at 10 AM
            retry_time = (now + timedelta(days=1)).replace(hour=10, minute=0, second=0)

        proposed_action.details = f"Scheduled retry for {retry_time.isoformat()}"
        proposed_action.status = "SCHEDULED"
        
        return proposed_action
