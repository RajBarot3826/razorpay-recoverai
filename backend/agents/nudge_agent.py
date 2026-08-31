import logging
import random
from datetime import datetime, timezone
from typing import Optional

from backend.models.schemas import PaymentTransaction, FailureClassification, RecoveryAction
from backend.compliance.guardrails import ComplianceGuardrails

logger = logging.getLogger(__name__)

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
            "Hi {name}, your payment of Rs {amount} was not completed. Please click here to retry with an alternate payment method.",
        ],
        "hindi": [
            "नमस्ते {name}, आपका ₹{amount} का भुगतान पूरा नहीं हो सका। कृपया पुनः प्रयास करें।",
        ],
    },
}

class CustomerNudgeAgent:
    def __init__(self, guardrails: ComplianceGuardrails = None):
        self.guardrails = guardrails or ComplianceGuardrails()

    async def generate_nudge(
        self,
        transaction: PaymentTransaction,
        classification: FailureClassification,
        language: str = "hinglish",
        channel: str = "whatsapp",
    ) -> RecoveryAction:
        proposed_action = RecoveryAction(
            id=f"nudge_{int(datetime.now(timezone.utc).timestamp()*1000)}",
            action_type="CUSTOMER_NUDGE",
            status="PENDING",
            details={"channel": channel, "language": language},
        )

        allowed, reason = self.guardrails.check(transaction, proposed_action)
        if not allowed:
            proposed_action.status = "BLOCKED"
            proposed_action.outcome = f"Blocked: {reason}"
            return proposed_action

        failure_type = str(classification.failure_type).upper()
        ft_templates = TEMPLATES.get(failure_type, TEMPLATES["DEFAULT"])
        lang_templates = ft_templates.get(language.lower(), ft_templates.get("hinglish", TEMPLATES["DEFAULT"]["hinglish"]))

        template = random.choice(lang_templates) if lang_templates else TEMPLATES["DEFAULT"]["english"][0]
        customer_name = transaction.metadata.get("customer_name", "Customer") if transaction.metadata else "Customer"
        
        message = template.format(
            name=customer_name,
            amount=f"{transaction.amount:,.2f}",
        )

        proposed_action.details = {
            "channel": channel,
            "language": language,
            "recipient": customer_name,
            "message": message,
        }
        proposed_action.status = "COMPLETED"
        proposed_action.outcome = message

        return proposed_action
