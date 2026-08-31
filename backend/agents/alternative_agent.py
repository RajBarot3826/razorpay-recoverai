import logging
from datetime import datetime, timezone

from backend.models.schemas import PaymentTransaction, FailureClassification, RecoveryAction
from backend.compliance.guardrails import ComplianceGuardrails

logger = logging.getLogger(__name__)

class AlternativePaymentAgent:
    def __init__(self, guardrails: ComplianceGuardrails = None):
        self.guardrails = guardrails or ComplianceGuardrails()

    async def suggest_alternative(self, transaction: PaymentTransaction, classification: FailureClassification) -> RecoveryAction:
        proposed_action = RecoveryAction(
            id=f"alt_{int(datetime.now(timezone.utc).timestamp()*1000)}",
            action_type="ALTERNATIVE_METHOD",
            status="PENDING",
            details={"notes": "Analyzing alternative methods..."},
        )

        allowed, reason = self.guardrails.check(transaction, proposed_action)
        if not allowed:
            proposed_action.status = "BLOCKED"
            proposed_action.outcome = f"Blocked: {reason}"
            return proposed_action

        current_method = str(transaction.method).lower()
        if "card" in current_method:
            alternatives = [("UPI", 0.95), ("Netbanking", 0.85)]
        elif "upi" in current_method:
            alternatives = [("Card", 0.90), ("Netbanking", 0.85)]
        else:
            alternatives = [("UPI", 0.95), ("Card", 0.90)]

        alt_str = ", ".join([f"{m} ({p*100:.0f}%)" for m, p in alternatives])
        
        proposed_action.status = "COMPLETED"
        proposed_action.details = {"alternatives": alt_str}
        proposed_action.outcome = f"Suggested alternatives: {alt_str}"

        return proposed_action
