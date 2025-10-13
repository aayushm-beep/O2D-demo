#!/usr/bin/env python3
"""
Generate demo data (Users, Customers, Products, Warehouses, Orders, Shipments)
Compatible with PostgreSQL / Render environment
"""

import os
import random
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine, text

# ---------------------------------------------------------------------
# PostgreSQL Connection (auto from Render .env)
# ---------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not found. Make sure it's set in environment.")

# Render gives 'postgres://' — SQLAlchemy needs 'postgresql+psycopg2://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# ---------------------------------------------------------------------
# Demo data sources
# ---------------------------------------------------------------------
CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
    "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Surat"
]
STATES = [
    "Maharashtra", "Delhi", "Karnataka", "Telangana",
    "Tamil Nadu", "West Bengal", "Gujarat", "Rajasthan"
]
BRANDS = ["Samsung", "Apple", "Sony", "LG", "Nike", "Adidas", "Puma", "Boat", "Philips", "Levis"]
CARRIERS = ["BlueDart", "Delhivery", "Ecom Express", "FedEx", "DTDC"]

# ---------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------
def random_email(name):
    return f"{name.lower().replace(' ', '.')}{random.randint(1,9999)}@example.com"

def random_phone():
    return f"+91 {random.randint(70000,99999)} {random.randint(10000,99999)}"

def random_date(days_back=365):
    start = date.today() - timedelta(days=days_back)
    return start + timedelta(days=random.randint(0, days_back))

# ---------------------------------------------------------------------
# Table generators
# ---------------------------------------------------------------------
def gen_users(n=5):
    now = datetime.utcnow()
    return [
        {
            "username": f"user{i+1}",
            "password": "admin123",
            "email": f"user{i+1}@demo.com",
            "role": "user",
            "full_name": f"User {i+1}",
            "phone": random_phone(),
            "is_active": True,
            "created_at": now,
        }
        for i in range(n)
    ]

def gen_customers(n=100):
    now = datetime.utcnow()
    data = []
    for i in range(n):
        name = f"Customer {i+1}"
        data.append({
            "customer_id": f"CUST{i+1:05d}",
            "name": name,
            "email": random_email(name),
            "phone": random_phone(),
            "company": random.choice(["TechCorp", "Solutions Pvt Ltd", "Industries Ltd"]),
            "address_line1": f"{random.randint(1,999)} {random.choice(['Main Rd','Market St','MG Road'])}",
            "address_line2": "",
            "city": random.choice(CITIES),
            "state": random.choice(STATES),
            "zipcode": str(random.randint(100000,999999)),
            "country": "India",
            "customer_type": random.choice(["Retail", "Wholesale", "Online"]),
            "credit_limit": round(random.uniform(50000, 300000), 2),
            "outstanding_balance": round(random.uniform(10000, 40000), 2),
            "created_at": now,
        })
    return data

def gen_products(n=200):
    now = datetime.utcnow()
    data = []
    categories = ["Electronics", "Clothing", "Home & Kitchen", "Sports", "Beauty", "Books"]
    for i in range(n):
        cat = random.choice(categories)
        brand = random.choice(BRANDS)
        data.append({
            "product_id": f"PROD{i+1:05d}",
            "name": f"{brand} {cat} Item {i+1}",
            "category": cat,
            "brand": brand,
            "sku": f"SKU-{i+1:06d}",
            "description": f"High-quality {cat.lower()} product",
            "unit_price": round(random.uniform(300, 10000), 2),
            "cost_price": round(random.uniform(200, 8000), 2),
            "stock_quantity": random.randint(10, 500),
            "reorder_level": random.randint(5, 30),
            "supplier_id": f"SUP{random.randint(1000,9999)}",
            "warehouse_location": f"Rack-{random.randint(1,50)}",
            "is_active": True,
            "created_at": now,
        })
    return data

def gen_warehouses(n=10):
    data = []
    for i in range(n):
        city = random.choice(CITIES)
        data.append({
            "warehouse_id": f"WH{i+1:03d}",
            "name": f"Warehouse {city}",
            "location": f"{random.randint(1,999)} {city} Industrial Area",
            "city": city,
            "state": random.choice(STATES),
            "manager_name": f"Manager {i+1}",
            "capacity": random.randint(10000, 20000),
            "current_stock": random.randint(2000, 8000),
            "is_active": True,
        })
    return data

def gen_orders(customers, products, warehouses, n=500):
    data = []
    for i in range(n):
        cust = random.choice(customers)
        prod = random.choice(products)
        wh = random.choice(warehouses)
        order_date = random_date(180)
        qty = random.randint(1, 5)
        unit_price = float(prod["unit_price"])
        subtotal = qty * unit_price
        discount = round(subtotal * random.uniform(0.02, 0.1), 2)
        tax = round((subtotal - discount) * 0.18, 2)
        total = subtotal - discount + tax
        delivery_date = order_date + timedelta(days=random.randint(2, 10))

        data.append({
            "order_id": f"ORD{i+1:06d}",
            "customer_id": cust["customer_id"],
            "customer_name": cust["name"],
            "customer_email": cust["email"],
            "customer_phone": cust["phone"],
            "customer_company": cust["company"],
            "order_date": order_date,
            "order_status": random.choice(["Pending", "Processing", "Shipped", "Delivered"]),
            "priority_level": random.choice(["Low", "Medium", "High"]),
            "order_type": random.choice(["Online", "Offline"]),
            "sales_channel": random.choice(["Website", "Mobile App", "Store"]),
            "product_id": prod["product_id"],
            "product_name": prod["name"],
            "product_category": prod["category"],
            "brand": prod["brand"],
            "quantity": qty,
            "unit_price": unit_price,
            "subtotal": subtotal,
            "discount_percent": 10,
            "discount_amount": discount,
            "tax_rate": 18,
            "tax_amount": tax,
            "shipping_cost": 100,
            "total_amount": total,
            "currency": "INR",
            "payment_method": random.choice(["Credit Card", "UPI", "Net Banking"]),
            "payment_status": random.choice(["Paid", "Pending"]),
            "shipping_city": random.choice(CITIES),
            "shipping_state": random.choice(STATES),
            "shipping_country": "India",
            "carrier": random.choice(CARRIERS),
            "tracking_number": f"TRK{random.randint(100000,999999)}",
            "delivery_date": delivery_date,
            "warehouse_id": wh["warehouse_id"],
            "warehouse_name": wh["name"],
            "vehicle_number": f"MH{random.randint(10,99)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(1000,9999)}",
            "driver_name": f"Driver {i+1}",
            "dispatch_date": order_date,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        })
    return data

def gen_shipments(orders):
    data = []
    for i, o in enumerate(orders):
        data.append({
            "shipment_id": f"SHP{i+1:06d}",
            "order_id": o["order_id"],
            "carrier": o["carrier"],
            "tracking_number": o["tracking_number"],
            "delivery_date": o["delivery_date"],
            "status": random.choice(["Delivered", "In Transit"]),
            "origin": o["shipping_city"],
            "destination": o["shipping_state"],
            "weight": round(random.uniform(5, 50), 2),
            "shipping_cost": 100.0,
            "notes": "",
            "created_at": datetime.utcnow(),
        })
    return data

# ---------------------------------------------------------------------
# Main loader
# ---------------------------------------------------------------------
def main():
    with engine.begin() as conn:
        print("🚀 Inserting demo dataset into PostgreSQL...")

        # Clear tables
        for table in ["shipments", "orders", "warehouses", "products", "customers", "users"]:
            try:
                conn.execute(text(f"DELETE FROM {table}"))
            except Exception as e:
                print(f"⚠ Skipped clearing {table}: {e}")

        # Insert users
        print("👥 Inserting users...")
        conn.execute(text("""
            INSERT INTO users (username, password, email, role, full_name, phone, is_active, created_at)
            VALUES (:username, :password, :email, :role, :full_name, :phone, :is_active, :created_at)
        """), gen_users())

        # Insert customers
        print("🏢 Inserting customers...")
        conn.execute(text("""
            INSERT INTO customers (customer_id, name, email, phone, company, address_line1, address_line2,
            city, state, zipcode, country, customer_type, credit_limit, outstanding_balance, created_at)
            VALUES (:customer_id, :name, :email, :phone, :company, :address_line1, :address_line2,
            :city, :state, :zipcode, :country, :customer_type, :credit_limit, :outstanding_balance, :created_at)
        """), gen_customers())

        # Insert products
        print("📦 Inserting products...")
        conn.execute(text("""
            INSERT INTO products (product_id, name, category, brand, sku, description,
            unit_price, cost_price, stock_quantity, reorder_level, supplier_id, warehouse_location,
            is_active, created_at)
            VALUES (:product_id, :name, :category, :brand, :sku, :description,
            :unit_price, :cost_price, :stock_quantity, :reorder_level, :supplier_id, :warehouse_location,
            :is_active, :created_at)
        """), gen_products())

        # Insert warehouses
        print("🏭 Inserting warehouses...")
        conn.execute(text("""
            INSERT INTO warehouses (warehouse_id, name, location, city, state,
            manager_name, capacity, current_stock, is_active)
            VALUES (:warehouse_id, :name, :location, :city, :state,
            :manager_name, :capacity, :current_stock, :is_active)
        """), gen_warehouses())

        # Insert orders and shipments
        customers = gen_customers(50)
        products = gen_products(50)
        warehouses = gen_warehouses(5)
        orders = gen_orders(customers, products, warehouses, 500)

        print("🧾 Inserting orders...")
        conn.execute(text("""
            INSERT INTO orders (order_id, customer_id, customer_name, customer_email, customer_phone,
            customer_company, order_date, order_status, priority_level, order_type, sales_channel,
            product_id, product_name, product_category, brand, quantity, unit_price, subtotal,
            discount_percent, discount_amount, tax_rate, tax_amount, shipping_cost, total_amount,
            currency, payment_method, payment_status, shipping_city, shipping_state, shipping_country,
            carrier, tracking_number, delivery_date, warehouse_id, warehouse_name, vehicle_number,
            driver_name, dispatch_date, created_at, updated_at)
            VALUES (:order_id, :customer_id, :customer_name, :customer_email, :customer_phone,
            :customer_company, :order_date, :order_status, :priority_level, :order_type, :sales_channel,
            :product_id, :product_name, :product_category, :brand, :quantity, :unit_price, :subtotal,
            :discount_percent, :discount_amount, :tax_rate, :tax_amount, :shipping_cost, :total_amount,
            :currency, :payment_method, :payment_status, :shipping_city, :shipping_state, :shipping_country,
            :carrier, :tracking_number, :delivery_date, :warehouse_id, :warehouse_name, :vehicle_number,
            :driver_name, :dispatch_date, :created_at, :updated_at)
        """), orders)

        print("🚚 Inserting shipments...")
        conn.execute(text("""
            INSERT INTO shipments (shipment_id, order_id, carrier, tracking_number, delivery_date,
            status, origin, destination, weight, shipping_cost, notes, created_at)
            VALUES (:shipment_id, :order_id, :carrier, :tracking_number, :delivery_date,
            :status, :origin, :destination, :weight, :shipping_cost, :notes, :created_at)
        """), gen_shipments(orders))

        print("\n✅ PostgreSQL demo data inserted successfully!")
        print("💾 You now have populated users, customers, products, orders, and shipments.\n")


if __name__ == "__main__":
    main()
