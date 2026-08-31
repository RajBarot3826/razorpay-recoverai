import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from backend.models.schemas import PaymentTransaction, FailureClassification, RecoveryAction
from backend.compliance.guardrails import ComplianceGuardrails

logger = logging.getLogger(__name__)

class SmartRetryAgent:
    def __init__(self, guardrails: ComplianceGuardrails = None):
        self.guardrails = guardrails or ComplianceGuardrails()

    async def execute(self, transaction: PaymentTransaction, classification: FailureClassification) -> RecoveryAction:
        proposed_action = RecoveryAction(
            id=f"retry_{int(datetime.now(timezone.utc).timestamp()*1000)}",
            action_type="SMART_RETRY",
            status="PENDING",
            details={"notes": "Determining optimal retry window..."},
        )

        allowed, reason = self.guardrails.check(transaction, proposed_action)
        if not allowed:
            proposed_action.status = "BLOCKED"
            proposed_action.outcome = f"Blocked: {reason}"
            return proposed_action

        failure_type = str(classification.failure_type).upper()
        now = datetime.now(timezone.utc)
        retry_time = now + timedelta(hours=2)

        if "NETWORK" in failure_type:
            retry_time = now + timedelta(minutes=15)
        elif "INSUFFICIENT_FUNDS" in failure_type:
            retry_time = (now + timedelta(days=1)).replace(hour=10, minute=0, second=0)

        proposed_action.details = {"scheduled_time": retry_time.isoformat()}
        proposed_action.status = "SCHEDULED"
        
        return proposed_action
