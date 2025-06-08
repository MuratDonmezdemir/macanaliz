from .. import db
from datetime import datetime

class Athlete(db.Model):
    __tablename__ = 'athletes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    date_of_birth = db.Column(db.Date)
    weight = db.Column(db.Float)  # kg cinsinden
    height = db.Column(db.Float)   # cm cinsinden
    experience_level = db.Column(db.String(32))  # Başlangıç, Orta, İleri, Profesyonel
    dominant_side = db.Column(db.String(10))  # right, left
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    equipment = db.relationship('Equipment', backref='athlete', lazy='dynamic')
    race_results = db.relationship('RaceResult', backref='athlete', lazy='dynamic')
    
    def __repr__(self):
        return f'<Athlete {self.first_name} {self.last_name}>'
