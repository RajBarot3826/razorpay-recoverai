import logging
from datetime import datetime, timezone
from typing import Tuple, List

from backend.models.schemas import PaymentTransaction, RecoveryAction

logger = logging.getLogger(__name__)

class ComplianceGuardrails:
    def __init__(self):
        self.max_retries = 3
        self.quiet_hours_start = 21
        self.quiet_hours_end = 8
        self.amount_threshold_for_escalation = 10000.0

    def check(self, transaction: PaymentTransaction, proposed_action: RecoveryAction) -> Tuple[bool, str]:
        action_type = proposed_action.action_type.value if hasattr(proposed_action.action_type, "value") else str(proposed_action.action_type).upper()
        failure_reason = str(transaction.failure_reason or "").upper()
        
        if "RISK" in failure_reason and "RETRY" in action_type:
            return False, "Cannot retry risk-blocked transactions."

        if "NUDGE" in action_type:
            now_hour = datetime.now(timezone.utc).hour
            if now_hour >= self.quiet_hours_start or now_hour < self.quiet_hours_end:
                return False, f"Cannot nudge during quiet hours (21:00 - 08:00). Current hour: {now_hour}"

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
