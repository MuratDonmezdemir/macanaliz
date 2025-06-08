from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import main_bp

@main_bp.route('/')
@main_bp.route('/index')
def index():
    return render_template('main/index.html', title='Ana Sayfa')

@main_bp.route('/profile')
@login_required
def profile():
    return render_template('main/profile.html', title='Profil')
