import logging
from typing import List, Dict, Any
import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.db import init_db
from backend.models.schemas import (
    PaymentTransaction,
    SimulateRequest,
)
from backend.pipeline.recovery_pipeline import RecoveryPipeline
from backend.simulator.failure_generator import PaymentFailureSimulator
from backend.razorpay.client import razorpay_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-20s | %(levelname)-7s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RecoverAI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = RecoveryPipeline()
simulator = PaymentFailureSimulator()

@app.on_event("startup")
async def startup_event():
    init_db()
    if pipeline.classifier.model is None:
        pipeline.classifier.self_train(n_samples=500)

@app.get("/")
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "RecoverAI",
        "version": "1.0.0",
        "classifier_ready": pipeline.classifier.model is not None,
    }

@app.post("/api/simulate")
async def simulate_transactions(request: SimulateRequest):
    try:
        transactions = simulator.generate_batch(request.count)
        return {
            "count": len(transactions),
            "transactions": [t.model_dump(mode="json") for t in transactions],
        }
    except Exception as e:
        logger.error(f"Simulation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/classify")
async def classify_transaction(transaction: PaymentTransaction):
    try:
        classification = pipeline.classifier.classify(transaction)
        return classification.model_dump()
    except Exception as e:
        logger.error(f"Classification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recover")
async def recover_transaction(transaction: PaymentTransaction):
    try:
        result = await pipeline.process_single(transaction)
        return result.model_dump(mode="json")
    except Exception as e:
        logger.error(f"Recovery error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recover/batch")
async def recover_batch(transactions: List[PaymentTransaction]):
    try:
        results = await pipeline.process_batch(transactions)
        metrics = pipeline.get_metrics()
        return {
            "processed": len(results),
            "recovered": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success),
            "recovery_rate": f"{(sum(1 for r in results if r.success) / len(results) * 100):.1f}%" if results else "0%",
            "metrics": metrics.model_dump(),
            "results": [r.model_dump(mode="json") for r in results],
        }
    except Exception as e:
        logger.error(f"Batch recovery error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/demo")
async def run_demo(request: SimulateRequest):
    try:
        count = min(request.count, 500)
        transactions = simulator.generate_batch(count)
        results = await pipeline.process_batch(transactions)
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
            "sample_results": [r.model_dump(mode="json") for r in results],
        }
    except Exception as e:
        logger.error(f"Demo pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics")
async def get_metrics():
    return pipeline.get_metrics().model_dump()

@app.get("/api/metrics/comparison")
async def get_metrics_comparison():
    return pipeline.get_before_after_comparison()

@app.get("/api/metrics/report")
async def get_metrics_report():
    return {"report": pipeline.metrics.export_report()}

@app.get("/api/transactions")
async def list_transactions():
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
    res = pipeline.get_transaction_result(transaction_id)
    if not res:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return res.model_dump(mode="json")

@app.get("/api/audit/{transaction_id}")
async def get_audit_trail(transaction_id: str):
    trail = pipeline.get_audit_trail(transaction_id)
    return {"transaction_id": transaction_id, "entries": [e.model_dump(mode="json") for e in trail]}

@app.get("/api/classifier/features")
async def get_classifier_features():
    return pipeline.classifier.get_feature_importance()

class CustomRecoveryRequest(BaseModel):
    amount: float = 2499.0
    currency: str = "INR"
    method: str = "upi"
    failure_reason: str = "UPI transaction timed out waiting for bank approval"
    customer_name: str = "Aarav Sharma"
    customer_phone: str = "+91 98765 43210"
    language: str = "hinglish"
    channel: str = "whatsapp"

class RazorpayOrderRequest(BaseModel):
    amount: float = 500.0
    currency: str = "INR"
    receipt: str = "rcpt_recoverai_001"
    notes: Dict[str, Any] = {}

class WebhookSimulateRequest(BaseModel):
    event: str = "payment.failed"
    amount: float = 3499.0
    method: str = "upi"
    error_code: str = "GATEWAY_TIMEOUT"
    error_description: str = "Bank system timed out waiting for MPIN authorization"
    customer_name: str = "Priya Patel"

@app.post("/api/recover/custom")
async def recover_custom_transaction(request: CustomRecoveryRequest):
    try:
        tx_id = f"txn_{uuid.uuid4().hex[:12]}"
        tx = PaymentTransaction(
            id=tx_id,
            amount=request.amount,
            currency=request.currency,
            method=request.method,
            status="failed",
            failure_reason=request.failure_reason,
            customer_id=f"cust_{request.customer_name.lower().replace(' ', '_')}",
            merchant_id="merch_enterprise_01",
            timestamp=datetime.now(timezone.utc),
            metadata={
                "customer_name": request.customer_name,
                "customer_phone": request.customer_phone,
                "device": "mobile_app",
                "attempt_count": 1
            }
        )

        result = await pipeline.process_single(tx)
        classification = pipeline.classifier.classify(tx)
        nudge_action = await pipeline.nudge_agent.generate_nudge(tx, classification, language=request.language or "hinglish")
        
        return {
            "transaction": tx.model_dump(mode="json"),
            "result": result.model_dump(mode="json"),
            "personalized_nudge": {
                "channel": request.channel.capitalize() if request.channel else "WhatsApp",
                "language": request.language or "hinglish",
                "recipient": request.customer_name,
                "phone": request.customer_phone,
                "message": nudge_action.outcome or (nudge_action.details.get("message") if isinstance(nudge_action.details, dict) else str(nudge_action.details)),
                "cta_url": f"https://rzp.io/i/{tx_id}"
            }
        }
    except Exception as e:
        logger.error(f"Custom recovery error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/webhook/razorpay")
async def handle_razorpay_webhook(payload: Dict[str, Any]):
    try:
        event = payload.get("event", "payment.failed")
        payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        
        amount_inr = float(payment_entity.get("amount", 100000)) / 100.0
        method = payment_entity.get("method", "upi")
        error_desc = payment_entity.get("error_description") or payment_entity.get("error_reason") or "Payment authorization failed"
        
        tx_id = payment_entity.get("id") or f"pay_{uuid.uuid4().hex[:12]}"
        tx = PaymentTransaction(
            id=tx_id,
            amount=amount_inr,
            currency=payment_entity.get("currency", "INR"),
            method=method,
            status="failed",
            failure_reason=error_desc,
            customer_id=payment_entity.get("contact") or f"cust_{uuid.uuid4().hex[:6]}",
            merchant_id=payment_entity.get("notes", {}).get("merchant_id", "merch_razorpay_01"),
            timestamp=datetime.now(timezone.utc),
            metadata=payment_entity
        )
        
        result = await pipeline.process_single(tx)
        return {
            "status": "success",
            "event_processed": event,
            "transaction_id": tx_id,
            "recovered": result.success,
            "recovery_strategy": [a.action_type for a in result.actions_taken],
            "audit_trail_entries": len(result.audit_trail)
        }
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/api/webhook/simulate")
async def simulate_webhook_event(req: WebhookSimulateRequest):
    mock_payload = {
        "event": req.event,
        "payload": {
            "payment": {
                "entity": {
                    "id": f"pay_live_{uuid.uuid4().hex[:10]}",
                    "amount": int(req.amount * 100),
                    "currency": "INR",
                    "status": "failed",
                    "method": req.method,
                    "error_code": req.error_code,
                    "error_description": req.error_description,
                    "contact": f"+91 98{uuid.uuid4().hex[:8]}",
                    "notes": {"customer_name": req.customer_name}
                }
            }
        }
    }
    return await handle_razorpay_webhook(mock_payload)

@app.post("/api/razorpay/create-order")
async def create_live_razorpay_order(req: RazorpayOrderRequest):
    try:
        amount_paise = int(req.amount * 100)
        order = await razorpay_client.create_payment(
            amount=amount_paise,
            currency=req.currency,
            receipt=req.receipt or f"rcpt_{uuid.uuid4().hex[:8]}",
            notes=req.notes or {"source": "RecoverAI Agent"}
        )
        return {
            "success": True,
            "order_id": order.get("id"),
            "amount_inr": req.amount,
            "currency": req.currency,
            "status": order.get("status"),
            "raw_order": order
        }
    except Exception as e:
        logger.error(f"Razorpay live order error: {e}")
        return {
            "success": False,
            "error": str(e),
            "order_id": f"order_mock_{uuid.uuid4().hex[:8]}",
            "amount_inr": req.amount,
            "currency": req.currency,
            "status": "created"
        }
