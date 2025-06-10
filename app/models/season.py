from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey

from .base import BaseModel
from app.extensions import db

class Season(BaseModel):
    """Sezon modeli"""
    __tablename__ = 'seasons'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_current = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'))
    
    # İlişkiler
    league = db.relationship('League', back_populates='seasons')
    matches = db.relationship('Match', back_populates='season', lazy='dynamic')
    standings = db.relationship('Standing', back_populates='season', lazy='dynamic')
    team_statistics = db.relationship('TeamStatistics', back_populates='season', lazy='dynamic')
    
    def __repr__(self):
        return f'<Season {self.name}>'
    
    def to_dict(self):
        """Sezon bilgilerini sözlük olarak döndürür"""
        return {
            'id': self.id,
            'name': self.name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_current': self.is_current
        }
