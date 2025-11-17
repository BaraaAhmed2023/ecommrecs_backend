from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.product import ProductResponse

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderItemResponse(OrderItemBase):
    id: int
    product: ProductResponse

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    total_amount: float
    status: str = "pending"
    daftra_invoice_id: Optional[str] = None

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int
    user_id: int
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True