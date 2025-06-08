from datetime import datetime
from .base import BaseModel
from app.extensions import db

class Stadium(BaseModel):
    """Stadyum modeli"""
    __tablename__ = 'stadiums'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50))
    country = db.String(50)
    capacity = db.Column(db.Integer)
    address = db.Column(db.String(200))
    opened = db.Column(db.Integer)  # Yıl olarak açılış tarihi
    surface = db.Column(db.String(50))
    image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    teams = db.relationship('Team', back_populates='stadium')
    matches = db.relationship('Match', back_populates='stadium')
    
    def __repr__(self):
        return f'<Stadium {self.name}>'
    
    def to_dict(self):
        """Stadyum bilgilerini sözlük olarak döndürür"""
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'country': self.country,
            'capacity': self.capacity,
            'opened': self.opened
        }
