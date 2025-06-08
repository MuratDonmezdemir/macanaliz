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
    """Application factory function."""
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
        # Load configuration
        if config_name not in config:
            raise ValueError(f"Geçersiz konfigürasyon adı: {config_name}")
        
        app.config.from_object(config[config_name])
        config[config_name].init_app(app)
        app.logger.info("Konfigürasyon başarıyla yüklendi")

        # Initialize extensions
        db.init_app(app)
        login_manager.init_app(app)
        
        cache_config = {
            'CACHE_TYPE': 'simple',
            'CACHE_DEFAULT_TIMEOUT': 300
        }
        cache.init_app(app, config=cache_config)

        Migrate(app, db)
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

    # Modelleri import et
    from .models import base, stadium, league, team, match, user

    # Blueprint'leri import et
    from .routes.main import bp as main_bp
    from .routes.auth import bp as auth_bp
    from .routes.api import api_bp

    # Blueprint'leri kaydet
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Template filters
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
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def server_error(error):
        app.logger.error(f'Server Error: {error}', exc_info=True)
        return {'error': 'Internal server error'}, 500

    return app
