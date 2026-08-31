import json
import logging
from typing import Dict, Any, Optional
import os

from backend.models.schemas import PaymentTransaction, FailureClassification, RootCauseAnalysis

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert payment failure analyst working for an Indian fintech company.
Analyze the failed payment transaction and provide a structured root cause analysis.

You must return a valid JSON object with exactly these fields:
{
  "root_cause": "A concise 1-sentence root cause",
  "explanation": "A detailed 2-3 sentence explanation of why this happened",
  "severity": "LOW|MEDIUM|HIGH|CRITICAL",
  "recommended_actions": ["action1", "action2", "action3"]
}

Severity guidelines:
- LOW: Transient issues (network timeout, bank server briefly down)
- MEDIUM: Customer-side issues (insufficient funds, wrong PIN)
- HIGH: Systemic issues (expired card, limit exceeded, repeated failures)
- CRITICAL: Risk/fraud flags (risk blocked, suspected fraud)

Consider Indian payment context: UPI, IMPS, NEFT, RuPay cards, net banking, salary cycles (1st and 28th), festival seasons.
"""

class RootCauseAnalyzer:
    def __init__(self, openai_api_key: Optional[str] = None, gemini_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        self.gemini_api_key = gemini_api_key or os.environ.get("GEMINI_API_KEY")
        self._openai_client = None
        self._gemini_model = None

        if self.openai_api_key:
            try:
                from openai import OpenAI
                self._openai_client = OpenAI(api_key=self.openai_api_key)
            except Exception:
                pass

        if self.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                self._gemini_model = genai.GenerativeModel("gemini-2.5-flash")
            except Exception:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=self.gemini_api_key)
                    self._gemini_model = genai.GenerativeModel("gemini-1.5-flash")
                except Exception:
                    pass

    async def analyze(self, transaction: PaymentTransaction, classification: FailureClassification) -> RootCauseAnalysis:
        user_prompt = self._build_user_prompt(transaction, classification)

        if self._openai_client:
            try:
                result = await self._analyze_openai(user_prompt, transaction, classification)
                if result:
                    return result
            except Exception:
                pass

        if self._gemini_model:
            try:
                result = await self._analyze_gemini(user_prompt, transaction, classification)
                if result:
                    return result
            except Exception:
                pass

        return self._rule_based_analysis(transaction, classification)

    def _build_user_prompt(self, transaction: PaymentTransaction, classification: FailureClassification) -> str:
        meta = transaction.metadata or {}
        return f"""Analyze this failed payment:

- Amount: INR {transaction.amount:,.2f}
- Method: {transaction.method}
- Failure Reason: {transaction.failure_reason}
- Classification: {classification.failure_type} (Confidence: {classification.confidence_score:.2f})
- Time of Day: {transaction.timestamp.strftime('%H:%M')} (Day {transaction.timestamp.day} of month)
- Attempt Count: {meta.get('attempt_count', 1)}
- Device: {meta.get('device', 'unknown')}
"""

    async def _analyze_openai(self, user_prompt: str, transaction: PaymentTransaction, classification: FailureClassification) -> Optional[RootCauseAnalysis]:
        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self._openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                max_tokens=300,
                temperature=0.2,
            ),
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        return RootCauseAnalysis(
            root_cause=data.get("root_cause", f"Payment failed: {classification.failure_type}"),
            explanation=data.get("explanation", ""),
            severity=data.get("severity", "MEDIUM"),
            recommended_actions=self._map_actions(data.get("recommended_actions", []), classification.failure_type),
            llm_model_used="gpt-4o-mini",
        )

    async def _analyze_gemini(self, user_prompt: str, transaction: PaymentTransaction, classification: FailureClassification) -> Optional[RootCauseAnalysis]:
        import asyncio
        loop = asyncio.get_event_loop()
        prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}\n\nReturn JSON ONLY:"
        response = await loop.run_in_executor(
            None,
            lambda: self._gemini_model.generate_content(prompt),
        )

        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        data = json.loads(text.strip())
        return RootCauseAnalysis(
            root_cause=data.get("root_cause", f"Payment failed: {classification.failure_type}"),
            explanation=data.get("explanation", ""),
            severity=data.get("severity", "MEDIUM"),
            recommended_actions=self._map_actions(data.get("recommended_actions", []), classification.failure_type),
            llm_model_used="gemini-2.5-flash",
        )

    def _map_actions(self, raw_actions: list, failure_type: str) -> list:
        from backend.models.schemas import ActionType
        actions = []
        for a in raw_actions:
            a_upper = str(a).upper().replace(" ", "_")
            for at in ActionType:
                if at.value in a_upper or a_upper in at.value:
                    if at not in actions:
                        actions.append(at)

        if not actions:
            rules = self._get_rule_actions(failure_type)
            actions = rules

        return actions

    def _get_rule_actions(self, failure_type: str) -> list:
        from backend.models.schemas import ActionType
        mapping = {
            "INSUFFICIENT_FUNDS": [ActionType.CUSTOMER_NUDGE, ActionType.SMART_RETRY],
            "BANK_TIMEOUT": [ActionType.SMART_RETRY],
            "UPI_TIMEOUT": [ActionType.SMART_RETRY, ActionType.CUSTOMER_NUDGE],
            "NETWORK_ERROR": [ActionType.SMART_RETRY],
            "INVALID_CARD": [ActionType.ALTERNATIVE_METHOD, ActionType.CUSTOMER_NUDGE],
            "EXPIRED_CARD": [ActionType.ALTERNATIVE_METHOD, ActionType.CUSTOMER_NUDGE],
            "AUTHENTICATION_FAILED": [ActionType.CUSTOMER_NUDGE, ActionType.SMART_RETRY],
            "INCORRECT_PIN": [ActionType.CUSTOMER_NUDGE],
            "LIMIT_EXCEEDED": [ActionType.ALTERNATIVE_METHOD, ActionType.CUSTOMER_NUDGE],
            "RISK_BLOCKED": [ActionType.ESCALATION],
            "APP_NOT_RESPONDING": [ActionType.SMART_RETRY],
            "SESSION_EXPIRED": [ActionType.CUSTOMER_NUDGE, ActionType.SMART_RETRY],
        }
        return mapping.get(failure_type, [ActionType.SMART_RETRY])

    def _rule_based_analysis(self, transaction: PaymentTransaction, classification: FailureClassification) -> RootCauseAnalysis:
        ft = classification.failure_type.value if hasattr(classification.failure_type, "value") else str(classification.failure_type)

        explanations = {
            "INSUFFICIENT_FUNDS": (
                "The bank declined the transaction due to non-sufficient funds (NSF). "
                "This is common around month-end when balances are low. "
                "Recovery via salary-day retry or nudge to add funds.",
                "MEDIUM",
            ),
            "BANK_TIMEOUT": (
                "The acquiring or issuing bank server did not respond within the timeout threshold. "
                "This is a transient infrastructure issue. Highly recoverable via exponential backoff retry.",
                "LOW",
            ),
            "UPI_TIMEOUT": (
                "The UPI collect request or intent flow timed out before the customer could approve in their UPI app. "
                "Usually caused by notification delivery delays or customer distraction.",
                "LOW",
            ),
            "NETWORK_ERROR": (
                "A network transport error occurred between the payment gateway and the banking switch. "
                "Transient issue, recommended immediate retry.",
                "LOW",
            ),
            "EXPIRED_CARD": (
                "The card used for payment has passed its expiration date. "
                "Retrying the same card will not work. Customer must provide updated card or alternate payment method.",
                "HIGH",
            ),
            "INVALID_CARD": (
                "Card number, CVV, or expiry was entered incorrectly or the card is not enabled for online transactions. "
                "Customer action required.",
                "MEDIUM",
            ),
            "AUTHENTICATION_FAILED": (
                "3D Secure OTP verification failed or OTP was not entered before expiry. "
                "Customer was likely distracted or OTP delivery was delayed.",
                "MEDIUM",
            ),
            "INCORRECT_PIN": (
                "Customer entered an incorrect UPI PIN or ATM PIN. "
                "Nudge customer to retry with correct credentials.",
                "MEDIUM",
            ),
            "LIMIT_EXCEEDED": (
                "Transaction amount exceeds daily or per-transaction limit set by bank or card issuer. "
                "Suggest splitting payment or using an alternate method.",
                "HIGH",
            ),
            "RISK_BLOCKED": (
                "Transaction was flagged and blocked by automated fraud/risk rules. "
                "Do not auto-retry. Requires manual review or customer identity verification.",
                "CRITICAL",
            ),
            "APP_NOT_RESPONDING": (
                "The customer's UPI or banking application crashed or failed to return a callback. "
                "Transient client-side issue.",
                "LOW",
            ),
            "SESSION_EXPIRED": (
                "The checkout session timed out before payment completion. "
                "Nudge customer with a pre-filled checkout link.",
                "LOW",
            ),
        }

        exp, sev = explanations.get(
            ft,
            ("Payment failed due to an unspecified gateway error. Standard retry recommended.", "MEDIUM")
        )

        return RootCauseAnalysis(
            root_cause=f"Payment failed due to {ft.replace('_', ' ').lower()}.",
            explanation=exp,
            severity=sev,
            recommended_actions=self._get_rule_actions(ft),
            llm_model_used="rule-engine-fallback",
        )
