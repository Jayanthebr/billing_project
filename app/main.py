# app/main.py
from fastapi import FastAPI, Request, Form, Depends, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .db import SessionLocal, engine, Base
from . import models, crud
from decimal import Decimal
from .utils_change import compute_change
import os
import aiosmtplib
from email.message import EmailMessage

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Simple home/billing page (Page 1)
@app.get("/billing", response_class=HTMLResponse)
def billing_page(request: Request, db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    # denominations for form defaults
    denoms = db.query(models.Denomination).order_by(models.Denomination.value.desc()).all()
    return templates.TemplateResponse("billing.html", {"request": request, "products": products, "denoms": denoms})

# Generate bill - receives form data (product entries created dynamically by JS)
@app.post("/generate-bill", response_class=HTMLResponse)
async def generate_bill(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    form = await request.form()
    # Extract posted data - we expect product lines as product_id_0, quantity_0, product_id_1, ...
    customer_email = form.get("customer_email")
    paid_amount = Decimal(form.get("paid_amount", "0"))
    # get dynamic lines
    items = []
    i = 0
    while True:
        pid = form.get(f"product_id_{i}")
        qty = form.get(f"quantity_{i}")
        if not pid:
            break
        items.append({"product_sku": pid.strip(), "quantity": int(qty)})
        i += 1

    # fetch/create customer
    customer = crud.get_or_create_customer(db, customer_email)

    # calculate per-item
    items_calc = []
    for it in items:
        prod = crud.get_product_by_sku(db, it["product_sku"])
        if not prod:
            raise HTTPException(status_code=400, detail=f"Product {it['product_sku']} not found")
        if prod.available_stocks < it["quantity"]:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {prod.product_id}")
        unit_price = Decimal(prod.price)
        qty = it["quantity"]
        item_subtotal = (unit_price * qty).quantize(Decimal("0.01"))
        item_tax = (item_subtotal * Decimal(prod.tax_percentage) / Decimal(100)).quantize(Decimal("0.01"))
        item_total = (item_subtotal + item_tax).quantize(Decimal("0.01"))
        items_calc.append({
            "product_id_db": prod.id,
            "product_sku": prod.product_id,
            "product_name": prod.name,
            "unit_price": unit_price,
            "tax_percentage": prod.tax_percentage,
            "quantity": qty,
            "item_subtotal": item_subtotal,
            "item_tax": item_tax,
            "item_total": item_total
        })

    # create purchase (decrement stocks)
    # decrement stocks before commit to ensure stock consistency
    for it in items_calc:
        p = db.query(models.Product).filter(models.Product.id == it["product_id_db"]).first()
        p.available_stocks -= it["quantity"]
        db.add(p)
    db.commit()

    purchase = crud.create_purchase(db, customer, items_calc, paid_amount)

    # compute change & denominations
    change_amount = Decimal(purchase.change_amount)
    available_denoms = [(d.value, d.count) for d in db.query(models.Denomination).order_by(models.Denomination.value.desc()).all()]
    used, remaining, insufficient = compute_change(change_amount, available_denoms)
    

    # If denominations were used, update counts
    if not insufficient:
        
        for entry in used:

            val = entry.get("value")
            used_count = entry.get("count")
    # do what you need to do with val and used_count

            if used_count > 0:
                d = db.query(models.Denomination).filter(models.Denomination.value == val).first()
                d.count -= used_count
                db.add(d)
        db.commit()

    # Background email send
    background_tasks.add_task(send_invoice_email, customer.email, purchase.id)

    # render invoice page (Page 2)
    items_in_db = db.query(models.PurchaseItem).filter(models.PurchaseItem.purchase_id == purchase.id).all()
    return templates.TemplateResponse("invoice.html", {
        "request": request,
        "purchase": purchase,
        "items": items_in_db,
        "denom_used": used,
        "insufficient_denominations": insufficient
    })

async def send_invoice_email(recipient: str, purchase_id: int):
    # Load SMTP config from env
    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASS = os.getenv("SMTP_PASS")
    if not SMTP_HOST:
        return  # no SMTP configured - skip silently or log
    # Construct email (simple)
    db = SessionLocal()
    purchase = db.query(models.Purchase).filter(models.Purchase.id == purchase_id).first()
    items = db.query(models.PurchaseItem).filter(models.PurchaseItem.purchase_id == purchase_id).all()
    body_lines = [f"Invoice: {purchase.invoice_no}\n", f"Total: {purchase.total_amount}\n", "Items:\n"]
    for it in items:
        body_lines.append(f"- {it.product_name} (x{it.quantity}) : {it.item_total}\n")
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = recipient
    msg["Subject"] = f"Your Invoice {purchase.invoice_no}"
    msg.set_content("\n".join(body_lines))

    await aiosmtplib.send(msg, hostname=SMTP_HOST, port=SMTP_PORT, username=SMTP_USER, password=SMTP_PASS, start_tls=True)
