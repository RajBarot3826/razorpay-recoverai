import logging
from datetime import datetime, timezone
from typing import Tuple, List

from backend.models.schemas import PaymentTransaction, RecoveryAction

logger = logging.getLogger(__name__)

class ComplianceGuardrails:
    """
    Enforces stopping rules and compliance logic.
    """
    def __init__(self):
        self.max_retries = 3
        self.quiet_hours_start = 21 # 9 PM
        self.quiet_hours_end = 8    # 8 AM
        self.amount_threshold_for_escalation = 10000.0

    def check(self, transaction: PaymentTransaction, proposed_action: RecoveryAction) -> Tuple[bool, str]:
        """
        Check if the proposed action is allowed.
        Returns (is_allowed, reason)
        """
        action_type = str(proposed_action.action_type).upper()
        
        # 1. No retries on Risk Blocked
        if "RISK" in str(transaction.failure_reason).upper() and action_type == "SMART_RETRY":
            return False, "Cannot retry risk-blocked transactions."

        # 2. Quiet Hours Check for Nudges
        if action_type == "CUSTOMER_NUDGE":
            now_hour = datetime.now(timezone.utc).hour # Simplified timezone logic (assume IST for hackathon or keep UTC)
            # Example assuming UTC matching local rules, in reality would use local time of customer
            if now_hour >= self.quiet_hours_start or now_hour < self.quiet_hours_end:
                return False, f"Cannot nudge during quiet hours (21:00 - 08:00). Current hour: {now_hour}"

        # 3. Could add max retry check here if we pass history

        return True, "Passed"

    def get_all_violations(self, transaction: PaymentTransaction, actions: List[RecoveryAction]) -> List[str]:
        violations = []
        retry_count = 0
        for action in actions:
            if action.action_type == "SMART_RETRY":
                retry_count += 1
                
        if retry_count > self.max_retries:
            violations.append(f"Exceeded max retries: {retry_count} > {self.max_retries}")
            
        return violations
