# app/crud.py
from sqlalchemy.orm import Session
from . import models
from decimal import Decimal
import uuid

def get_or_create_customer(db: Session, email: str):
    cust = db.query(models.Customer).filter(models.Customer.email == email).first()
    if cust:
        return cust
    cust = models.Customer(email=email)
    db.add(cust); db.commit(); db.refresh(cust)
    return cust

def get_product_by_sku(db: Session, sku: str):
    return db.query(models.Product).filter(models.Product.product_id == sku).first()

def decrement_stock(db: Session, product: models.Product, qty: int):
    if product.available_stocks < qty:
        raise ValueError(f"Insufficient stock for {product.product_id}")
    product.available_stocks -= qty
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def create_purchase(db: Session, customer: models.Customer, items_calc: dict, paid_amount: Decimal):
    # items_calc contains list of item dicts with calculations
    invoice_no = str(uuid.uuid4())[:8].upper()
    total_sub = sum([i["item_subtotal"] for i in items_calc])
    total_tax = sum([i["item_tax"] for i in items_calc])
    total_amount = total_sub + total_tax
    change_amount = Decimal(paid_amount) - total_amount
    purchase = models.Purchase(
        invoice_no=invoice_no,
        customer_id=customer.id,
        total_subtotal=total_sub,
        total_tax=total_tax,
        total_amount=total_amount,
        paid_amount=paid_amount,
        change_amount=change_amount
    )
    db.add(purchase); db.commit(); db.refresh(purchase)
    for it in items_calc:
        pi = models.PurchaseItem(
            purchase_id=purchase.id,
            product_id=it["product_id_db"],
            product_sku=it["product_sku"],
            product_name=it["product_name"],
            unit_price=it["unit_price"],
            tax_percentage=it["tax_percentage"],
            quantity=it["quantity"],
            item_subtotal=it["item_subtotal"],
            item_tax=it["item_tax"],
            item_total=it["item_total"]
        )
        db.add(pi)
    db.commit()
    db.refresh(purchase)
    return purchase
