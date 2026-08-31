import logging
from datetime import datetime, timezone
from typing import List

from backend.models.schemas import PaymentTransaction, FailureClassification, RecoveryAction

logger = logging.getLogger(__name__)

class EscalationAgent:
    def __init__(self, amount_threshold: float = 10000.0):
        self.amount_threshold = amount_threshold

    async def evaluate_escalation(self, transaction: PaymentTransaction, classification: FailureClassification, previous_actions: List[RecoveryAction]) -> RecoveryAction:
        proposed_action = RecoveryAction(
            id=f"esc_{int(datetime.now(timezone.utc).timestamp()*1000)}",
            action_type="ESCALATION",
            status="PENDING",
            details={"notes": "Evaluating escalation criteria..."},
        )
        
        reasons = []
        
        if transaction.amount > self.amount_threshold:
            reasons.append(f"High value transaction (>₹{self.amount_threshold})")
            
        failure_type = str(classification.failure_type).upper()
        if "RISK" in failure_type or "FRAUD" in failure_type:
            reasons.append("Flagged by risk/fraud systems")
            
        retry_count = sum(1 for a in previous_actions if a.action_type == "SMART_RETRY")
        if retry_count >= 3:
            reasons.append("Repeated failures (>= 3 retries)")
            
        if reasons:
            proposed_action.status = "COMPLETED"
            proposed_action.details = {"reasons": reasons}
            proposed_action.outcome = "Escalated to human review queue."
        else:
            proposed_action.status = "SKIPPED"
            proposed_action.details = {"notes": "Does not meet escalation criteria."}
            proposed_action.outcome = "No escalation needed."
            
        return proposed_action
