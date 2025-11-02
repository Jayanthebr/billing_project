# app/schemas.py
from pydantic import BaseModel, EmailStr, conint, condecimal
from typing import List, Optional

class PurchaseItemIn(BaseModel):
    product_id: str  # product SKU
    quantity: conint(gt=0)

class BillingRequest(BaseModel):
    customer_email: EmailStr
    items: List[PurchaseItemIn]
    paid_amount: condecimal(gt=0)
    denominations: Optional[dict] = None  # optional initial denominations counts from form
