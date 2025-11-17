from sqlalchemy import Column, Integer, String, Float, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    sku = Column(String, unique=True, index=True)
    images = Column(JSON)  # Store as JSON array of image URLs
    category_id = Column(Integer, ForeignKey("categories.id"))
    daftra_item_id = Column(String)  # Daftra item reference

    category = relationship("Category", back_populates="products")