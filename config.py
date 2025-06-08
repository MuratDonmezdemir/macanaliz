import os
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Temel dizin
basedir = Path(__file__).parent.resolve()

class Config:
    # Genel yapılandırma
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError('SECRET_KEY ortam değişkeni ayarlanmamış')
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    @staticmethod
    def init_app(app):
        pass
    
    # SQLite yapılandırması (geliştirme için)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'macanaliz.db')
    
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
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'dev.db')
    
    # Geliştirme için güvenlik ayarlarını gevşet
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False
    
    # Üretimde PostgreSQL kullanımı önerilir
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError('DATABASE_URL ortam değişkeni ayarlanmamış')
    
    # Güvenlik ayarları
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Performans ayarları
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 20,
        'max_overflow': 10,
    }

# Konfigürasyon sözlüğü
config = {
    'development': DevelopmentConfig(),
    'testing': TestingConfig(),
    'production': ProductionConfig(),
    'default': DevelopmentConfig()
}
