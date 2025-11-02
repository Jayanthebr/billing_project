# app/seed_data.py
from .db import SessionLocal, engine, Base
from .models import Product, Denomination
from decimal import Decimal

def seed():
    db = SessionLocal()
    # Create some products
    products = [
        {"product_id":"SKU1001","name":"Pen Blue","available_stocks":100,"price":Decimal("10.00"),"tax_percentage":Decimal("5.00")},
        {"product_id":"SKU1002","name":"Notebook A4","available_stocks":50,"price":Decimal("40.00"),"tax_percentage":Decimal("12.00")},
        {"product_id":"SKU1003","name":"Marker","available_stocks":75,"price":Decimal("25.00"),"tax_percentage":Decimal("18.00")},
        {"product_id":"SKU1004","name":"Eraser","available_stocks":200,"price":Decimal("5.00"),"tax_percentage":Decimal("0.00")},
        {"product_id":"SKU1005","name":"Pencil","available_stocks":150,"price":Decimal("8.00"),"tax_percentage":Decimal("0.00")},
    ]
    for p in products:
        if not db.query(Product).filter(Product.product_id==p["product_id"]).first():
            prod = Product(**p)
            db.add(prod)

    # Denominations default
    denom_values = [2000, 500, 200, 100, 50, 20, 10, 5, 2, 1]
    for v in denom_values:
        if not db.query(Denomination).filter(Denomination.value==v).first():
            db.add(Denomination(value=v, count=50))  # default count 50 of each for seed

    db.commit()
    db.close()

if __name__ == "__main__":
    seed()
