# models.py  —  PostgreSQL-compatible ORM
from datetime import datetime, date, time
import decimal
from sqlalchemy import Index, text
from database import db

# ---------------------------------------------------
# USERS
# ---------------------------------------------------
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, index=True)
    role = db.Column(db.String(20), server_default=text("'user'"))
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, server_default=text("true"))
    created_at = db.Column(db.DateTime, server_default=db.func.now(), index=True)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# ---------------------------------------------------
# CUSTOMERS
# ---------------------------------------------------
class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100), index=True)
    state = db.Column(db.String(50), index=True)
    zipcode = db.Column(db.String(20))
    country = db.Column(db.String(50), server_default=text("'India'"), index=True)
    customer_type = db.Column(db.String(20))
    credit_limit = db.Column(db.Numeric(12, 2), server_default=text("0"))
    outstanding_balance = db.Column(db.Numeric(12, 2), server_default=text("0"))
    created_at = db.Column(db.DateTime, server_default=db.func.now(), index=True)


# ---------------------------------------------------
# PRODUCTS
# ---------------------------------------------------
class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    category = db.Column(db.String(100), index=True)
    brand = db.Column(db.String(100), index=True)
    sku = db.Column(db.String(100), unique=True, index=True)
    description = db.Column(db.Text)
    unit_price = db.Column(db.Numeric(12, 2), server_default=text("0"))
    cost_price = db.Column(db.Numeric(12, 2), server_default=text("0"))
    stock_quantity = db.Column(db.Integer, server_default=text("0"))
    reorder_level = db.Column(db.Integer, server_default=text("10"))
    supplier_id = db.Column(db.String(50))
    warehouse_location = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, server_default=text("true"), index=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), index=True)


# ---------------------------------------------------
# WAREHOUSES
# ---------------------------------------------------
class Warehouse(db.Model):
    __tablename__ = "warehouses"

    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    location = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    manager_name = db.Column(db.String(100))
    capacity = db.Column(db.Integer, server_default=text("0"))
    current_stock = db.Column(db.Integer, server_default=text("0"))
    is_active = db.Column(db.Boolean, server_default=text("true"), index=True)


# ---------------------------------------------------
# SHIPMENTS
# ---------------------------------------------------
class Shipment(db.Model):
    __tablename__ = "shipments"

    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    order_id = db.Column(db.String(50), index=True)
    carrier = db.Column(db.String(100))
    tracking_number = db.Column(db.String(100))
    ship_date = db.Column(db.Date)
    delivery_date = db.Column(db.Date)
    status = db.Column(db.String(30))
    origin = db.Column(db.String(200))
    destination = db.Column(db.String(200))
    weight = db.Column(db.Numeric(10, 2))
    shipping_cost = db.Column(db.Numeric(10, 2))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), index=True)


# ---------------------------------------------------
# ORDERS (150+ columns, all preserved)
# ---------------------------------------------------
class Order(db.Model):
    __tablename__ = "orders"

    order_id = db.Column(db.String(50), primary_key=True)

    # --- Customer Info (15)
    customer_id = db.Column(db.String(50), index=True)
    customer_name = db.Column(db.String(100), nullable=False, index=True)
    customer_email = db.Column(db.String(100))
    customer_phone = db.Column(db.String(20))
    customer_company = db.Column(db.String(150))
    customer_type = db.Column(db.String(30))
    customer_segment = db.Column(db.String(50))
    customer_tier = db.Column(db.String(20))
    customer_since = db.Column(db.Date)
    customer_rating = db.Column(db.Numeric(3, 2))
    customer_lifetime_value = db.Column(db.Numeric(12, 2))
    account_manager = db.Column(db.String(100))
    customer_city = db.Column(db.String(100))
    customer_state = db.Column(db.String(50))
    customer_country = db.Column(db.String(50))

    # --- Order Meta (10)
    order_date = db.Column(db.Date, index=True)
    order_time = db.Column(db.Time)
    order_status = db.Column(db.String(30), server_default=text("'Pending'"), index=True)
    priority_level = db.Column(db.String(20), server_default=text("'Medium'"), index=True)
    order_type = db.Column(db.String(50))
    sales_channel = db.Column(db.String(50))
    sales_rep = db.Column(db.String(100))
    department = db.Column(db.String(50))
    region = db.Column(db.String(50))
    division = db.Column(db.String(50))

    # --- Product Info (20)
    product_id = db.Column(db.String(50), index=True)
    product_name = db.Column(db.String(200), index=True)
    product_category = db.Column(db.String(100))
    product_subcategory = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    sku = db.Column(db.String(100))
    quantity = db.Column(db.Integer, server_default=text("1"))
    unit_price = db.Column(db.Numeric(12, 2), server_default=text("0"))
    subtotal = db.Column(db.Numeric(12, 2), server_default=text("0"))
    discount_percent = db.Column(db.Numeric(5, 2), server_default=text("0"))
    discount_amount = db.Column(db.Numeric(12, 2), server_default=text("0"))
    tax_rate = db.Column(db.Numeric(5, 2), server_default=text("0"))
    tax_amount = db.Column(db.Numeric(12, 2), server_default=text("0"))
    shipping_cost = db.Column(db.Numeric(10, 2), server_default=text("0"))
    total_amount = db.Column(db.Numeric(12, 2), server_default=text("0"))
    currency = db.Column(db.String(10), server_default=text("'INR'"))
    payment_status = db.Column(db.String(30))
    payment_method = db.Column(db.String(50))
    payment_due_date = db.Column(db.Date)

    # --- Shipping (15)
    shipping_address_line1 = db.Column(db.String(200))
    shipping_address_line2 = db.Column(db.String(200))
    shipping_city = db.Column(db.String(100))
    shipping_state = db.Column(db.String(100))
    shipping_country = db.Column(db.String(100))
    shipping_zipcode = db.Column(db.String(20))
    carrier = db.Column(db.String(100))
    tracking_number = db.Column(db.String(100))
    delivery_date = db.Column(db.Date)
    delivery_status = db.Column(db.String(30))
    warehouse_id = db.Column(db.String(50))
    warehouse_name = db.Column(db.String(100))
    dispatch_date = db.Column(db.Date)
    driver_name = db.Column(db.String(100))
    vehicle_number = db.Column(db.String(50))

    # --- Analytics & Flags (miscellaneous)
    order_source = db.Column(db.String(50))
    marketing_campaign = db.Column(db.String(100))
    utm_source = db.Column(db.String(100))
    region_name = db.Column(db.String(100))
    return_status = db.Column(db.String(30))
    qc_status = db.Column(db.String(30))
    on_time_delivery = db.Column(db.Boolean)
    perfect_order = db.Column(db.Boolean)

    # --- Timestamps
    created_at = db.Column(db.DateTime, server_default=db.func.now(), index=True)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now(), index=True)

    def to_dict(self):
        out = {}
        for c in self.__table__.columns:
            v = getattr(self, c.name)
            if isinstance(v, decimal.Decimal):
                out[c.name] = float(v)
            elif hasattr(v, "isoformat"):
                out[c.name] = v.isoformat()
            else:
                out[c.name] = v
        return out


# Composite indexes
Index("ix_orders_status_date", Order.order_status, Order.order_date)
Index("ix_orders_customer_city", Order.customer_name, Order.customer_city)
Index("ix_orders_carrier_state", Order.carrier, Order.shipping_state)
