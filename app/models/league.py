from app.models.base import BaseModel
from app import db

class League(BaseModel):
    """League model representing football leagues."""
    __tablename__ = 'leagues'
    
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    level = db.Column(db.Integer, default=1)  # 1: Premier League, 2: Championship, etc.
    logo = db.Column(db.String(200))
    current_season = db.Column(db.String(20))  # Example: 2024-2025
    
    # Relationships
    country = db.relationship('Country', back_populates='leagues')
    teams = db.relationship('Team', back_populates='league', lazy='dynamic')
    matches = db.relationship('Match', back_populates='league', lazy='dynamic')
    
    def __repr__(self):
        return f'<League {self.name}>'
