from pydantic import BaseModel
from typing import List, Optional

class ProductBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    stock: int = 0
    sku: str
    images: Optional[List[str]] = None
    category_id: Optional[int] = None
    daftra_item_id: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    sku: Optional[str] = None
    images: Optional[List[str]] = None
    category_id: Optional[int] = None
    daftra_item_id: Optional[str] = None

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True