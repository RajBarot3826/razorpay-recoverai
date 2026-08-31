import logging
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

from backend.models.schemas import (
    PaymentTransaction,
    RecoveryResult,
    RecoveryMetrics,
    FailureClassification,
    RootCauseAnalysis,
    RecoveryAction,
    AuditEntry,
)
from backend.agents.classifier import FailureClassifier
from backend.agents.root_cause import RootCauseAnalyzer
from backend.agents.strategy_engine import RecoveryStrategyEngine
from backend.agents.retry_agent import SmartRetryAgent
from backend.agents.nudge_agent import CustomerNudgeAgent
from backend.agents.alternative_agent import AlternativePaymentAgent
from backend.agents.escalation_agent import EscalationAgent
from backend.compliance.guardrails import ComplianceGuardrails
from backend.compliance.audit import AuditLogger
from backend.pipeline.metrics import MetricsCollector

logger = logging.getLogger(__name__)

RECOVERY_PROBABILITY = {
    "INSUFFICIENT_FUNDS": 0.45,
    "BANK_TIMEOUT": 0.80,
    "UPI_TIMEOUT": 0.75,
    "NETWORK_ERROR": 0.85,
    "AUTHENTICATION_FAILED": 0.55,
    "APP_NOT_RESPONDING": 0.70,
    "INCORRECT_PIN": 0.60,
    "SESSION_EXPIRED": 0.65,
    "LIMIT_EXCEEDED": 0.30,
    "EXPIRED_CARD": 0.20,
    "INVALID_CARD": 0.10,
    "RISK_BLOCKED": 0.00,
    "UNKNOWN": 0.25,
}

class RecoveryPipeline:
    def __init__(self):
        self.classifier = FailureClassifier()
        self.root_cause_analyzer = RootCauseAnalyzer()
        self.strategy_engine = RecoveryStrategyEngine()

        self.guardrails = ComplianceGuardrails()
        self.retry_agent = SmartRetryAgent(guardrails=self.guardrails)
        self.nudge_agent = CustomerNudgeAgent(guardrails=self.guardrails)
        self.alt_payment_agent = AlternativePaymentAgent()
        self.escalation_agent = EscalationAgent()

        self.audit_logger = AuditLogger()
        self.metrics = MetricsCollector()

        self.results_store: Dict[str, RecoveryResult] = {}

    async def process_single(self, transaction: PaymentTransaction) -> RecoveryResult:
        transaction_id = transaction.id

        result = RecoveryResult(
            transaction_id=transaction_id,
            original_amount=transaction.amount,
            failure_type="UNKNOWN",
            confidence_score=0.0,
            root_cause="Analysis pending",
            actions_taken=[],
            audit_trail=[],
            success=False,
        )

        try:
            classification = self.classifier.classify(transaction)
            ft = classification.failure_type.value if hasattr(classification.failure_type, "value") else str(classification.failure_type)
            result.failure_type = ft
            result.confidence_score = classification.confidence_score
            self.audit_logger.log(
                agent_name="FailureClassifier",
                action="CLASSIFY",
                reasoning=f"Classified as {ft} with {classification.confidence_score:.2f} confidence",
                outcome="success",
                compliant=True,
                transaction_id=transaction_id,
            )

            root_cause = await self.root_cause_analyzer.analyze(transaction, classification)
            result.root_cause = root_cause.explanation
            sev = root_cause.severity.value if hasattr(root_cause.severity, "value") else str(root_cause.severity)
            self.audit_logger.log(
                agent_name="RootCauseAnalyzer",
                action="ANALYZE",
                reasoning=root_cause.explanation,
                outcome=f"severity={sev}",
                compliant=True,
                transaction_id=transaction_id,
            )

            actions = await self.strategy_engine.decide_strategy(root_cause, transaction.amount)
            self.audit_logger.log(
                agent_name="StrategyEngine",
                action="DECIDE_STRATEGY",
                reasoning=f"Generated {len(actions)} recovery action(s)",
                outcome=actions[0].action_type if actions else "none",
                compliant=True,
                transaction_id=transaction_id,
            )

            execution_success = False
            for action in actions:
                is_compliant, compliance_reason = self.guardrails.check(transaction, action)
                if not is_compliant:
                    self.audit_logger.log(
                        agent_name="ComplianceGuardrails",
                        action="BLOCK",
                        reasoning=compliance_reason,
                        outcome="blocked",
                        compliant=False,
                        transaction_id=transaction_id,
                    )
                    action.status = "BLOCKED"
                    action.outcome = f"Blocked: {compliance_reason}"
                    result.actions_taken.append(action)
                    continue

                action_type = str(action.action_type).upper()
                executed_action = None

                if "RETRY" in action_type:
                    executed_action = await self.retry_agent.execute(transaction, classification)
                elif "NUDGE" in action_type:
                    executed_action = await self.nudge_agent.generate_nudge(transaction, classification)
                elif "ALTERNATIVE" in action_type:
                    executed_action = await self.alt_payment_agent.suggest_alternative(transaction, classification)
                elif "ESCALATION" in action_type:
                    executed_action = await self.escalation_agent.evaluate_escalation(
                        transaction, classification, result.actions_taken
                    )

                if executed_action:
                    result.actions_taken.append(executed_action)
                    
                    failure_key = str(result.failure_type or "UNKNOWN").upper()
                    success_prob = RECOVERY_PROBABILITY.get(failure_key, 0.25)
                    
                    status = str(executed_action.status).upper()
                    if status in ("BLOCKED", "SKIPPED", "FAILED"):
                        pass
                    elif status in ("SUCCESS", "COMPLETED", "SCHEDULED"):
                        if random.random() < success_prob:
                            execution_success = True
                            executed_action.outcome = (
                                f"Recovery successful (prob={success_prob:.0%}). "
                                + (executed_action.outcome or "")
                            )
                        else:
                            executed_action.outcome = (
                                f"Recovery attempted but failed (prob={success_prob:.0%}). "
                                + (executed_action.outcome or "")
                            )

                    self.audit_logger.log(
                        agent_name=f"{action_type}Agent",
                        action="EXECUTE",
                        reasoning=str(executed_action.details),
                        outcome=executed_action.outcome or str(executed_action.status),
                        compliant=True,
                        transaction_id=transaction_id,
                    )

            result.success = execution_success

        except Exception as e:
            logger.error(f"Error processing transaction {transaction_id}: {str(e)}")
            result.success = False
            self.audit_logger.log(
                agent_name="RecoveryPipeline",
                action="ERROR",
                reasoning=str(e),
                outcome="pipeline_error",
                compliant=True,
                transaction_id=transaction_id,
            )

        result.audit_trail = self.audit_logger.get_trail(transaction_id)
        self.metrics.record(result)
        self.results_store[transaction_id] = result

        return result

    async def process_batch(self, transactions: List[PaymentTransaction]) -> List[RecoveryResult]:
        results = []
        for tx in transactions:
            try:
                res = await self.process_single(tx)
                results.append(res)
            except Exception as e:
                logger.error(f"Batch processing error for {tx.id}: {str(e)}")
                err_res = RecoveryResult(
                    transaction_id=tx.id,
                    original_amount=tx.amount,
                    failure_type="UNKNOWN",
                    confidence_score=0.0,
                    root_cause=str(e),
                    actions_taken=[],
                    audit_trail=[],
                    success=False,
                )
                self.results_store[tx.id] = err_res
                results.append(err_res)
        return results

    def get_metrics(self) -> RecoveryMetrics:
        return self.metrics.get_summary()

    def get_before_after_comparison(self) -> Dict[str, Any]:
        return self.metrics.get_before_after()

    def get_transaction_result(self, transaction_id: str) -> Optional[RecoveryResult]:
        return self.results_store.get(transaction_id)
