from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
import decimal

db = SQLAlchemy()
migrate = Migrate()
cache = Cache()

def init_app(app):
    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    try:
        with app.app_context():
            db.create_all()
            print("✓ Database tables ensured.")
    except Exception as e:
        print("DB init error:", e)

def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError