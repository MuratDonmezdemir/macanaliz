from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_caching import Cache
from flask_admin import Admin

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
cache = Cache()
admin = Admin(name="MacAnaliz", template_mode="bootstrap4")
