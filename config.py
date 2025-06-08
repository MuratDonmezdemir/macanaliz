import os
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Temel dizin
basedir = Path(__file__).parent.resolve()

class Config:
    # Genel yapılandırma
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gizli-anahtar-buraya-12345'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SQLite yapılandırması (geliştirme için)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'windsurf.db')
    
    # API Ayarları
    OPENMETEO_API_URL = 'https://api.open-meteo.com/v1/forecast'
    
    # Yol ayarları
    MODEL_PATH = basedir / 'models'
    DATA_PATH = basedir / 'data'
    
    # Sayfalama
    ITEMS_PER_PAGE = 20
    
    # Güvenlik
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False
    # Üretimde MySQL veya PostgreSQL kullanılabilir
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #     'mysql+pymysql://user:password@localhost/windsurf_prod'

# Konfigürasyon sözlüğü
config = {
    'development': DevelopmentConfig(),
    'testing': TestingConfig(),
    'production': ProductionConfig(),
    'default': DevelopmentConfig()
}
