#!/usr/bin/env python3
"""
Generate 50,000 realistic records across all tables for testing
Safely matches models.py schema using parameterized queries
"""

import random
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine, text

# ------------------ CONFIGURATION ------------------
DB = {
    "user": "root",
    "password": "root",
    "host": "localhost",
    "port": 3306,
    "database": "order_dispatch_db"
}

# ------------------ SAMPLE DATA ------------------
CITIES = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 'Pune', 'Ahmedabad']
STATES = ['Maharashtra', 'Delhi', 'Karnataka', 'Telangana', 'Tamil Nadu', 'West Bengal', 'Gujarat', 'Rajasthan']
BRANDS = ['Samsung', 'Apple', 'Sony', 'LG', 'Nike', 'Adidas', 'Puma', 'Boat', 'Philips', 'Levis']
CARRIERS = ['BlueDart', 'Delhivery', 'Ecom Express', 'FedEx', 'DTDC']

# ------------------ CONNECTION ------------------
engine = create_engine(
    f"mysql+pymysql://{DB['user']}:{DB['password']}@{DB['host']}:{DB['port']}/{DB['database']}?charset=utf8mb4",
    pool_pre_ping=True
)

# ------------------ UTILITIES ------------------
def random_email(name):
    domains = ['gmail.com', 'yahoo.com', 'outlook.com']
    return f"{name.lower().replace(' ', '.')}{random.randint(1, 9999)}@{random.choice(domains)}"

def random_phone():
    return f"+91 {random.randint(70000,99999)} {random.randint(10000,99999)}"

def random_date(days_back=365):
    start = date.today() - timedelta(days=days_back)
    return start + timedelta(days=random.randint(0, days_back))

# ------------------ RESET TABLES ------------------
def reset_tables(conn):
    print("🧹 Clearing existing data...")
    for table in ['shipments', 'orders', 'warehouses', 'products', 'customers', 'users']:
        try:
            conn.execute(text(f"TRUNCATE TABLE {table}"))
        except Exception as e:
            print(f"⚠️ Could not truncate {table}: {e}")
    # No manual commit here ✅


# ------------------ DATA GENERATORS ------------------
def gen_users(n=10):
    return [
        {
            "username": f"user{i+1}",
            "password": "admin123",
            "email": f"user{i+1}@test.com",
            "role": "admin",
            "full_name": f"User {i+1}",
            "phone": random_phone(),
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        for i in range(n)
    ]

def gen_customers(n=10000):
    data = []
    for i in range(n):
        name = f"Customer {i+1}"
        data.append({
            "customer_id": f"CUST{i+1:05d}",
            "name": name,
            "email": random_email(name),
            "phone": random_phone(),
            "company": random.choice(['Tech Corp', 'Solutions Pvt Ltd', 'Industries Ltd']),
            "address_line1": f"{random.randint(1,999)} {random.choice(['MG Road','Park St','Main Rd'])}",
            "address_line2": "",
            "city": random.choice(CITIES),
            "state": random.choice(STATES),
            "zipcode": f"{random.randint(100000,999999)}",
            "country": "India",
            "customer_type": random.choice(['Retail','Wholesale','Online']),
            "credit_limit": round(random.uniform(50000, 500000), 2),
            "outstanding_balance": round(random.uniform(10000, 50000), 2),
            "created_at": datetime.utcnow()
        })
    return data

def gen_products(n=2000):
    cats = ['Electronics','Clothing','Home & Kitchen','Sports','Beauty','Books']
    data = []
    for i in range(n):
        cat = random.choice(cats)
        data.append({
            "product_id": f"PROD{i+1:05d}",
            "name": f"{random.choice(BRANDS)} {cat} {i+1}",
            "category": cat,
            "brand": random.choice(BRANDS),
            "sku": f"SKU-{i+1:06d}",
            "description": f"High-quality {cat.lower()} item",
            "unit_price": round(random.uniform(500, 50000), 2),
            "cost_price": round(random.uniform(300, 40000), 2),
            "stock_quantity": random.randint(50, 1000),
            "reorder_level": random.randint(10, 50),
            "supplier_id": f"SUP{random.randint(1000,9999)}",
            "warehouse_location": f"Rack-{random.randint(1,50)}",
            "is_active": True,
            "created_at": datetime.utcnow()
        })
    return data

def gen_warehouses(n=20):
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
            "current_stock": random.randint(2000, 10000),
            "is_active": True
        })
    return data

def gen_orders(customers, products, warehouses, n=50000):
    data = []
    for i in range(n):
        cust = random.choice(customers)
        prod = random.choice(products)
        wh = random.choice(warehouses)
        order_date = random_date(180)
        qty = random.randint(1, 5)
        unit_price = float(prod["unit_price"])
        subtotal = qty * unit_price
        discount = round(subtotal * random.uniform(0.01, 0.1), 2)
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
            "order_status": random.choice(['Pending','Processing','Shipped','Delivered']),
            "priority_level": random.choice(['Low','Medium','High']),
            "order_type": random.choice(['Online','Offline','Phone']),
            "sales_channel": random.choice(['Website','Mobile App','Store']),
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
            "payment_method": random.choice(['Credit Card','UPI','Net Banking']),
            "payment_status": random.choice(['Paid','Pending']),
            "shipping_city": random.choice(CITIES),
            "shipping_state": random.choice(STATES),
            "shipping_country": "India",
            "carrier": random.choice(CARRIERS),
            "tracking_number": f"TRK{random.randint(1000000,9999999)}",
            "delivery_date": delivery_date,
            "warehouse_id": wh["warehouse_id"],
            "warehouse_name": wh["name"],
            "vehicle_number": f"MH{random.randint(10,99)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(1000,9999)}",
            "driver_name": f"Driver {i+1}",
            "dispatch_date": order_date,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
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
            "status": random.choice(['Delivered','In Transit']),
            "origin": o["shipping_city"],
            "destination": o["shipping_state"],
            "weight": round(random.uniform(5,50),2),
            "shipping_cost": 100.0,
            "notes": "",
            "created_at": datetime.utcnow()
        })
    return data

# ------------------ MAIN ------------------
def main():
    print("="*70)
    print(" REALISTIC BULK DATA GENERATOR - 50,000 Orders + Related Tables ")
    print("="*70)

    with engine.begin() as conn:
        reset_tables(conn)

        print("👥 Inserting users...")
        conn.execute(text("""
            INSERT INTO users (username, password, email, role, full_name, phone, is_active, created_at)
            VALUES (:username, :password, :email, :role, :full_name, :phone, :is_active, :created_at)
        """), gen_users())

        print("🏢 Inserting customers...")
        conn.execute(text("""
            INSERT INTO customers (customer_id, name, email, phone, company, address_line1, address_line2, city, state, zipcode, country, customer_type, credit_limit, outstanding_balance, created_at)
            VALUES (:customer_id, :name, :email, :phone, :company, :address_line1, :address_line2, :city, :state, :zipcode, :country, :customer_type, :credit_limit, :outstanding_balance, :created_at)
        """), gen_customers())

        print("📦 Inserting products...")
        conn.execute(text("""
            INSERT INTO products (product_id, name, category, brand, sku, description, unit_price, cost_price, stock_quantity, reorder_level, supplier_id, warehouse_location, is_active, created_at)
            VALUES (:product_id, :name, :category, :brand, :sku, :description, :unit_price, :cost_price, :stock_quantity, :reorder_level, :supplier_id, :warehouse_location, :is_active, :created_at)
        """), gen_products())

        print("🏭 Inserting warehouses...")
        conn.execute(text("""
            INSERT INTO warehouses (warehouse_id, name, location, city, state, manager_name, capacity, current_stock, is_active)
            VALUES (:warehouse_id, :name, :location, :city, :state, :manager_name, :capacity, :current_stock, :is_active)
        """), gen_warehouses())

        print("🧾 Generating orders (this may take a few minutes)...")
        customers = gen_customers()
        products = gen_products()
        warehouses = gen_warehouses()
        orders = gen_orders(customers, products, warehouses)

        batch_size = 2000
        for i in range(0, len(orders), batch_size):
            conn.execute(text("""
                INSERT INTO orders (order_id, customer_id, customer_name, customer_email, customer_phone, customer_company, order_date, order_status, priority_level, order_type, sales_channel, product_id, product_name, product_category, brand, quantity, unit_price, subtotal, discount_percent, discount_amount, tax_rate, tax_amount, shipping_cost, total_amount, currency, payment_method, payment_status, shipping_city, shipping_state, shipping_country, carrier, tracking_number, delivery_date, warehouse_id, warehouse_name, vehicle_number, driver_name, dispatch_date, created_at, updated_at)
                VALUES (:order_id, :customer_id, :customer_name, :customer_email, :customer_phone, :customer_company, :order_date, :order_status, :priority_level, :order_type, :sales_channel, :product_id, :product_name, :product_category, :brand, :quantity, :unit_price, :subtotal, :discount_percent, :discount_amount, :tax_rate, :tax_amount, :shipping_cost, :total_amount, :currency, :payment_method, :payment_status, :shipping_city, :shipping_state, :shipping_country, :carrier, :tracking_number, :delivery_date, :warehouse_id, :warehouse_name, :vehicle_number, :driver_name, :dispatch_date, :created_at, :updated_at)
            """), orders[i:i+batch_size])

        print("🚚 Inserting shipments...")
        shipments = gen_shipments(orders)
        conn.execute(text("""
            INSERT INTO shipments (shipment_id, order_id, carrier, tracking_number, delivery_date, status, origin, destination, weight, shipping_cost, notes, created_at)
            VALUES (:shipment_id, :order_id, :carrier, :tracking_number, :delivery_date, :status, :origin, :destination, :weight, :shipping_cost, :notes, :created_at)
        """), shipments)

        print("\n✅ All data successfully inserted!")
        print("📊 You now have 50,000 realistic orders + all linked tables.")
        print("="*70)

if __name__ == "__main__":
    main()
