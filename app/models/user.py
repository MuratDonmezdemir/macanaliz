from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from .base import BaseModel
from app.extensions import db, login_manager
from .prediction import Prediction
from sqlalchemy.orm import relationship

class User(UserMixin, BaseModel):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # İlişkiler
    athlete = db.relationship('Athlete', backref='user', uselist=False)
    predictions = db.relationship('Prediction', backref='user', lazy='dynamic')
    notifications = db.Column(db.Boolean, default=True, nullable=False)
    
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
