from typing import List
import logging
from datetime import datetime, timezone

from backend.models.schemas import RootCauseAnalysis, RecoveryAction

logger = logging.getLogger(__name__)

class RecoveryStrategyEngine:
    """
    Decides the best recovery actions based on Root Cause Analysis.
    """
    
    def __init__(self):
        pass

    async def decide_strategy(self, rca: RootCauseAnalysis, transaction_amount: float = 0.0) -> List[RecoveryAction]:
        """
        Determine the ordered list of recovery actions.
        """
        actions = []
        severity = rca.severity.upper() if isinstance(rca.severity, str) else rca.severity.value
        
        # 1. Critical severity -> immediate escalation
        if severity == "CRITICAL":
            actions.append(
                self._create_action(rca.transaction_id, "ESCALATION", "Immediate human review required due to critical risk.")
            )
            return actions

        # 2. High value transactions get priority alternative suggestion or escalation if complex
        if transaction_amount > 10000 and severity == "HIGH":
            actions.append(
                self._create_action(rca.transaction_id, "ESCALATION", "High value transaction failed with high severity.")
            )

        # 3. Handle based on root cause / recommendations
        rca_lower = rca.root_cause.lower()
        if "fund" in rca_lower or "nsf" in rca_lower:
            actions.append(self._create_action(rca.transaction_id, "CUSTOMER_NUDGE", "Nudge customer for insufficient funds."))
            actions.append(self._create_action(rca.transaction_id, "SMART_RETRY", "Schedule smart retry for next salary day."))
        elif "network" in rca_lower or "timeout" in rca_lower or "downtime" in rca_lower:
            actions.append(self._create_action(rca.transaction_id, "SMART_RETRY", "Immediate or short-delay retry due to network issue."))
        elif "expire" in rca_lower or "invalid" in rca_lower:
            actions.append(self._create_action(rca.transaction_id, "CUSTOMER_NUDGE", "Ask customer to update payment method."))
            actions.append(self._create_action(rca.transaction_id, "ALTERNATIVE_METHOD", "Suggest UPI or other method."))
        else:
            # Fallback strategy
            actions.append(self._create_action(rca.transaction_id, "ALTERNATIVE_METHOD", "Suggest alternative payment method."))
            actions.append(self._create_action(rca.transaction_id, "CUSTOMER_NUDGE", "General failure notification."))

        return actions

    def _create_action(self, transaction_id: str, action_type: str, details: str) -> RecoveryAction:
        return RecoveryAction(
            id=f"act_{int(datetime.now(timezone.utc).timestamp()*1000)}",
            transaction_id=transaction_id,
            action_type=action_type,
            status="PENDING",
            details=details,
            created_at=datetime.now(timezone.utc)
        )
