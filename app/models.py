# app/models.py
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .db import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    available_stocks = Column(Integer, nullable=False, default=0)
    price = Column(Numeric(12,2), nullable=False)
    tax_percentage = Column(Numeric(5,2), nullable=False, default=0.0)
    created_at = Column(DateTime, server_default=func.now())

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    purchases = relationship("Purchase", back_populates="customer")

class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(Integer, primary_key=True, index=True)
    invoice_no = Column(String(64), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    total_subtotal = Column(Numeric(12,2), nullable=False)
    total_tax = Column(Numeric(12,2), nullable=False)
    total_amount = Column(Numeric(12,2), nullable=False)
    paid_amount = Column(Numeric(12,2), nullable=False)
    change_amount = Column(Numeric(12,2), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")
    customer = relationship("Customer", back_populates="purchases")

class PurchaseItem(Base):
    __tablename__ = "purchase_items"
    id = Column(Integer, primary_key=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    product_sku = Column(String(64), nullable=False)
    product_name = Column(String(255), nullable=False)
    unit_price = Column(Numeric(12,2), nullable=False)
    tax_percentage = Column(Numeric(5,2), nullable=False)
    quantity = Column(Integer, nullable=False)
    item_subtotal = Column(Numeric(12,2), nullable=False)
    item_tax = Column(Numeric(12,2), nullable=False)
    item_total = Column(Numeric(12,2), nullable=False)
    purchase = relationship("Purchase", back_populates="items")

class Denomination(Base):
    __tablename__ = "denominations"
    id = Column(Integer, primary_key=True)
    value = Column(Integer, nullable=False)  # e.g. 2000
    count = Column(Integer, nullable=False, default=0)
