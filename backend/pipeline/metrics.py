from typing import Dict, List, Any
from backend.models.schemas import RecoveryResult, RecoveryMetrics

class MetricsCollector:
    """
    Collects and aggregates metrics for the recovery pipeline.
    """
    def __init__(self):
        self.total_processed = 0
        self.total_recovered = 0
        self.total_failed = 0
        self.total_revenue_recovered = 0.0
        self.by_failure_type: Dict[str, Dict[str, int]] = {}
        self.by_action_type: Dict[str, Dict[str, int]] = {}
        
    def record(self, result: RecoveryResult):
        """
        Record a single recovery result into metrics.
        """
        self.total_processed += 1
        is_success = result.success
        
        if is_success:
            self.total_recovered += 1
            if result.original_transaction and result.original_transaction.amount:
                self.total_revenue_recovered += result.original_transaction.amount
        else:
            self.total_failed += 1
            
        # By failure type
        if result.failure_type:
            if result.failure_type not in self.by_failure_type:
                self.by_failure_type[result.failure_type] = {"processed": 0, "recovered": 0}
            self.by_failure_type[result.failure_type]["processed"] += 1
            if is_success:
                self.by_failure_type[result.failure_type]["recovered"] += 1
                
        # By action type
        if result.executed_action:
            action = result.executed_action.action_type
            if action not in self.by_action_type:
                self.by_action_type[action] = {"processed": 0, "recovered": 0}
            self.by_action_type[action]["processed"] += 1
            if is_success:
                self.by_action_type[action]["recovered"] += 1

    def get_summary(self) -> RecoveryMetrics:
        """
        Get aggregated recovery metrics.
        """
        recovery_rate = (self.total_recovered / self.total_processed) if self.total_processed > 0 else 0.0
        return RecoveryMetrics(
            total_processed=self.total_processed,
            total_recovered=self.total_recovered,
            total_failed=self.total_failed,
            recovery_rate=recovery_rate,
            total_revenue_recovered=self.total_revenue_recovered,
            by_failure_type=self.by_failure_type,
            by_action_type=self.by_action_type
        )

    def get_before_after(self) -> Dict[str, Any]:
        """
        Returns a simulated comparison of AI recovery vs baseline (15%).
        """
        baseline_rate = 0.15
        baseline_recovered = int(self.total_processed * baseline_rate)
        
        average_tx_amount = self.total_revenue_recovered / self.total_recovered if self.total_recovered > 0 else 0
        baseline_revenue = baseline_recovered * average_tx_amount
        
        return {
            "baseline": {
                "recovery_rate": baseline_rate,
                "recovered_count": baseline_recovered,
                "revenue_recovered": baseline_revenue
            },
            "ai": {
                "recovery_rate": (self.total_recovered / self.total_processed) if self.total_processed > 0 else 0.0,
                "recovered_count": self.total_recovered,
                "revenue_recovered": self.total_revenue_recovered
            },
            "lift": {
                "absolute_rate_increase": ((self.total_recovered / self.total_processed) if self.total_processed > 0 else 0.0) - baseline_rate,
                "additional_recovered_count": self.total_recovered - baseline_recovered,
                "additional_revenue": self.total_revenue_recovered - baseline_revenue
            }
        }

    def export_report(self) -> str:
        """
        Generate a markdown formatted metrics report.
        """
        metrics = self.get_summary()
        ba = self.get_before_after()
        
        report = f"# RecoverAI Performance Report\n\n"
        report += f"## Overview\n"
        report += f"- **Total Processed:** {metrics.total_processed}\n"
        report += f"- **Total Recovered:** {metrics.total_recovered}\n"
        report += f"- **Recovery Rate:** {metrics.recovery_rate * 100:.2f}%\n"
        report += f"- **Revenue Recovered:** ${metrics.total_revenue_recovered:.2f}\n\n"
        
        report += f"## AI vs Baseline (Simulation)\n"
        report += f"- **Baseline Recovery:** {ba['baseline']['recovered_count']} ({ba['baseline']['recovery_rate']*100:.1f}%)\n"
        report += f"- **AI Recovery Lift:** +{ba['lift']['absolute_rate_increase']*100:.1f}% (Additional {ba['lift']['additional_recovered_count']} transactions)\n\n"
        
        report += f"## By Failure Type\n"
        for ft, stats in metrics.by_failure_type.items():
            rate = (stats["recovered"] / stats["processed"]) * 100 if stats["processed"] > 0 else 0
            report += f"- **{ft}:** {stats['recovered']}/{stats['processed']} ({rate:.1f}%)\n"
            
        return report
