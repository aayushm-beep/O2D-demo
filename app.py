import os
from flask import Flask, render_template, jsonify, request, Response, session, redirect, url_for
from flask_compress import Compress
from functools import wraps
from datetime import datetime, timedelta, date
from sqlalchemy import func, cast, Date, or_
import decimal
import hashlib
import secrets

# Initialize Flask app
app = Flask(__name__)

# Load configuration based on environment
ENV = os.getenv('FLASK_ENV', 'production')

if ENV == 'production':
    from config import ProductionConfig
    app.config.from_object(ProductionConfig)
    print("✅ Loaded ProductionConfig")
else:
    from config import DevelopmentConfig
    app.config.from_object(DevelopmentConfig)
    print("✅ Loaded DevelopmentConfig")

# Initialize app-specific configurations
from config import Config
Config.init_app(app)

# Enable HTTP compression
Compress(app)

# Initialize database and cache
from database import db, init_app, cache
init_app(app)

# Import models
from models import Order, User, Warehouse, Product, Customer, Shipment

# Register API routes if available
try:
    from api_routes import api
    app.register_blueprint(api)
    print("✅ API routes registered")
except ImportError:
    print("⚠️ API routes not found, skipping")

# Helper functions
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def as_float(v, default=0.0):
    if v is None:
        return default
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, decimal.Decimal):
        return float(v)
    try:
        return float(v)
    except:
        return default

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Auth routes
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.json or request.form
        user = User.query.filter_by(username=data.get('username')).first()
        if user and user.password == hash_password(data.get('password')):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return jsonify({"success": True, "redirect": url_for('home')})
        return jsonify({"success": False, "error": "Invalid credentials"}), 401
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

# Page routes
@app.route("/")
@login_required
def home():
    return render_template("dashboard.html", username=session.get('username'))

@app.route("/orders")
@login_required
def orders_page():
    return render_template("orders.html")

@app.route("/customers")
@login_required
def customers_page():
    return render_template("customers.html")

@app.route("/products")
@login_required
def products_page():
    return render_template("products.html")

@app.route("/warehouse")
@login_required
def warehouse_page():
    return render_template("warehouse.html")

@app.route("/shipments")
@login_required
def shipments_page():
    return render_template("shipments.html")

@app.route("/analytics")
@login_required
def analytics_page():
    return render_template("analytics.html")

@app.route("/settings")
@login_required
def settings_page():
    return render_template("settings.html")

@app.route('/forecast')
@login_required
def forecast_page():
    return render_template('forecast.html')

# OPTIMIZED API endpoints
@app.get("/api/metrics/summary")
@login_required
@cache.cached(timeout=30)
def api_metrics_summary():
    today = date.today()
    week_ago = today - timedelta(days=7)
    
    total_orders = db.session.query(func.count(Order.order_id)).scalar() or 0
    revenue_7d = db.session.query(func.coalesce(func.sum(Order.total_amount), 0)).filter(Order.order_date >= week_ago).scalar() or 0
    open_orders = db.session.query(func.count(Order.order_id)).filter(Order.order_status.in_(["Pending", "Processing"])).scalar() or 0
    avg_order_value = db.session.query(func.coalesce(func.avg(Order.total_amount), 0)).scalar() or 0
    
    return jsonify({
        "total_orders": int(total_orders),
        "revenue_7d": float(revenue_7d),
        "open_orders": int(open_orders),
        "avg_order_value": float(avg_order_value)
    })

# OPTIMIZED Orders API - Pagination with selected columns only
@app.get("/api/orders/data")
@login_required
def api_orders_data():
    try:
        page = max(1, int(request.args.get("page", 1)))
        page_size = min(100, max(10, int(request.args.get("page_size", 25))))
        
        # Filters
        search = request.args.get("search", "").strip()
        status = request.args.get("status", "").strip()
        priority = request.args.get("priority", "").strip()
        
        # Build query - SELECT only needed columns for performance
        query = db.session.query(
            Order.order_id,
            Order.customer_name,
            Order.customer_email,
            Order.product_name,
            Order.order_status,
            Order.priority_level,
            Order.total_amount,
            Order.order_date,
            Order.quantity,
            Order.payment_status,
            Order.shipping_city,
            Order.shipping_state,
            Order.carrier,
            Order.tracking_number
        )
        
        # Apply filters
        if search:
            like = f"%{search}%"
            query = query.filter(or_(
                Order.order_id.ilike(like),
                Order.customer_name.ilike(like),
                Order.product_name.ilike(like)
            ))
        
        if status:
            query = query.filter(Order.order_status == status)
        
        if priority:
            query = query.filter(Order.priority_level == priority)
        
        # Get total count
        total = query.count()
        
        # Paginate
        orders = query.order_by(Order.order_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        # Serialize efficiently
        data = []
        for o in orders:
            data.append({
                "order_id": o[0],
                "customer_name": o[1],
                "customer_email": o[2],
                "product_name": o[3],
                "order_status": o[4],
                "priority_level": o[5],
                "total_amount": float(o[6]) if o[6] else 0,
                "order_date": o[7].isoformat() if o[7] else None,
                "quantity": o[8],
                "payment_status": o[9],
                "shipping_city": o[10],
                "shipping_state": o[11],
                "carrier": o[12],
                "tracking_number": o[13]
            })
        
        return jsonify({
            "orders": data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        })
        
    except Exception as e:
        print(f"Orders API Error: {e}")
        return jsonify({"error": str(e)}), 500

# Dashboard data - optimized
@app.route("/api/dashboard/data")
@login_required
@cache.cached(timeout=60)
def dashboard_data():
    try:
        # Metrics
        total_orders = db.session.query(func.count(Order.order_id)).scalar() or 0
        total_revenue = db.session.query(func.coalesce(func.sum(Order.total_amount), 0)).scalar() or 0
        pending_orders = db.session.query(func.count(Order.order_id)).filter_by(order_status="Pending").scalar() or 0
        delivered_today = db.session.query(func.count(Order.order_id)).filter(
            Order.delivery_date == date.today(),
            Order.order_status == "Delivered"
        ).scalar() or 0
        
        # Recent orders - limit columns
        recent = db.session.query(
            Order.order_id, Order.customer_name, Order.product_name, 
            Order.order_status, Order.total_amount, Order.order_date
        ).order_by(Order.order_date.desc()).limit(10).all()
        
        recent_orders = [{
            "order_id": r[0],
            "customer_name": r[1],
            "product_name": r[2],
            "order_status": r[3],
            "total_amount": float(r[4]) if r[4] else 0,
            "order_date": r[5].isoformat() if r[5] else None
        } for r in recent]
        
        # Status distribution
        status_data = db.session.query(
            Order.order_status, func.count(Order.order_id)
        ).group_by(Order.order_status).all()
        
        status_counts = {s[0]: s[1] for s in status_data}
        
        # Performance data - last 7 days
        week_ago = date.today() - timedelta(days=6)
        perf_data = db.session.query(
            cast(Order.order_date, Date).label("d"),
            func.count(Order.order_id).label("cnt")
        ).filter(Order.order_date >= week_ago).group_by("d").order_by("d").all()
        
        labels = []
        orders_data = []
        for i in range(7):
            day = date.today() - timedelta(days=6-i)
            labels.append(day.strftime("%b %d"))
            count = next((p[1] for p in perf_data if p[0] == day), 0)
            orders_data.append(count)
        
        return jsonify({
            "metrics": {
                "total_revenue": float(total_revenue),
                "total_orders": total_orders,
                "pending_orders": pending_orders,
                "delivered_today": delivered_today
            },
            "recent_orders": recent_orders,
            "chart_data": {
                "performance": {
                    "labels": labels,
                    "orders_data": orders_data
                },
                "status_distribution": {
                    "labels": list(status_counts.keys()),
                    "data": list(status_counts.values())
                }
            }
        })
    except Exception as e:
        print(f"Dashboard error: {e}")
        return jsonify({"error": str(e)}), 500

# Customers API
@app.route("/api/customers", methods=["GET"])
@login_required
@cache.cached(timeout=120, query_string=True)
def api_customers():
    try:
        customers = db.session.query(Customer).limit(1000).all()
        return jsonify({"customers": [c.to_dict() for c in customers]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Products API
@app.route("/api/products", methods=["GET"])
@login_required
@cache.cached(timeout=120, query_string=True)
def api_products():
    try:
        products = db.session.query(Product).limit(1000).all()
        return jsonify({"products": [p.to_dict() for p in products]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# CSV Export - optimized
@app.get("/api/export/csv")
@login_required
def api_export_csv():
    try:
        from io import StringIO
        import csv
        
        search = request.args.get("search", "").strip()
        status = request.args.get("status", "").strip()
        priority = request.args.get("priority", "").strip()
        
        query = db.session.query(Order)
        
        if search:
            like = f"%{search}%"
            query = query.filter(or_(
                Order.order_id.ilike(like),
                Order.customer_name.ilike(like)
            ))
        if status:
            query = query.filter(Order.order_status == status)
        if priority:
            query = query.filter(Order.priority_level == priority)
        
        orders = query.order_by(Order.order_date.desc()).limit(5000).all()
        
        output = StringIO()
        writer = csv.writer(output)
        
        headers = ["Order ID", "Customer", "Product", "Status", "Amount", "Date"]
        writer.writerow(headers)
        
        for o in orders:
            writer.writerow([
                o.order_id,
                o.customer_name,
                o.product_name,
                o.order_status,
                float(o.total_amount) if o.total_amount else 0,
                o.order_date.isoformat() if o.order_date else ""
            ])
        
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename=orders_{date.today()}.csv"}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            data = request.json or request.form
            if User.query.filter_by(username=data.get('username')).first():
                return jsonify({"success": False, "error": "Username exists"}), 400
            
            new_user = User(
                username=data.get('username'),
                password=hash_password(data.get('password')),
                email=data.get('email'),
                full_name=f"{data.get('firstName','')} {data.get('lastName','')}".strip(),
                phone=data.get('phone'),
                role='user'
            )
            db.session.add(new_user)
            db.session.commit()
            return jsonify({"success": True})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500
    return render_template("register.html")

@app.route("/api/register", methods=["POST"])
def api_register():
    return register()

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        return jsonify({"success": True, "message": "Reset link sent"})
    return render_template("forgot_password.html")

@app.route("/api/forgot-password", methods=["POST"])
def api_forgot_password():
    return forgot_password()

@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if request.method == "POST":
        return jsonify({"success": True})
    return render_template("reset_password.html", token=token)

@app.route("/api/init")
def init_data():
    try:
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password=hash_password('admin123'),
                role='admin',
                email='admin@dispatchpro.com'
            )
            db.session.add(admin)
            db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Health check endpoint for Render
@app.route("/health")
def health():
    return jsonify({"status": "healthy", "version": "2.0.0"}), 200

# Optional Google Sheets integration
try:
    from sheets_sync import export_table, import_table
    SHEETS_AVAILABLE = True
    print("✓ Google Sheets integration loaded successfully")
except ImportError as e:
    print(f"⚠ Google Sheets not available: {e}")
    SHEETS_AVAILABLE = False
    def export_table(*args, **kwargs):
        return 0, 0
    def import_table(*args, **kwargs):
        return {"error": "Sheets integration not configured"}
except Exception as e:
    print(f"⚠ Google Sheets error: {e}")
    SHEETS_AVAILABLE = False
    def export_table(*args, **kwargs):
        return 0, 0
    def import_table(*args, **kwargs):
        return {"error": str(e)}

@app.post("/admin/sync/export/<entity>")
@login_required
def sync_export(entity):
    entity = entity.lower()
    if entity not in ("orders","products","customers","warehouses","shipments"):
        return jsonify({"error":"unknown entity"}), 400
    try:
        rows, cols = export_table(db.session, entity)
        return jsonify({"ok": True, "entity": entity, "rows": rows, "cols": cols})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.post("/admin/sync/import/<entity>")
@login_required
def sync_import(entity):
    entity = entity.lower()
    if entity not in ("orders","products","customers","warehouses","shipments"):
        return jsonify({"error":"unknown entity"}), 400
    try:
        stats = import_table(db.session, entity)
        return jsonify({"ok": True, "entity": entity, **stats})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/sheets")
@login_required
def sheets_page():
    sid = app.config.get("GOOGLE_SPREADSHEET_ID", "") or "1Jf8YNR1YA56uIEbxRR-v1ux5wOMu3zefXBBGhFvWpoI"
    return render_template("sheets.html", spreadsheet_id=sid)

@app.get("/admin/sync/check")
@login_required
def sync_check():
    ok = True
    issues = []
    
    if not SHEETS_AVAILABLE:
        ok = False
        issues.append("Google Sheets dependencies not installed (gspread missing)")
        return jsonify({"ok": ok, "issues": issues})
    
    sa_json = app.config.get('GOOGLE_SA_JSON', '')
    if not sa_json:
        ok = False
        issues.append("GOOGLE_SA_JSON not set in environment")
    elif sa_json and os.path.isfile(sa_json):
        pass
    elif sa_json and sa_json.startswith('{'):
        pass
    else:
        ok = False
        issues.append(f"GOOGLE_SA_JSON is neither a valid file nor JSON content")
    
    spreadsheet_id = app.config.get('GOOGLE_SPREADSHEET_ID', '')
    if not spreadsheet_id:
        ok = False
        issues.append("GOOGLE_SPREADSHEET_ID not set")
    
    return jsonify({"ok": ok, "issues": issues})

# Main entry point
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = app.config.get('DEBUG', False)
    app.run(host="0.0.0.0", port=port, debug=debug)