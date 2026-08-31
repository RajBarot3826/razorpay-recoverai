"""
LLM-powered Root Cause Analyzer for RecoverAI.
Uses OpenAI GPT-4 or Google Gemini to analyze payment failures
and produce structured root cause analysis. Falls back to
rule-based analysis if API keys are unavailable.
"""

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
    """
    LLM-powered Root Cause Analyzer for payment failures.
    Uses OpenAI (primary) or Google Gemini (fallback) to analyze
    the transaction and failure features.
    Falls back to rule-based analysis when no API keys are available.
    """

    def __init__(self, openai_api_key: Optional[str] = None, gemini_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        self.gemini_api_key = gemini_api_key or os.environ.get("GEMINI_API_KEY")
        self._openai_client = None
        self._gemini_model = None

        # Initialize OpenAI client if available
        if self.openai_api_key:
            try:
                from openai import OpenAI
                self._openai_client = OpenAI(api_key=self.openai_api_key)
                logger.info("RootCauseAnalyzer: OpenAI client initialized")
            except Exception as e:
                logger.warning(f"Failed to init OpenAI: {e}")

        # Initialize Gemini client if available
        if self.gemini_api_key and not self._openai_client:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                self._gemini_model = genai.GenerativeModel("gemini-1.5-flash")
                logger.info("RootCauseAnalyzer: Gemini client initialized")
            except Exception as e:
                logger.warning(f"Failed to init Gemini: {e}")

    async def analyze(self, transaction: PaymentTransaction, classification: FailureClassification) -> RootCauseAnalysis:
        """Analyze a failed transaction using LLM or rule-based fallback."""
        user_prompt = self._build_user_prompt(transaction, classification)

        # Try OpenAI first
        if self._openai_client:
            try:
                result = await self._analyze_openai(user_prompt, transaction, classification)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"OpenAI analysis failed: {e}")

        # Try Gemini
        if self._gemini_model:
            try:
                result = await self._analyze_gemini(user_prompt, transaction, classification)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"Gemini analysis failed: {e}")

        # Fallback to rule-based
        logger.info("Using rule-based fallback for root cause analysis")
        return self._rule_based_analysis(transaction, classification)

    def _build_user_prompt(self, transaction: PaymentTransaction, classification: FailureClassification) -> str:
        meta = transaction.metadata or {}
        return f"""Analyze this failed payment:

Transaction ID: {transaction.id}
Amount: {transaction.currency} {transaction.amount:,.2f}
Payment Method: {transaction.method}
Failure Reason: {transaction.failure_reason}
ML Classification: {classification.failure_type} (confidence: {classification.confidence:.2f})
Device: {meta.get('device', 'unknown')}
Location: {meta.get('location', 'unknown')}
Attempt Count: {meta.get('attempt_count', 1)}
Time: {transaction.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC') if transaction.timestamp else 'unknown'}

Provide root cause analysis as JSON."""

    async def _analyze_openai(self, user_prompt: str, transaction: PaymentTransaction, classification: FailureClassification) -> Optional[RootCauseAnalysis]:
        """Use OpenAI GPT-4 for analysis."""
        import asyncio

        def _call():
            response = self._openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=500,
            )
            return response.choices[0].message.content

        loop = asyncio.get_event_loop()
        raw = await loop.run_in_executor(None, _call)
        return self._parse_llm_response(raw, transaction.id)

    async def _analyze_gemini(self, user_prompt: str, transaction: PaymentTransaction, classification: FailureClassification) -> Optional[RootCauseAnalysis]:
        """Use Google Gemini for analysis."""
        import asyncio

        def _call():
            response = self._gemini_model.generate_content(
                f"{SYSTEM_PROMPT}\n\n{user_prompt}",
                generation_config={"temperature": 0.3, "max_output_tokens": 500},
            )
            return response.text

        loop = asyncio.get_event_loop()
        raw = await loop.run_in_executor(None, _call)
        return self._parse_llm_response(raw, transaction.id)

    def _parse_llm_response(self, raw: str, transaction_id: str) -> Optional[RootCauseAnalysis]:
        """Parse LLM JSON response into RootCauseAnalysis."""
        try:
            # Handle markdown code blocks
            text = raw.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
                text = text.rsplit("```", 1)[0]

            data = json.loads(text)
            return RootCauseAnalysis(
                transaction_id=transaction_id,
                root_cause=data.get("root_cause", "Unknown"),
                explanation=data.get("explanation", "Unable to determine"),
                severity=data.get("severity", "MEDIUM"),
                recommended_actions=data.get("recommended_actions", []),
            )
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse LLM response: {e}")
            return None

    def _rule_based_analysis(self, transaction: PaymentTransaction, classification: FailureClassification) -> RootCauseAnalysis:
        """Deterministic rule-based fallback for root cause analysis."""
        failure_type = str(classification.failure_type).upper() if classification.failure_type else ""

        # Default values
        severity = "MEDIUM"
        root_cause = f"Payment failure: {transaction.failure_reason}"
        explanation = "Transaction failed for unclassified reasons."
        recommendations = ["Suggest alternative payment method"]

        if "INSUFFICIENT_FUNDS" in failure_type:
            severity = "LOW"
            root_cause = "Customer lacks sufficient funds in their account."
            explanation = (
                "The bank declined the transaction due to non-sufficient funds (NSF). "
                "This is common around month-end when balances are low. "
                "Recovery via salary-day retry or nudge to add funds."
            )
            recommendations = [
                "Nudge customer to add funds",
                "Retry on next salary day (1st or 28th of month)",
                "Suggest smaller partial payment option",
            ]
        elif "RISK" in failure_type or "FRAUD" in failure_type:
            severity = "CRITICAL"
            root_cause = "Transaction flagged by risk management system."
            explanation = (
                "High risk indicators were detected. This could be unusual transaction "
                "pattern, location mismatch, or suspicious device. Do NOT retry automatically."
            )
            recommendations = [
                "Escalate to human review immediately",
                "Do not retry automatically",
                "Verify customer identity if they contact support",
            ]
        elif "NETWORK" in failure_type or "TIMEOUT" in failure_type:
            severity = "LOW"
            root_cause = "Network timeout or gateway downtime."
            explanation = (
                "The acquiring bank or payment gateway did not respond in time. "
                "This is typically a transient issue that resolves within minutes."
            )
            recommendations = [
                "Retry after 15 minutes",
                "Try routing through alternative gateway",
                "Check bank status page for outages",
            ]
        elif "EXPIRED" in failure_type:
            severity = "MEDIUM"
            root_cause = "Payment card has expired."
            explanation = (
                "The credit/debit card used has passed its expiry date. "
                "Customer needs to use a different card or payment method."
            )
            recommendations = [
                "Nudge customer to update card details",
                "Suggest UPI as alternative (higher success rate in India)",
            ]
        elif "INVALID_CARD" in failure_type:
            severity = "MEDIUM"
            root_cause = "Invalid card details entered."
            explanation = (
                "The card number, CVV, or expiry date entered is incorrect. "
                "Customer may have mistyped or is using a cancelled card."
            )
            recommendations = [
                "Prompt user to re-enter card details carefully",
                "Suggest saved card or UPI payment",
            ]
        elif "AUTHENTICATION" in failure_type or "PIN" in failure_type:
            severity = "LOW"
            root_cause = "Authentication failure (wrong OTP or PIN)."
            explanation = (
                "The customer entered an incorrect OTP or UPI PIN. "
                "This is common and usually resolves on retry."
            )
            recommendations = [
                "Prompt user to re-enter OTP/PIN carefully",
                "Ensure SMS delivery is not delayed",
            ]
        elif "LIMIT" in failure_type:
            severity = "MEDIUM"
            root_cause = "Transaction amount exceeds daily/per-transaction limit."
            explanation = (
                "The bank has set a limit on transaction amount that was exceeded. "
                "Customer may need to increase their limit via bank app."
            )
            recommendations = [
                "Suggest splitting into smaller payments",
                "Suggest alternative payment method with higher limit",
                "Guide customer to increase bank limit via mobile banking",
            ]
        elif "APP_NOT_RESPONDING" in failure_type or "SESSION" in failure_type:
            severity = "LOW"
            root_cause = "Payment app or banking session issue."
            explanation = (
                "The UPI app or net banking session experienced a timeout or crash. "
                "Typically resolves by restarting the app or session."
            )
            recommendations = [
                "Ask user to restart payment app",
                "Retry in 5-10 minutes",
            ]

        return RootCauseAnalysis(
            transaction_id=transaction.id,
            root_cause=root_cause,
            explanation=explanation,
            severity=severity,
            recommended_actions=recommendations,
        )
