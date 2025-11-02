#  Billing Management System

The **Billing Management System** is a simple yet powerful project built using **FastAPI** and **SQLite**.  
It allows users to generate customer bills, manage available product data, and automatically calculate the change to be returned using available denominations.  

This project is ideal for small retail shops, demo POS systems, or as a learning project for FastAPI and backend logic with database integration.

---

## Overview

This web app consists of:
- A **frontend form** (HTML + JavaScript) for entering purchase and payment details.
- A **FastAPI backend** that processes the data, performs calculations, and renders the invoice.
- A **SQLite database** that stores product and currency denomination information.

When a customer purchases items:
1. The user selects products and quantities.
2. The system computes the total bill.
3. The customer pays an amount.
4. The backend determines how much change to return, and the exact notes/coins required.
5. The generated invoice is displayed in the browser.

---

## Features

-  **Bill Generation** — Create bills dynamically with product details, quantity, and prices.
-  **Change Calculation** — Automatically computes change to be returned in available denominations.
-  **Product Inventory** — Stores multiple products with stock and tax details.
-  **Tax Calculation** — Each product has a specific tax percentage included in the final total.
-  **Denomination Management** — Default denominations (₹2000, ₹500, ₹200, ₹100, etc.) with adjustable quantities.
-  **Web Interface** — Simple form-based UI to test the full billing workflow.
-  **FastAPI + SQLite** — Lightweight backend with fast response times.

---

---

## Technologies Used

 Component        | Technology Used 
-----------------------------------
 **Backend**      | FastAPI (Python 3.8+) 
 **Database**     | SQLite (via SQLAlchemy ORM) 
 **Frontend**     | HTML5, JavaScript 
 **Server**       | Uvicorn 
 **Dependencies** | Pydantic, SQLAlchemy, Jinja2, python-multipart 

---

##  Setup Instructions

Follow these steps to run the project locally on your system.

### 1️ Clone the repository

git clone https://github.com/<your-username>/billing_project.git

cd billing_project

python -m venv venv

venv\Scripts\activate("windows")

source venv/bin/activate("macOS/Linux")

pip install -r requirements.txt

python -m app.seed_data

uvicorn app.main:app --reload

then visit "http://127.0.0.1:8000/billing"



