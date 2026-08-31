from dataclasses import dataclass
from typing import List, Optional

@dataclass
class FailureScenario:
    name: str
    failure_type: str
    payment_methods: List[str]
    probability: float
    is_recoverable: bool
    typical_recovery_actions: List[str]
    description: str

SCENARIOS_REGISTRY = [
    FailureScenario(
        name="Insufficient Funds",
        failure_type="INSUFFICIENT_FUNDS",
        payment_methods=["card", "upi", "netbanking", "wallet"],
        probability=0.30,
        is_recoverable=True,
        typical_recovery_actions=["Send notification to top up", "Offer alternative payment method"],
        description="The customer's bank account or credit card does not have sufficient funds."
    ),
    FailureScenario(
        name="Bank Server Down",
        failure_type="BANK_TIMEOUT",
        payment_methods=["netbanking", "upi", "card"],
        probability=0.07,
        is_recoverable=True,
        typical_recovery_actions=["Retry payment after 15-30 minutes", "Notify user to try again later"],
        description="The acquiring or issuing bank's servers are down or unresponsive."
    ),
    FailureScenario(
        name="Invalid Card",
        failure_type="INVALID_CARD",
        payment_methods=["card"],
        probability=0.05,
        is_recoverable=False,
        typical_recovery_actions=["Prompt user to enter correct card details"],
        description="The card details (number, CVV) entered are incorrect."
    ),
    FailureScenario(
        name="UPI Timeout",
        failure_type="UPI_TIMEOUT",
        payment_methods=["upi"],
        probability=0.15,
        is_recoverable=True,
        typical_recovery_actions=["Ask user to check UPI app", "Retry payment prompt"],
        description="UPI app did not respond in time or request expired."
    ),
    FailureScenario(
        name="Network Error",
        failure_type="NETWORK_ERROR",
        payment_methods=["card", "upi", "netbanking", "wallet"],
        probability=0.03,
        is_recoverable=True,
        typical_recovery_actions=["Silent automatic retry", "Prompt user to check internet and retry"],
        description="A network dropout occurred during the transaction."
    ),
    FailureScenario(
        name="Authentication Failed",
        failure_type="AUTHENTICATION_FAILED",
        payment_methods=["card", "upi", "netbanking"],
        probability=0.10,
        is_recoverable=True,
        typical_recovery_actions=["Prompt user to re-enter OTP or PIN"],
        description="The user entered an incorrect OTP or PIN."
    ),
    FailureScenario(
        name="Risk Blocked",
        failure_type="RISK_BLOCKED",
        payment_methods=["card", "upi", "netbanking", "wallet"],
        probability=0.02,
        is_recoverable=False,
        typical_recovery_actions=["Request manual review", "Block user from further attempts temporarily"],
        description="Transaction blocked due to high fraud risk score."
    ),
    FailureScenario(
        name="Expired Card",
        failure_type="EXPIRED_CARD",
        payment_methods=["card"],
        probability=0.10,
        is_recoverable=False,
        typical_recovery_actions=["Prompt user to use a different card"],
        description="The credit or debit card used has expired."
    ),
    FailureScenario(
        name="Limit Exceeded",
        failure_type="LIMIT_EXCEEDED",
        payment_methods=["card", "upi", "netbanking", "wallet"],
        probability=0.05,
        is_recoverable=True,
        typical_recovery_actions=["Suggest lower amount", "Suggest alternative payment method"],
        description="Transaction exceeds the daily limit set by the user or bank."
    ),
    FailureScenario(
        name="App Not Responding",
        failure_type="APP_NOT_RESPONDING",
        payment_methods=["upi"],
        probability=0.08,
        is_recoverable=True,
        typical_recovery_actions=["Ask user to retry from app", "Suggest other UPI app"],
        description="The UPI application is stuck or unresponsive."
    ),
    FailureScenario(
        name="Session Expired",
        failure_type="SESSION_EXPIRED",
        payment_methods=["netbanking"],
        probability=0.05,
        is_recoverable=True,
        typical_recovery_actions=["Prompt user to restart transaction"],
        description="The netbanking session timed out."
    ),
    FailureScenario(
        name="Incorrect PIN",
        failure_type="INCORRECT_PIN",
        payment_methods=["upi"],
        probability=0.05,
        is_recoverable=True,
        typical_recovery_actions=["Prompt user to re-enter PIN carefully"],
        description="The user entered an incorrect UPI PIN."
    ),
    FailureScenario(
        name="Unknown",
        failure_type="UNKNOWN",
        payment_methods=["card", "upi", "netbanking", "wallet"],
        probability=0.01,
        is_recoverable=False,
        typical_recovery_actions=["Check with support"],
        description="An unknown error occurred."
    )
]

def get_scenario(failure_type: str) -> Optional[FailureScenario]:
    """Retrieve a failure scenario by its type."""
    for scenario in SCENARIOS_REGISTRY:
        if scenario.failure_type == failure_type:
            return scenario
    return None

def get_recoverable_scenarios() -> List[FailureScenario]:
    """Retrieve all recoverable failure scenarios."""
    return [s for s in SCENARIOS_REGISTRY if s.is_recoverable]
