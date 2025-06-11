import os
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Ana dizin
basedir = Path(__file__).parent


class Config:
    # Uygulama ayarları
    SECRET_KEY = os.environ.get("SECRET_KEY") or "gizli-anahtar-buraya"
    DEBUG = os.environ.get("FLASK_DEBUG", "False") == "True"

    # Veritabanı ayarları
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL") or f"sqlite:///{os.path.join(basedir, 'app.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 10,
        "max_overflow": 20,
    }

    # API Ayarları
    FOOTBALL_API_KEY = os.environ.get("FOOTBALL_API_KEY")
    FOOTBALL_API_BASE_URL = "https://api.football-data.org/v4"

    # RapidAPI Ayarları
    RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
    RAPIDAPI_HOST = "api-football-v1.p.rapidapi.com"
    RAPIDAPI_BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"

    # Desteklenen Ligler
    LEAGUES = {
        "TR1": {"name": "Süper Lig", "country": "Türkiye"},
        "PL": {"name": "Premier League", "country": "İngiltere"},
        "PD": {"name": "La Liga", "country": "İspanya"},
        "SA": {"name": "Serie A", "country": "İtalya"},
        "BL1": {"name": "Bundesliga", "country": "Almanya"},
        "FL1": {"name": "Ligue 1", "country": "Fransa"},
        "PPL": {"name": "Primeira Liga", "country": "Portekiz"},
        "ERED": {"name": "Eredivisie", "country": "Hollanda"},
    }

    # Uygulama Ayarları
    ITEMS_PER_PAGE = 20
    MODEL_DIR = os.path.join(basedir, "models")
    DATA_DIR = os.path.join(basedir, "data")

    # Loglama Ayarları
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @classmethod
    def init_app(cls, app):
        """Uygulama başlatıldığında çalışacak ayarlar"""
        # Klasörleri oluştur
        for directory in [cls.MODEL_DIR, cls.DATA_DIR]:
            os.makedirs(directory, exist_ok=True)


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 20,
        "max_overflow": 10,
    }


# Konfigürasyon sözlüğü
config = {
    "development": DevelopmentConfig(),
    "testing": TestingConfig(),
    "production": ProductionConfig(),
    "default": DevelopmentConfig(),
}
