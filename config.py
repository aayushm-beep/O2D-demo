import os
from datetime import timedelta

class Config:
    """Application configuration with performance optimizations"""
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'dpg-d3kussl6ubrc738thlq0-a')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_USER = os.getenv('DB_USER', 'order_dispatch_db_user')
    DB_PASS = os.getenv('DB_PASS', 'tiuuNCy1n0JYEEl02EozDFnEiIKN7eJM')
    DB_NAME = os.getenv('DB_NAME', 'order_dispatch_db')
    
    # SQLAlchemy Configuration with Performance Optimizations
    # Base URI - will be overridden in ProductionConfig
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///default.db")
    
    # Fix postgres:// to postgresql:// for SQLAlchemy compatibility
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Set to True for debugging
    
    # Connection Pool Settings for Better Performance
    SQLALCHEMY_POOL_SIZE = 20
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_POOL_RECYCLE = 3600
    SQLALCHEMY_MAX_OVERFLOW = 40
    SQLALCHEMY_POOL_PRE_PING = True

    # Session
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False

    # Caching
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Cache Configuration (Flask-Caching)
    CACHE_KEY_PREFIX = 'dispatch_'
    
    # Redis Cache (if using Redis)
    CACHE_REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    CACHE_REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    CACHE_REDIS_DB = int(os.getenv('REDIS_DB', 0))
    CACHE_REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    
    # JSON Configuration
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    
    # Compression
    COMPRESS_MIMETYPES = ['application/json','text/html','text/css','application/javascript']
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 1024
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'pdf', 'png', 'jpg', 'jpeg'}
    
    # Pagination
    ITEMS_PER_PAGE = 25
    MAX_ITEMS_PER_PAGE = 100
    
    # API Rate Limiting (if using Flask-Limiter)
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')
    
    # Email Configuration (for password reset, notifications)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_SENDER', 'noreply@dispatchpro.com')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    
    # Security Headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Application Settings
    APP_NAME = 'DispatchPro'
    APP_VERSION = '2.0.0'
    TIMEZONE = 'Asia/Kolkata'
    CURRENCY = 'INR'
    
    # Google Sheets Configuration
    GOOGLE_SA_JSON = os.getenv("GOOGLE_SA_JSON", "").strip()
    GOOGLE_SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID", "1Jf8YNR1YA56uIEbxRR-v1ux5wOMu3zefXBBGhFvWpoI").strip()
    
    # Tab names
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
        # Create upload folder if it doesn't exist
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # Set security headers
        @app.after_request
        def set_security_headers(response):
            for header, value in Config.SECURITY_HEADERS.items():
                response.headers[header] = value
            return response


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    CACHE_TYPE = 'SimpleCache'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'SimpleCache')
    SESSION_COOKIE_SECURE = True
    
    # Use environment variables for sensitive data
    SECRET_KEY = os.getenv('SECRET_KEY', Config.SECRET_KEY)
    
    # Database URL - Render provides this as DATABASE_URL
    DATABASE_URL = os.getenv('DATABASE_URL', '')
    
    # Fix Render's postgres:// to postgresql://
    if DATABASE_URL:
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Fallback to MySQL with individual env vars
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:"
            f"{os.getenv('DB_PASS', 'root')}@"
            f"{os.getenv('DB_HOST', 'localhost')}:"
            f"{os.getenv('DB_PORT', '3306')}/"
            f"{os.getenv('DB_NAME', 'order_dispatch_db')}"
            "?charset=utf8mb4"
        )


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
