import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from collections import defaultdict
import logging

from backend.models.schemas import AuditEntry

logger = logging.getLogger(__name__)

class AuditLogger:
    def __init__(self):
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
        entry = AuditEntry(
            id=f"aud_{int(datetime.now(timezone.utc).timestamp()*1000)}",
            transaction_id=transaction_id,
            timestamp=datetime.now(timezone.utc),
            agent_name=agent_name,
            action=action,
            details=details or {"reasoning": reasoning, "compliant": compliant},
            outcome=outcome,
        )

        self._trails[transaction_id].append(entry)
        return entry

    def get_trail(self, transaction_id: str) -> List[AuditEntry]:
        return self._trails.get(transaction_id, [])

    def get_all_trails(self) -> Dict[str, List[AuditEntry]]:
        return dict(self._trails)

    def export_trail(self, transaction_id: str, format: str = "json") -> str:
        trail = self.get_trail(transaction_id)
        if format == "json":
            return json.dumps(
                [e.model_dump(mode="json") for e in trail], indent=2
            )
        return str(trail)

    def get_stats(self) -> Dict[str, Any]:
        total_entries = sum(len(t) for t in self._trails.values())
        total_transactions = len(self._trails)
        compliant_count = sum(
            1
            for trail in self._trails.values()
            for e in trail
            if e.details.get("compliant", True)
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
