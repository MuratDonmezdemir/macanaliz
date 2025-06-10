from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship, backref
from app.models.prediction import Prediction

from .base import BaseModel
from app.extensions import db, login_manager

class User(UserMixin, BaseModel):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    athlete = db.relationship('Athlete', back_populates='user', uselist=False)
    predictions = db.relationship('Prediction', back_populates='user', lazy='dynamic')
    notifications = db.Column(db.Boolean, default=True, nullable=False)
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if 'password' in kwargs:
            self.set_password(kwargs['password'])
    
    def set_password(self, password):
        """Şifreyi hash'leyerek kaydeder"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Girilen şifrenin doğruluğunu kontrol eder"""
        return check_password_hash(self.password_hash, password)
    
    def get_prediction_accuracy(self):
        """Kullanıcının tahmin başarı oranını hesaplar"""
        total_predictions = self.predictions.count()
        if total_predictions == 0:
            return 0
        
        correct_predictions = self.predictions.filter_by(is_correct=True).count()
        return (correct_predictions / total_predictions) * 100
    
    def get_ranking(self):
        """Kullanıcının genel sıralamasını döndürür"""
        # Burada daha karmaşık bir sıralama algoritması kullanılabilir
        users = User.query.order_by(User.predictions.desc()).all()
        for i, user in enumerate(users, 1):
            if user.id == self.id:
                return i
        return None
    
    def get_recent_predictions(self, limit=5):
        """Son tahminleri getirir"""
        return self.predictions.order_by(Prediction.created_at.desc()).limit(limit).all()
    
    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
