"""
Customer Nudge Agent for RecoverAI.
Generates personalized recovery messages in English and Hinglish
with proper channel selection (SMS, WhatsApp, Push, Email).
"""

import logging
import random
from datetime import datetime, timezone
from typing import Optional

from backend.models.schemas import PaymentTransaction, FailureClassification, RecoveryAction
from backend.compliance.guardrails import ComplianceGuardrails

logger = logging.getLogger(__name__)

# Hinglish nudge templates by failure type
TEMPLATES = {
    "INSUFFICIENT_FUNDS": {
        "hinglish": [
            "Hi {name}, aapka Rs {amount} ka payment insufficient balance ki wajah se fail ho gaya. Funds add karke retry karein! 💳",
            "Namaste {name}! Lagta hai balance thoda kam hai. Rs {amount} ke liye funds add karein aur payment complete karein. 🙏",
            "{name} ji, payment Rs {amount} fail hua - balance low hai. Jab funds aa jayein tab retry kar lena! Aasaan hai. 💰",
        ],
        "english": [
            "Hi {name}, your payment of Rs {amount} failed due to insufficient balance. Please add funds and try again.",
            "Your Rs {amount} transaction couldn't go through. Please ensure sufficient balance and retry.",
        ],
    },
    "EXPIRED_CARD": {
        "hinglish": [
            "Hi {name}, aapka card expire ho chuka hai. Naya card add karein ya UPI se Rs {amount} pay karein! 🔄",
            "{name} ji, card ki validity khatam ho gayi. UPI ya naye card se payment complete karein. 📱",
        ],
        "english": [
            "Hi {name}, your card has expired. Please update your card or try UPI to complete the Rs {amount} payment.",
        ],
    },
    "NETWORK_ERROR": {
        "hinglish": [
            "Hi {name}, network issue ki wajah se payment fail hua. Abhi dobara try karein - chances ache hain! 🔄",
            "{name} ji, chhoti si network problem thi. 2 min mein retry karein, ho jayega! ✅",
        ],
        "english": [
            "Hi {name}, your payment failed due to a temporary network issue. Please try again now.",
        ],
    },
    "AUTHENTICATION_FAILED": {
        "hinglish": [
            "Hi {name}, OTP ya PIN galat ho gaya tha. Dhyan se enter karein aur Rs {amount} ka payment complete karein! 🔐",
            "{name} ji, authentication fail hua. Sahi OTP/PIN daalke retry karein. Easy hai! 👍",
        ],
        "english": [
            "Hi {name}, authentication failed. Please re-enter your OTP/PIN carefully to complete the Rs {amount} payment.",
        ],
    },
    "DEFAULT": {
        "hinglish": [
            "Hi {name}, aapka Rs {amount} ka payment fail ho gaya. Kripya dobara try karein. 🙏",
            "{name} ji, payment process nahi ho paya. Ek aur baar try karein ya doosra method use karein! 💳",
        ],
        "english": [
            "Hi {name}, your payment of Rs {amount} could not be processed. Please try again or use an alternative method.",
        ],
    },
}

# Channel selection based on amount and failure type
CHANNEL_PRIORITY = {
    "high_value": ["whatsapp", "sms", "email"],      # > Rs 5000
    "medium_value": ["sms", "whatsapp", "push"],      # Rs 500-5000
    "low_value": ["push", "sms"],                      # < Rs 500
}


class CustomerNudgeAgent:
    """
    Generates personalized recovery messages in English and Hinglish.
    Selects optimal communication channel based on transaction context.
    """

    def __init__(self, guardrails: ComplianceGuardrails = None):
        self.guardrails = guardrails or ComplianceGuardrails()

    def _select_channel(self, transaction: PaymentTransaction) -> str:
        """Select communication channel based on transaction value."""
        if transaction.amount > 5000:
            return random.choice(CHANNEL_PRIORITY["high_value"])
        elif transaction.amount > 500:
            return random.choice(CHANNEL_PRIORITY["medium_value"])
        else:
            return random.choice(CHANNEL_PRIORITY["low_value"])

    def _generate_message(
        self, transaction: PaymentTransaction, failure_type: str, language: str = "hinglish"
    ) -> str:
        """Generate a personalized nudge message."""
        # Find matching template category
        template_key = "DEFAULT"
        for key in TEMPLATES:
            if key in failure_type.upper():
                template_key = key
                break

        templates = TEMPLATES[template_key].get(language, TEMPLATES[template_key].get("hinglish", []))
        if not templates:
            templates = TEMPLATES["DEFAULT"]["hinglish"]

        template = random.choice(templates)

        # Extract customer name (in real system, would look up from DB)
        customer_name = f"Customer-{transaction.customer_id[-4:]}" if transaction.customer_id else "Customer"

        return template.format(
            name=customer_name,
            amount=f"{transaction.amount:,.2f}",
            currency=transaction.currency,
        )

    async def generate_nudge(
        self,
        transaction: PaymentTransaction,
        classification: FailureClassification,
        language: str = "hinglish",
    ) -> RecoveryAction:
        """Generate a personalized nudge message with channel selection."""
        proposed_action = RecoveryAction(
            id=f"nudge_{int(datetime.now(timezone.utc).timestamp() * 1000)}",
            transaction_id=transaction.id,
            action_type="CUSTOMER_NUDGE",
            status="PENDING",
            details="Generating nudge...",
            created_at=datetime.now(timezone.utc),
        )

        # Compliance check
        allowed, reason = self.guardrails.check(transaction, proposed_action)
        if not allowed:
            proposed_action.status = "BLOCKED"
            proposed_action.outcome = f"Blocked by guardrails: {reason}"
            proposed_action.completed_at = datetime.now(timezone.utc)
            return proposed_action

        # Generate message and select channel
        failure_type = str(classification.failure_type)
        channel = self._select_channel(transaction)
        message = self._generate_message(transaction, failure_type, language)

        proposed_action.status = "COMPLETED"
        proposed_action.details = {
            "channel": channel,
            "language": language,
            "message": message,
            "failure_type": failure_type,
        }
        proposed_action.outcome = f"Nudge queued via {channel.upper()}"
        proposed_action.completed_at = datetime.now(timezone.utc)

        return proposed_action
