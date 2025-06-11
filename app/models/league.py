from ..extensions import db
from .base import BaseModel

class League(BaseModel):
    """Futbol liglerini temsil eden model."""
    __tablename__ = 'leagues'
    
    name = db.Column(db.String(100), nullable=False, unique=True)
    country = db.Column(db.String(50))
    logo = db.Column(db.String(255))
    
    # İlişkiler
    matches = db.relationship('Match', backref='league', lazy=True)
    
    def __repr__(self):
        return f'<League {self.name}>'
