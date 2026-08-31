"""
RecoverAI — FastAPI Application

Main entry point for the RecoverAI API.
Provides endpoints for simulating failures, classifying them,
running recovery pipelines, and viewing metrics.

Run with: uvicorn backend.main:app --reload --port 8000
"""

import logging
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.db import init_db
from backend.models.schemas import (
    PaymentTransaction,
    RecoveryResult,
    RecoveryMetrics,
    SimulateRequest,
)
from backend.pipeline.recovery_pipeline import RecoveryPipeline
from backend.simulator.failure_generator import PaymentFailureSimulator

# ─── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-25s | %(levelname)-7s | %(message)s",
)
logger = logging.getLogger(__name__)

# ─── App ────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="RecoverAI",
    description="AI-Powered Payment Recovery Agent — Razorpay Buildathon 2026",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Global Instances ───────────────────────────────────────────────────────
pipeline = RecoveryPipeline()
simulator = PaymentFailureSimulator()


@app.on_event("startup")
async def startup_event():
    """Initialize database and train classifier on startup."""
    logger.info("🚀 Initializing RecoverAI...")
    init_db()

    # Self-train classifier if no model exists
    if pipeline.classifier.model is None:
        logger.info("🧠 No trained model found. Self-training classifier...")
        metrics = pipeline.classifier.self_train(n_samples=500)
        logger.info(f"✅ Classifier trained: accuracy={metrics.get('accuracy', 0):.3f}")

    logger.info("✅ RecoverAI startup complete.")


# ─── Health ─────────────────────────────────────────────────────────────────

@app.get("/")
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "RecoverAI",
        "version": "1.0.0",
        "classifier_ready": pipeline.classifier.model is not None,
    }


# ─── Simulation ─────────────────────────────────────────────────────────────

@app.post("/api/simulate")
async def simulate_transactions(request: SimulateRequest):
    """Generate N simulated failed transactions."""
    try:
        transactions = simulator.generate_batch(request.count)
        return {
            "count": len(transactions),
            "transactions": [t.model_dump(mode="json") for t in transactions],
        }
    except Exception as e:
        logger.error(f"Simulation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Classification ─────────────────────────────────────────────────────────

@app.post("/api/classify")
async def classify_transaction(transaction: PaymentTransaction):
    """Classify a single transaction's failure type."""
    try:
        classification = pipeline.classifier.classify(transaction)
        return classification.model_dump(mode="json")
    except Exception as e:
        logger.error(f"Classification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Root Cause Analysis ────────────────────────────────────────────────────

@app.post("/api/analyze")
async def analyze_root_cause(transaction: PaymentTransaction):
    """Run root cause analysis on a single transaction."""
    try:
        classification = pipeline.classifier.classify(transaction)
        root_cause = await pipeline.root_cause_analyzer.analyze(transaction, classification)
        return root_cause.model_dump(mode="json")
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Recovery ────────────────────────────────────────────────────────────────

@app.post("/api/recover")
async def recover_single(transaction: PaymentTransaction):
    """Run the full recovery pipeline on a single transaction."""
    try:
        result = await pipeline.process_single(transaction)
        return result.model_dump(mode="json")
    except Exception as e:
        logger.error(f"Recovery error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/recover/batch")
async def recover_batch(transactions: List[PaymentTransaction]):
    """Run the full recovery pipeline on a batch of transactions."""
    try:
        results = await pipeline.process_batch(transactions)
        return {
            "count": len(results),
            "recovered": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success),
            "results": [r.model_dump(mode="json") for r in results],
        }
    except Exception as e:
        logger.error(f"Batch recovery error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Simulate + Recover (Convenience) ───────────────────────────────────────

@app.post("/api/demo")
async def demo_full_pipeline(request: SimulateRequest):
    """
    Convenience endpoint: generate failures AND run recovery in one call.
    Perfect for demos and the pitch video.
    """
    try:
        # 1. Generate failures
        transactions = simulator.generate_batch(request.count)
        logger.info(f"Generated {len(transactions)} failed transactions")

        # 2. Run recovery
        results = await pipeline.process_batch(transactions)

        # 3. Get metrics
        metrics = pipeline.get_metrics()
        comparison = pipeline.get_before_after_comparison()

        return {
            "transactions_generated": len(transactions),
            "results_summary": {
                "total": len(results),
                "recovered": sum(1 for r in results if r.success),
                "failed": sum(1 for r in results if not r.success),
                "recovery_rate": f"{(sum(1 for r in results if r.success) / len(results) * 100):.1f}%",
            },
            "metrics": metrics.model_dump(),
            "before_after": comparison,
            "sample_results": [r.model_dump(mode="json") for r in results[:5]],
        }
    except Exception as e:
        logger.error(f"Demo pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Metrics ─────────────────────────────────────────────────────────────────

@app.get("/api/metrics")
async def get_metrics():
    """Get aggregate recovery metrics."""
    return pipeline.get_metrics().model_dump()


@app.get("/api/metrics/comparison")
async def get_metrics_comparison():
    """Get before/after comparison (AI vs baseline)."""
    return pipeline.get_before_after_comparison()


@app.get("/api/metrics/report")
async def get_metrics_report():
    """Get markdown-formatted metrics report."""
    return {"report": pipeline.metrics.export_report()}


# ─── Transaction History ─────────────────────────────────────────────────────

@app.get("/api/transactions")
async def list_transactions():
    """List all processed transactions with summary."""
    return [
        {
            "transaction_id": tid,
            "success": r.success,
            "failure_type": r.failure_type,
            "original_amount": r.original_amount,
            "actions_count": len(r.actions_taken),
        }
        for tid, r in pipeline.results_store.items()
    ]


@app.get("/api/transactions/{transaction_id}")
async def get_transaction(transaction_id: str):
    """Get full detail including audit trail for one transaction."""
    res = pipeline.get_transaction_result(transaction_id)
    if not res:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return res.model_dump(mode="json")


# ─── Audit ───────────────────────────────────────────────────────────────────

@app.get("/api/audit/{transaction_id}")
async def get_audit_trail(transaction_id: str):
    """Get audit trail for a specific transaction."""
    trail = pipeline.audit_logger.get_trail(transaction_id)
    return {
        "transaction_id": transaction_id,
        "entries": [e.model_dump(mode="json") for e in trail],
    }


# ─── Classifier Info ─────────────────────────────────────────────────────────

@app.get("/api/classifier/features")
async def get_feature_importance():
    """Get feature importance from the ML classifier."""
    return pipeline.classifier.get_feature_importance()


# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
