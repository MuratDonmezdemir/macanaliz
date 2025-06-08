import os
from flask import Flask
from flask_migrate import Migrate
from config import config
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

# Import extensions
from .extensions import db, login_manager, cache

def create_app(config_name='default'):
    """Uygulama fabrika fonksiyonu"""
    app = Flask(__name__)

    # Temel loglama ayarları
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)

    # Konsol log handler'ı ekle
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    app.logger.addHandler(console_handler)

    app.logger.info("Uygulama başlatılıyor...")

    try:
        # Konfigürasyonu yükle
        if config_name not in config:
            raise ValueError(f"Geçersiz konfigürasyon adı: {config_name}")
        
        app.config.from_object(config[config_name])
        config[config_name].init_app(app)
        app.logger.info("Konfigürasyon başarıyla yüklendi")

        # Eklentileri başlat
        db.init_app(app)
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'
        
        cache_config = {
            'CACHE_TYPE': 'simple',
            'CACHE_DEFAULT_TIMEOUT': 300
        }
        cache.init_app(app, config=cache_config)

        Migrate(app, db)

        # Modelleri başlat
        with app.app_context():
            from .models import init_models
            init_models()
            app.logger.info("Modeller başarıyla başlatıldı")
            
    except Exception as e:
        app.logger.error(f"Uygulama başlatılırken hata oluştu: {str(e)}", exc_info=True)
        raise
    
    # Log klasörünü oluştur ve dosya handler'ını ayarla
    try:
        os.makedirs('logs', exist_ok=True)
        
        file_handler = RotatingFileHandler(
            'logs/macanaliz.log',
            maxBytes=10240 * 10,
            backupCount=10,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(file_handler)
    except Exception as e:
        app.logger.error(f"Log dosyası oluşturulurken hata: {str(e)}")

    # Blueprint'leri kaydet
    register_blueprints(app)
    
    # Template filtrelerini kaydet
    register_template_filters(app)
    
    # Hata yöneticilerini kaydet
    register_error_handlers(app)

    return app

def register_blueprints(app):
    """Blueprint'leri kaydeder"""
    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.api.routes import api_bp
    
    # Blueprint'leri kaydet
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)git add .
git commit -m "Proje yapısı güncellendi ve auth sistemi düzeltildi"
git push origin main
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Debug için kayıtlı endpoint'leri göster
    app.logger.info("Kayıtlı endpoint'ler:")
    for rule in app.url_map.iter_rules():
        app.logger.info(f"{rule.endpoint} -> {rule}")

def register_template_filters(app):
    """Template filtrelerini kaydeder"""
    @app.template_filter('datetimeformat')
    def datetimeformat(value, format='%Y-%m-%d %H:%M'):
        if value is None:
            return ""
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                return value
        return value.strftime(format)
    
    @app.template_filter('round')
    def round_filter(value, decimals=0):
        if value is None:
            return ""
        try:
            return round(float(value), decimals)
        except (ValueError, TypeError):
            return value

def register_error_handlers(app):
    """Hata yöneticilerini kaydeder"""
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def server_error(error):
        app.logger.error(f'Server Error: {error}', exc_info=True)
        return {'error': 'Internal server error'}, 500
