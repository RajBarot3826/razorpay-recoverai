"""
Audit Trail Logger for RecoverAI.
Logs every AI decision with full context for compliance and explainability.
"""

import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from collections import defaultdict
import logging

from backend.models.schemas import AuditEntry

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Logs every agent decision with: who (agent), what (action),
    why (reasoning), when (timestamp), outcome, and compliance status.
    
    Stores in memory with optional DB persistence.
    """

    def __init__(self):
        # Store audit entries grouped by transaction_id for fast lookup
        self._trails: Dict[str, List[AuditEntry]] = defaultdict(list)

    def log(
        self,
        agent_name: str,
        action: str,
        reasoning: str,
        outcome: str = "",
        compliant: bool = True,
        transaction_id: str = "",
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditEntry:
        """
        Create and store an audit log entry.

        Args:
            agent_name: Which agent made the decision
            action: What action was taken (CLASSIFY, ANALYZE, EXECUTE, BLOCK, etc.)
            reasoning: Why the decision was made
            outcome: What happened as a result
            compliant: Whether the action passed compliance checks
            transaction_id: The transaction this entry belongs to
            details: Optional additional structured details
        
        Returns:
            The created AuditEntry
        """
        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc),
            agent_name=agent_name,
            action=action,
            reasoning=reasoning,
            outcome=outcome,
            compliance_check=compliant,
            details=details or {},
        )

        self._trails[transaction_id].append(entry)

        logger.info(
            f"AUDIT | {agent_name:20s} | {action:20s} | "
            f"txn={transaction_id} | compliant={compliant} | {outcome}"
        )
        return entry

    def get_trail(self, transaction_id: str) -> List[AuditEntry]:
        """Retrieve all audit entries for a transaction."""
        return self._trails.get(transaction_id, [])

    def get_all_trails(self) -> Dict[str, List[AuditEntry]]:
        """Get all audit trails."""
        return dict(self._trails)

    def export_trail(self, transaction_id: str, format: str = "json") -> str:
        """Export a transaction's audit trail as JSON string."""
        trail = self.get_trail(transaction_id)
        if format == "json":
            return json.dumps(
                [e.model_dump(mode="json") for e in trail], indent=2
            )
        return str(trail)

    def get_stats(self) -> Dict[str, Any]:
        """Get aggregate audit stats."""
        total_entries = sum(len(t) for t in self._trails.values())
        total_transactions = len(self._trails)
        compliant_count = sum(
            1
            for trail in self._trails.values()
            for e in trail
            if e.compliance_check
        )
        return {
            "total_entries": total_entries,
            "total_transactions": total_transactions,
            "compliant_entries": compliant_count,
            "non_compliant_entries": total_entries - compliant_count,
            "compliance_rate": (
                compliant_count / total_entries if total_entries > 0 else 1.0
            ),
        }
