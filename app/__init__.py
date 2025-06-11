import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import current_user
from config import Config
import logging
from logging.handlers import RotatingFileHandler
from apscheduler.schedulers.background import BackgroundScheduler
# Döngüsel import sorununu önlemek için DataCollector'ü fonksiyon içinde import ediyoruz

# Uzantıları içe aktar
from .extensions import db, login_manager, cache, admin

# Migrate'i başlat
migrate = Migrate()


def create_app(config_class=Config):
    """Uygulama fabrika fonksiyonu"""
    app = Flask(__name__)

    # Konfigürasyonu yükle
    app.config.from_object(config_class)
    if hasattr(config_class, "init_app"):
        config_class.init_app(app)

    # Loglama ayarlarını yapılandır
    configure_logging(app)

    # Uzantıları başlat
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    cache.init_app(app)

    # Modeller arası ilişkileri başlat
    with app.app_context():
        from app.models import init_models

        init_models()

    # Admin panelini başlat
    from .admin import init_app as init_admin

    init_admin(app)

    # Blueprint'leri kaydet
    register_blueprints(app)

    # Template filtrelerini kaydet
    register_template_filters(app)

    # Hata yöneticilerini kaydet
    register_error_handlers(app)

    # Shell context
    @app.shell_context_processor
    def make_shell_context():
        from app.models import Match, Team, Prediction

        return {"db": db, "Match": Match, "Team": Team, "Prediction": Prediction}

    return app


def configure_logging(app):
    """Uygulama loglama ayarlarını yapılandırır"""
    logging.basicConfig(
        level=getattr(logging, app.config.get("LOG_LEVEL", "INFO")),
        format=app.config.get("LOG_FORMAT", "%(asctime)s %(levelname)s: %(message)s"),
    )

    # Dosyaya loglama
    if not app.debug and not app.testing:
        try:
            os.makedirs("logs", exist_ok=True)
            file_handler = RotatingFileHandler(
                "logs/macanaliz.log",
                maxBytes=10240 * 10,  # 10KB
                backupCount=10,
                encoding="utf-8",
            )
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
                )
            )
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info("MacAnaliz başlatılıyor...")
        except Exception as e:
            if "app" in locals() and hasattr(app, "logger"):
                app.logger.error(f"Log dosyası oluşturulurken hata: {str(e)}")


def register_blueprints(app):
    """Blueprint'leri uygulamaya kaydeder"""
    try:
        # Sadece temel blueprint'leri içe aktar
        from app.main.routes import main_bp
        from app.api.routes import api_bp

        # Blueprint'leri kaydet
        app.register_blueprint(main_bp)
        app.register_blueprint(api_bp, url_prefix="/api")

        # Debug için kayıtlı endpoint'leri göster
        app.logger.info("Kayıtlı endpoint'ler:")
        for rule in app.url_map.iter_rules():
            app.logger.info(f"{rule.endpoint} -> {rule}")
    except ImportError as e:
        if "app" in locals() and hasattr(app, "logger"):
            app.logger.warning(f"Blueprint yüklenirken hata: {str(e)}")
            app.logger.exception(e)


def register_template_filters(app):
    """Template filtrelerini kaydeder"""

    @app.template_filter("datetimeformat")
    def datetimeformat(value, format="%Y-%m-%d %H:%M"):
        if value is None:
            return ""
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                return value
        return value.strftime(format) if hasattr(value, "strftime") else str(value)

    @app.template_filter("round")
    def round_filter(value, decimals=0):
        if value is None:
            return ""
        try:
            return round(float(value), int(decimals))
        except (ValueError, TypeError):
            return value


def register_error_handlers(app):
    """Hata yöneticilerini kaydeder"""

    @app.errorhandler(404)
    def not_found_error(error):
        if request.headers.get("Content-Type") == "application/json":
            return {"error": "Not found"}, 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        if hasattr(db, "session"):
            db.session.rollback()
        if request.headers.get("Content-Type") == "application/json":
            return {"error": "Internal server error"}, 500
        return render_template("errors/500.html"), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        if request.headers.get("Content-Type") == "application/json":
            return {"error": "Forbidden"}, 403
        return render_template("errors/403.html"), 403


# Uygulama başlatıldığında çalışacak kod
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
