import os

# Absolute path to the directory containing this file
_BASE_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
_DB_PATH  = os.path.join(_BASE_DIR, "syllabus.db")

class DevelopmentConfig:
    # Secret key for session security, CHANGE
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-before-deploying")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + _DB_PATH
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-before-deploying")
    
    # Try to use DATABASE_URL if provided (e.g., from PostgreSQL service on Render)
    database_url = os.environ.get("DATABASE_URL", "").strip()
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    # If DATABASE_URL not set, fall back to SQLite
    if database_url:
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + _DB_PATH
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True


# Dictionary so app.py can look up the right config by environment name
config = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
}
