from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

from . import routes  # Bu satır en sonda olmalı
