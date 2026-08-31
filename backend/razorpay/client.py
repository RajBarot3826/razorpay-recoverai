import asyncio
import razorpay
import logging
from typing import Dict, Any, List, Optional
from ..config import settings

logger = logging.getLogger(__name__)

class RazorpayClientWrapper:
    def __init__(self):
        self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        self.client.set_app_details({"title": "RecoverAI", "version": "1.0"})
    
    async def _execute_with_retry(self, func, *args, **kwargs) -> Any:
        retries = settings.MAX_RETRIES
        for attempt in range(retries):
            try:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, lambda: func(*args, **kwargs))
                return result
            except Exception as e:
                logger.error(f"Razorpay API Error on attempt {attempt+1}: {e}")
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(1)

    async def create_payment(self, amount: int, currency: str = "INR", receipt: Optional[str] = None, notes: Optional[Dict] = None) -> Dict[str, Any]:
        data = {
            "amount": amount,
            "currency": currency,
        }
        if receipt:
            data["receipt"] = receipt
        if notes:
            data["notes"] = notes
        return await self._execute_with_retry(self.client.order.create, data=data)

    async def fetch_payment(self, payment_id: str) -> Dict[str, Any]:
        return await self._execute_with_retry(self.client.payment.fetch, payment_id)

    async def fetch_payments(self, skip: int = 0, count: int = 10, **kwargs) -> Dict[str, Any]:
        data = {"skip": skip, "count": count}
        data.update(kwargs)
        return await self._execute_with_retry(self.client.payment.all, data)

    async def fetch_failed_payments(self, skip: int = 0, count: int = 10) -> List[Dict[str, Any]]:
        payments = await self.fetch_payments(skip=skip, count=count)
        return [p for p in payments.get("items", []) if p.get("status") == "failed"]

    async def create_refund(self, payment_id: str, amount: Optional[int] = None) -> Dict[str, Any]:
        data = {}
        if amount:
            data["amount"] = amount
        return await self._execute_with_retry(self.client.payment.refund, payment_id, data)

    async def create_subscription(self, plan_id: str, total_count: int, quantity: int = 1, customer_id: Optional[str] = None) -> Dict[str, Any]:
        data = {
            "plan_id": plan_id,
            "total_count": total_count,
            "quantity": quantity
        }
        if customer_id:
            data["customer_id"] = customer_id
        return await self._execute_with_retry(self.client.subscription.create, data=data)

razorpay_client = RazorpayClientWrapper()
