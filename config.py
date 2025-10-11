import os
from datetime import timedelta

class Config:
    """Application configuration with performance optimizations"""
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASS = os.getenv('DB_PASS', '')
    DB_NAME = os.getenv('DB_NAME', 'order_dispatch_db')
    
    # SQLAlchemy Configuration with Performance Optimizations
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///default.db")
    
    # Fix postgres:// to postgresql:// for SQLAlchemy compatibility
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "pool_size": 10,
        "max_overflow": 20,
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Session
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False

    # Caching
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(24).hex())
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False  # Set True only with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Cache Configuration
    CACHE_KEY_PREFIX = 'dispatch_'
    
    # JSON Configuration
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    
    # Compression
    COMPRESS_MIMETYPES = ['application/json','text/html','text/css','application/javascript']
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 1024
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'pdf', 'png', 'jpg', 'jpeg'}
    
    # Pagination
    ITEMS_PER_PAGE = 25
    MAX_ITEMS_PER_PAGE = 100
    
    # Application Settings
    APP_NAME = 'DispatchPro'
    APP_VERSION = '2.0.0'
    TIMEZONE = 'Asia/Kolkata'
    CURRENCY = 'INR'
    
    # Google Sheets Configuration
    GOOGLE_SA_JSON = os.getenv("GOOGLE_SA_JSON", "").strip()
    GOOGLE_SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID", "").strip()
    
    SHEETS_TABS = {
        "orders": "Orders",
        "products": "Products",
        "customers": "Customers",
        "warehouses": "Warehouses",
        "shipments": "Shipments",
    }
    
    @staticmethod
    def init_app(app):
        """Initialize application with config"""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    CACHE_TYPE = 'SimpleCache'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    CACHE_TYPE = 'SimpleCache'
    SESSION_COOKIE_SECURE = False  # Set True with HTTPS
    
    SECRET_KEY = os.getenv('SECRET_KEY', Config.SECRET_KEY)
    
    # Database URL from Render
    DATABASE_URL = os.getenv('DATABASE_URL', '')
    
    if DATABASE_URL:
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'