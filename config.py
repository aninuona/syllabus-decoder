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
    SESSION_COOKIE_SECURE = False   # False for http localhostsqlite3 syllabus.db "PRAGMA table_info(syllabus_entries);"

    # SQLALCHEMY_DATABASE_URI = "sqlite:///syllabus.db"

    # Disable modification tracking to save memory
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEBUG = True


class ProductionConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    # For Neon: DATABASE_URL already starts with "postgresql://"
    database_url = os.environ.get("DATABASE_URL", "")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True


# Dictionary so app.py can look up the right config by environment name
config = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
}
