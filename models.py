from datetime import datetime
import decimal
from sqlalchemy import Index
from database import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, index=True)
    role = db.Column(db.String(20), default='user')
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'full_name': self.full_name,
            'is_active': self.is_active
        }

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(100), index=True)
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100), index=True)
    state = db.Column(db.String(50), index=True)
    zipcode = db.Column(db.String(20))
    country = db.Column(db.String(50), default='USA', index=True)
    customer_type = db.Column(db.String(20))
    credit_limit = db.Column(db.Numeric(10, 2), default=0)
    outstanding_balance = db.Column(db.Numeric(10, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'company': self.company,
            'city': self.city,
            'state': self.state,
            'customer_type': self.customer_type,
            'credit_limit': float(self.credit_limit) if self.credit_limit else 0,
            'outstanding_balance': float(self.outstanding_balance) if self.outstanding_balance else 0
        }

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    category = db.Column(db.String(100), index=True)
    brand = db.Column(db.String(100), index=True)
    sku = db.Column(db.String(100), unique=True, index=True)
    description = db.Column(db.Text)
    unit_price = db.Column(db.Numeric(10, 2), default=0)
    cost_price = db.Column(db.Numeric(10, 2), default=0)
    stock_quantity = db.Column(db.Integer, default=0)
    reorder_level = db.Column(db.Integer, default=10)
    supplier_id = db.Column(db.String(50))
    warehouse_location = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'name': self.name,
            'category': self.category,
            'brand': self.brand,
            'sku': self.sku,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'stock_quantity': self.stock_quantity,
            'reorder_level': self.reorder_level,
            'is_active': self.is_active
        }

class Warehouse(db.Model):
    __tablename__ = 'warehouses'
    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    location = db.Column(db.String(200))
    city = db.Column(db.String(100), index=True)
    state = db.Column(db.String(50), index=True)
    manager_name = db.Column(db.String(100))
    capacity = db.Column(db.Integer)
    current_stock = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'warehouse_id': self.warehouse_id,
            'name': self.name,
            'location': self.location,
            'city': self.city,
            'manager_name': self.manager_name,
            'capacity': self.capacity,
            'current_stock': self.current_stock,
            'utilization': round((self.current_stock / self.capacity * 100), 2) if self.capacity else 0
        }

class Shipment(db.Model):
    __tablename__ = 'shipments'
    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    order_id = db.Column(db.String(50), index=True)
    carrier = db.Column(db.String(100), index=True)
    tracking_number = db.Column(db.String(100), index=True)
    ship_date = db.Column(db.Date, index=True)
    delivery_date = db.Column(db.Date, index=True)
    status = db.Column(db.String(20))
    origin = db.Column(db.String(200))
    destination = db.Column(db.String(200))
    weight = db.Column(db.Numeric(10, 2))
    shipping_cost = db.Column(db.Numeric(10, 2))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'shipment_id': self.shipment_id,
            'order_id': self.order_id,
            'carrier': self.carrier,
            'tracking_number': self.tracking_number,
            'ship_date': self.ship_date.isoformat() if self.ship_date else None,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'status': self.status,
            'shipping_cost': float(self.shipping_cost) if self.shipping_cost else 0
        }

class Order(db.Model):
    __tablename__ = 'orders'
    
    # Primary Identification
    order_id = db.Column(db.String(50), primary_key=True)
    reference_number = db.Column(db.String(50))
    po_number = db.Column(db.String(50))
    invoice_number = db.Column(db.String(50))
    external_order_id = db.Column(db.String(100))
    
    # Customer Information
    customer_id = db.Column(db.String(50), nullable=False, index=True)
    customer_name = db.Column(db.String(100), nullable=False, index=True)
    customer_email = db.Column(db.String(100), index=True)
    customer_phone = db.Column(db.String(20))
    customer_mobile = db.Column(db.String(20))
    customer_fax = db.Column(db.String(20))
    customer_company = db.Column(db.String(150))
    customer_tax_id = db.Column(db.String(50))
    customer_type = db.Column(db.String(30))
    customer_segment = db.Column(db.String(50))
    customer_tier = db.Column(db.String(20))
    customer_since = db.Column(db.Date)
    customer_rating = db.Column(db.Numeric(3,2))
    customer_lifetime_value = db.Column(db.Numeric(12,2))
    account_manager = db.Column(db.String(100))
    
    # Order Date/Time
    order_date = db.Column(db.Date, nullable=False, index=True)
    order_time = db.Column(db.Time)
    order_datetime = db.Column(db.DateTime)
    order_timezone = db.Column(db.String(50))
    expected_ship_date = db.Column(db.Date)
    requested_delivery_date = db.Column(db.Date)
    promised_delivery_date = db.Column(db.Date)
    actual_ship_date = db.Column(db.Date)
    actual_delivery_date = db.Column(db.Date)
    order_processing_time = db.Column(db.Integer)
    
    # Status & Priority
    order_status = db.Column(db.String(30), default='Pending', index=True)
    order_substatus = db.Column(db.String(50))
    priority_level = db.Column(db.String(20), default='Medium', index=True)
    priority_score = db.Column(db.Integer)
    urgency_flag = db.Column(db.Boolean, default=False)
    rush_order = db.Column(db.Boolean, default=False)
    backorder_status = db.Column(db.String(30))
    fulfillment_status = db.Column(db.String(30))
    approval_status = db.Column(db.String(30))
    cancellation_reason = db.Column(db.Text)
    
    # Order Classification
    order_type = db.Column(db.String(50), index=True)
    order_category = db.Column(db.String(50))
    order_source = db.Column(db.String(50))
    sales_channel = db.Column(db.String(50), index=True)
    sales_rep = db.Column(db.String(100))
    sales_team = db.Column(db.String(100))
    department = db.Column(db.String(50))
    division = db.Column(db.String(50))
    territory = db.Column(db.String(50))
    region = db.Column(db.String(50))
    
    # Marketing & Promotion
    marketing_campaign = db.Column(db.String(150))
    campaign_id = db.Column(db.String(50))
    promo_code = db.Column(db.String(50))
    discount_code = db.Column(db.String(50))
    affiliate_id = db.Column(db.String(50))
    referral_source = db.Column(db.String(100))
    utm_source = db.Column(db.String(100))
    utm_campaign = db.Column(db.String(100))
    
    # Product Information
    product_id = db.Column(db.String(50), index=True)
    product_name = db.Column(db.String(200), index=True)
    product_category = db.Column(db.String(100), index=True)
    product_subcategory = db.Column(db.String(100))
    product_line = db.Column(db.String(100))
    brand = db.Column(db.String(100), index=True)
    model = db.Column(db.String(100))
    sku = db.Column(db.String(100))
    upc = db.Column(db.String(50))
    ean = db.Column(db.String(50))
    isbn = db.Column(db.String(50))
    manufacturer = db.Column(db.String(100))
    manufacturer_part_number = db.Column(db.String(100))
    supplier_id = db.Column(db.String(50))
    supplier_name = db.Column(db.String(100))
    product_description = db.Column(db.Text)
    product_weight = db.Column(db.Numeric(10,3))
    product_dimensions = db.Column(db.String(50))
    product_color = db.Column(db.String(50))
    product_size = db.Column(db.String(50))
    
    # Inventory & Stock
    quantity = db.Column(db.Integer, default=1)
    quantity_shipped = db.Column(db.Integer, default=0)
    quantity_backordered = db.Column(db.Integer, default=0)
    quantity_cancelled = db.Column(db.Integer, default=0)
    stock_location = db.Column(db.String(100))
    bin_location = db.Column(db.String(50))
    lot_number = db.Column(db.String(50))
    serial_number = db.Column(db.String(100))
    batch_number = db.Column(db.String(100))
    expiry_date = db.Column(db.Date)
    manufacture_date = db.Column(db.Date)
    reorder_point = db.Column(db.Integer)
    
    # Pricing & Financial
    unit_price = db.Column(db.Numeric(12,2), default=0.00)
    list_price = db.Column(db.Numeric(12,2), default=0.00)
    cost_price = db.Column(db.Numeric(12,2), default=0.00)
    wholesale_price = db.Column(db.Numeric(12,2), default=0.00)
    retail_price = db.Column(db.Numeric(12,2), default=0.00)
    subtotal = db.Column(db.Numeric(12,2), default=0.00)
    discount_percent = db.Column(db.Numeric(5,2), default=0.00)
    discount_amount = db.Column(db.Numeric(12,2), default=0.00)
    discount_type = db.Column(db.String(30))
    tax_rate = db.Column(db.Numeric(5,2), default=0.00)
    tax_amount = db.Column(db.Numeric(12,2), default=0.00)
    tax_exempt = db.Column(db.Boolean, default=False)
    vat_rate = db.Column(db.Numeric(5,2), default=0.00)
    vat_amount = db.Column(db.Numeric(12,2), default=0.00)
    shipping_cost = db.Column(db.Numeric(10,2), default=0.00)
    handling_fee = db.Column(db.Numeric(10,2), default=0.00)
    insurance_cost = db.Column(db.Numeric(10,2), default=0.00)
    customs_duty = db.Column(db.Numeric(10,2), default=0.00)
    other_charges = db.Column(db.Numeric(10,2), default=0.00)
    total_amount = db.Column(db.Numeric(12,2), default=0.00)
    currency = db.Column(db.String(10), default='USD')
    exchange_rate = db.Column(db.Numeric(10,6), default=1.000000)
    profit_margin = db.Column(db.Numeric(5,2))
    commission_amount = db.Column(db.Numeric(10,2))
    gross_profit = db.Column(db.Numeric(12,2))
    
    # Payment Information
    payment_terms = db.Column(db.String(50))
    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.String(30), index=True)
    payment_date = db.Column(db.Date)
    payment_due_date = db.Column(db.Date)
    payment_reference = db.Column(db.String(100))
    transaction_id = db.Column(db.String(100))
    credit_card_type = db.Column(db.String(30))
    credit_card_last4 = db.Column(db.String(4))
    bank_name = db.Column(db.String(100))
    check_number = db.Column(db.String(50))
    credit_limit = db.Column(db.Numeric(12,2), default=0.00)
    credit_used = db.Column(db.Numeric(12,2), default=0.00)
    balance_due = db.Column(db.Numeric(12,2), default=0.00)
    advance_payment = db.Column(db.Numeric(12,2), default=0.00)
    
    # Shipping Address
    shipping_address_line1 = db.Column(db.String(200))
    shipping_address_line2 = db.Column(db.String(200))
    shipping_address_line3 = db.Column(db.String(200))
    shipping_city = db.Column(db.String(100), index=True)
    shipping_state = db.Column(db.String(100), index=True)
    shipping_zipcode = db.Column(db.String(20))
    shipping_country = db.Column(db.String(100), index=True)
    shipping_county = db.Column(db.String(100))
    shipping_district = db.Column(db.String(100))
    shipping_landmark = db.Column(db.String(200))
    shipping_contact = db.Column(db.String(100))
    shipping_phone = db.Column(db.String(20))
    shipping_email = db.Column(db.String(100))
    shipping_instructions = db.Column(db.Text)
    delivery_instructions = db.Column(db.Text)
    
    # Billing Address
    billing_address_line1 = db.Column(db.String(200))
    billing_address_line2 = db.Column(db.String(200))
    billing_city = db.Column(db.String(100))
    billing_state = db.Column(db.String(100))
    billing_zipcode = db.Column(db.String(20))
    billing_country = db.Column(db.String(100))
    billing_contact = db.Column(db.String(100))
    billing_phone = db.Column(db.String(20))
    billing_email = db.Column(db.String(100))
    same_as_shipping = db.Column(db.Boolean, default=True)
    
    # Shipping & Delivery
    carrier = db.Column(db.String(100), index=True)
    carrier_service = db.Column(db.String(100))
    tracking_number = db.Column(db.String(100), index=True)
    tracking_url = db.Column(db.String(500))
    shipping_method = db.Column(db.String(50))
    service_level = db.Column(db.String(50))
    delivery_date = db.Column(db.Date, index=True)
    delivery_time = db.Column(db.Time)
    delivery_window_start = db.Column(db.Time)
    delivery_window_end = db.Column(db.Time)
    signature_required = db.Column(db.Boolean, default=False)
    signature_obtained = db.Column(db.String(100))
    delivery_proof = db.Column(db.String(200))
    package_weight = db.Column(db.Numeric(10,2))
    package_dimensions = db.Column(db.String(50))
    number_of_packages = db.Column(db.Integer, default=1)
    package_type = db.Column(db.String(50))
    pallet_count = db.Column(db.Integer, default=0)
    container_number = db.Column(db.String(50))
    freight_class = db.Column(db.String(20))
    
    # Warehouse & Dispatch
    warehouse_id = db.Column(db.String(50), index=True)
    warehouse_name = db.Column(db.String(100))
    warehouse_location = db.Column(db.String(200))
    dispatch_date = db.Column(db.Date)
    dispatch_time = db.Column(db.Time)
    dispatcher_name = db.Column(db.String(100))
    dispatch_status = db.Column(db.String(30))
    pick_date = db.Column(db.Date)
    pick_time = db.Column(db.Time)
    picker_name = db.Column(db.String(100))
    pack_date = db.Column(db.Date)
    pack_time = db.Column(db.Time)
    packer_name = db.Column(db.String(100))
    loading_dock = db.Column(db.String(50))
    manifest_number = db.Column(db.String(100))
    
    # Vehicle & Driver
    vehicle_id = db.Column(db.String(50))
    vehicle_type = db.Column(db.String(50))
    vehicle_number = db.Column(db.String(50))
    driver_name = db.Column(db.String(100))
    driver_license = db.Column(db.String(50))
    driver_phone = db.Column(db.String(20))
    driver_email = db.Column(db.String(100))
    route_plan = db.Column(db.Text)
    estimated_arrival = db.Column(db.DateTime)
    actual_arrival = db.Column(db.DateTime)
    
    # Quality & Compliance
    quality_check = db.Column(db.Boolean, default=False)
    qc_inspector = db.Column(db.String(100))
    qc_date = db.Column(db.Date)
    qc_status = db.Column(db.String(30))
    qc_notes = db.Column(db.Text)
    safety_rating = db.Column(db.String(10))
    compliance_cert = db.Column(db.String(100))
    hazmat_class = db.Column(db.String(50))
    special_handling = db.Column(db.String(200))
    temperature_controlled = db.Column(db.Boolean, default=False)
    temperature_range = db.Column(db.String(50))
    regulatory_compliance = db.Column(db.Text)
    
    # Returns & Refunds
    return_eligible = db.Column(db.Boolean, default=True)
    return_window_days = db.Column(db.Integer, default=30)
    return_reason = db.Column(db.Text)
    return_status = db.Column(db.String(30))
    return_date = db.Column(db.Date)
    rma_number = db.Column(db.String(50))
    refund_amount = db.Column(db.Numeric(10,2), default=0.00)
    refund_status = db.Column(db.String(30))
    refund_date = db.Column(db.Date)
    restocking_fee = db.Column(db.Numeric(10,2), default=0.00)
    
    # Customer Service
    csr_assigned = db.Column(db.String(100))
    support_ticket = db.Column(db.String(50))
    complaint_type = db.Column(db.String(100))
    complaint_description = db.Column(db.Text)
    resolution_status = db.Column(db.String(30))
    resolution_date = db.Column(db.Date)
    resolution_notes = db.Column(db.Text)
    escalation_level = db.Column(db.Integer, default=0)
    escalated_to = db.Column(db.String(100))
    follow_up_date = db.Column(db.Date)
    follow_up_required = db.Column(db.Boolean, default=False)
    customer_feedback = db.Column(db.Text)
    customer_rating_service = db.Column(db.Integer)
    nps_score = db.Column(db.Integer)
    satisfaction_score = db.Column(db.Integer)
    
    # Warranty & Service
    warranty_period = db.Column(db.String(50))
    warranty_start_date = db.Column(db.Date)
    warranty_end_date = db.Column(db.Date)
    warranty_claim = db.Column(db.Boolean, default=False)
    warranty_claim_number = db.Column(db.String(50))
    service_contract = db.Column(db.Boolean, default=False)
    installation_required = db.Column(db.Boolean, default=False)
    installation_date = db.Column(db.Date)
    
    # Notifications
    email_sent = db.Column(db.Boolean, default=False)
    sms_sent = db.Column(db.Boolean, default=False)
    notification_sent = db.Column(db.Boolean, default=False)
    confirmation_email_sent = db.Column(db.Boolean, default=False)
    shipping_notification_sent = db.Column(db.Boolean, default=False)
    delivery_notification_sent = db.Column(db.Boolean, default=False)
    notification_preferences = db.Column(db.Text)
    communication_log = db.Column(db.Text)
    
    # Analytics
    conversion_source = db.Column(db.String(100))
    landing_page = db.Column(db.String(500))
    session_id = db.Column(db.String(100))
    user_agent = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    device_type = db.Column(db.String(50))
    browser = db.Column(db.String(50))
    operating_system = db.Column(db.String(50))
    geolocation = db.Column(db.String(200))
    ab_test_variant = db.Column(db.String(50))
    
    # Performance Metrics
    processing_time_minutes = db.Column(db.Integer)
    fulfillment_time_hours = db.Column(db.Integer)
    delivery_time_days = db.Column(db.Integer)
    cycle_time_total_hours = db.Column(db.Integer)
    on_time_delivery = db.Column(db.Boolean)
    perfect_order = db.Column(db.Boolean)
    order_accuracy_score = db.Column(db.Numeric(5,2))
    fulfillment_accuracy = db.Column(db.Numeric(5,2))
    
    # Custom Fields
    custom_field_1 = db.Column(db.String(200))
    custom_field_2 = db.Column(db.String(200))
    custom_field_3 = db.Column(db.String(200))
    custom_field_4 = db.Column(db.String(200))
    custom_field_5 = db.Column(db.String(200))
    custom_field_6 = db.Column(db.String(200))
    custom_field_7 = db.Column(db.String(200))
    custom_field_8 = db.Column(db.String(200))
    custom_field_9 = db.Column(db.String(200))
    custom_field_10 = db.Column(db.String(200))
    custom_text_1 = db.Column(db.Text)
    custom_text_2 = db.Column(db.Text)
    custom_text_3 = db.Column(db.Text)
    custom_number_1 = db.Column(db.Numeric(15,4))
    custom_number_2 = db.Column(db.Numeric(15,4))
    custom_number_3 = db.Column(db.Numeric(15,4))
    custom_date_1 = db.Column(db.Date)
    custom_date_2 = db.Column(db.Date)
    custom_boolean_1 = db.Column(db.Boolean)
    custom_boolean_2 = db.Column(db.Boolean)
    
    # System Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_by = db.Column(db.String(100))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    updated_by = db.Column(db.String(100))
    deleted_at = db.Column(db.DateTime)
    deleted_by = db.Column(db.String(100))
    is_deleted = db.Column(db.Boolean, default=False)
    version = db.Column(db.Integer, default=1)
    last_modified_by = db.Column(db.String(100))
    modification_notes = db.Column(db.Text)

    def to_dict(self):
        out = {}
        for c in self.__table__.columns:
            v = getattr(self, c.name)
            if v is None:
                out[c.name] = None
            elif hasattr(v, "isoformat"):
                out[c.name] = v.isoformat()
            elif isinstance(v, decimal.Decimal):
                out[c.name] = float(v)
            else:
                out[c.name] = v
        return out

# Composite indexes
Index('ix_orders_status_date', Order.order_status, Order.order_date)
Index('ix_orders_channel_date', Order.sales_channel, Order.order_date)
Index('ix_orders_country_state', Order.shipping_country, Order.shipping_state)