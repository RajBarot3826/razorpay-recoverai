import uuid
import random
import json
import datetime
from typing import List, Dict, Any
from backend.models.schemas import PaymentTransaction
from backend.simulator.scenarios import SCENARIOS_REGISTRY

class PaymentFailureSimulator:
    """Synthetic payment failure generator."""

    def __init__(self):
        self.methods = ["card", "upi", "netbanking", "wallet"]
        self.devices = ["mobile_app", "mobile_web", "desktop"]
        self.browsers = ["chrome", "safari", "firefox", "edge", "unknown"]
        self.locations = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow"]
        
        self.method_failure_weights = {
            "card": {
                "INSUFFICIENT_FUNDS": 0.30,
                "EXPIRED_CARD": 0.10,
                "INVALID_CARD": 0.05,
                "AUTHENTICATION_FAILED": 0.10,
                "NETWORK_ERROR": 0.03,
                "BANK_TIMEOUT": 0.05,
                "RISK_BLOCKED": 0.02,
                "LIMIT_EXCEEDED": 0.05,
                "UNKNOWN": 0.01
            },
            "upi": {
                "UPI_TIMEOUT": 0.15,
                "APP_NOT_RESPONDING": 0.08,
                "INCORRECT_PIN": 0.05,
                "INSUFFICIENT_FUNDS": 0.15,
                "NETWORK_ERROR": 0.03,
                "BANK_TIMEOUT": 0.04,
                "LIMIT_EXCEEDED": 0.05,
                "RISK_BLOCKED": 0.02,
                "UNKNOWN": 0.01
            },
            "netbanking": {
                "BANK_TIMEOUT": 0.07,
                "SESSION_EXPIRED": 0.05,
                "AUTHENTICATION_FAILED": 0.05,
                "NETWORK_ERROR": 0.02,
                "INSUFFICIENT_FUNDS": 0.05,
                "LIMIT_EXCEEDED": 0.05,
                "RISK_BLOCKED": 0.01,
                "UNKNOWN": 0.01
            },
            "wallet": {
                "INSUFFICIENT_FUNDS": 0.20,
                "NETWORK_ERROR": 0.02,
                "RISK_BLOCKED": 0.01,
                "AUTHENTICATION_FAILED": 0.05,
                "LIMIT_EXCEEDED": 0.05,
                "UNKNOWN": 0.01
            }
        }

    def _generate_amount(self) -> float:
        """Generate realistic amounts (₹100-₹50,000 right-skewed)."""
        amount = random.lognormvariate(6.5, 1.2)
        return round(min(max(amount, 100.0), 50000.0), 2)

    def _generate_timestamp(self) -> datetime.datetime:
        """Generate realistic timestamps (last 7 days)."""
        now = datetime.datetime.now(datetime.timezone.utc)
        days_ago = random.uniform(0, 7)
        return now - datetime.timedelta(days=days_ago)

    def _generate_metadata(self) -> Dict[str, Any]:
        """Generate realistic metadata."""
        return {
            "device": random.choice(self.devices),
            "browser": random.choice(self.browsers),
            "location": random.choice(self.locations),
            "attempt_count": random.choices([1, 2, 3, 4, 5], weights=[0.6, 0.25, 0.1, 0.04, 0.01])[0],
            "ip_address": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
        }
        
    def _create_transaction(self, method: str, failure_reason: str) -> PaymentTransaction:
        return PaymentTransaction(
            id=f"txn_{uuid.uuid4().hex[:16]}",
            amount=self._generate_amount(),
            currency="INR",
            method=method,
            status="failed",
            failure_reason=failure_reason,
            customer_id=f"cust_{random.randint(10000, 99999)}",
            merchant_id=f"merch_{random.randint(100, 999)}",
            timestamp=self._generate_timestamp(),
            metadata=self._generate_metadata()
        )

    def generate_batch(self, n: int) -> List[PaymentTransaction]:
        """Generates n failed transactions."""
        transactions = []
        for _ in range(n):
            method = random.choices(
                list(self.method_failure_weights.keys()),
                weights=[0.4, 0.4, 0.15, 0.05]
            )[0]
            
            reasons = list(self.method_failure_weights[method].keys())
            weights = list(self.method_failure_weights[method].values())
            
            failure_reason = random.choices(reasons, weights=weights)[0]
            transactions.append(self._create_transaction(method, failure_reason))
            
        return transactions

    def generate_with_recoverable_ratio(self, n: int, recoverable_pct: float = 0.65) -> List[PaymentTransaction]:
        """Generates transactions targeting a specific recoverable ratio."""
        recoverable_reasons = set([s.failure_type for s in SCENARIOS_REGISTRY if s.is_recoverable])
        unrecoverable_reasons = set([s.failure_type for s in SCENARIOS_REGISTRY if not s.is_recoverable])
        
        transactions = []
        for _ in range(n):
            method = random.choices(
                list(self.method_failure_weights.keys()),
                weights=[0.4, 0.4, 0.15, 0.05]
            )[0]
            
            method_reasons = set(self.method_failure_weights[method].keys())
            rec_reasons_for_method = list(method_reasons.intersection(recoverable_reasons))
            unrec_reasons_for_method = list(method_reasons.intersection(unrecoverable_reasons))
            
            is_rec = random.random() < recoverable_pct
            
            if is_rec and rec_reasons_for_method:
                failure_reason = random.choice(rec_reasons_for_method)
            elif not is_rec and unrec_reasons_for_method:
                failure_reason = random.choice(unrec_reasons_for_method)
            else:
                failure_reason = random.choice(list(method_reasons))
                
            transactions.append(self._create_transaction(method, failure_reason))
            
        return transactions

    def export_to_json(self, transactions: List[PaymentTransaction], filepath: str):
        """Export generated transactions to JSON for training data."""
        with open(filepath, 'w') as f:
            # Assuming model_dump is available (Pydantic v2)
            json.dump([t.model_dump(mode='json') for t in transactions], f, indent=2)
