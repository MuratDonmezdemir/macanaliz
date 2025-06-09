from flask import render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from ..models import Match, Team, db, User, Prediction
from datetime import datetime, timedelta
from . import main_bp
from .forms import ProfileForm, ChangePasswordForm
from .. import db
from werkzeug.security import generate_password_hash

@main_bp.route('/')
@main_bp.route('/index')
def index():
    # Yaklaşan maçları getir (önümüzdeki 7 gün içindeki maçlar)
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=7)
    
    matches = Match.query.filter(
        Match.match_date >= start_date,
        Match.match_date <= end_date
    ).order_by(Match.match_date).limit(10).all()
    
    return render_template('main/index.html', 
                         title='Ana Sayfa',
                         matches=matches)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Yaklaşan maçları getir (önümüzdeki 7 gün içindeki maçlar)
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=7)
    
    matches = Match.query.filter(
        Match.match_date >= start_date,
        Match.match_date <= end_date
    ).order_by(Match.match_date).limit(10).all()
    
    return render_template('main/dashboard.html', 
                         title='Kontrol Paneli',
                         matches=matches)

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile_form = ProfileForm(obj=current_user)
    password_form = ChangePasswordForm()
    
    if profile_form.validate_on_submit() and 'update_profile' in request.form:
        current_user.username = profile_form.username.data
        current_user.email = profile_form.email.data
        current_user.notifications = profile_form.notifications.data
        db.session.commit()
        flash('Profil bilgileriniz başarıyla güncellendi.', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('main/profile.html', 
                         title='Profil',
                         profile_form=profile_form,
                         password_form=password_form)

@main_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    password_form = ChangePasswordForm()
    
    if password_form.validate_on_submit():
        if current_user.check_password(password_form.current_password.data):
            current_user.password_hash = generate_password_hash(password_form.new_password.data)
            db.session.commit()
            flash('Şifreniz başarıyla değiştirildi.', 'success')
        else:
            flash('Mevcut şifreniz yanlış.', 'danger')
    else:
        for field, errors in password_form.errors.items():
            for error in errors:
                flash(f'{getattr(password_form, field).label.text}: {error}', 'danger')
    
    return redirect(url_for('main.profile'))
