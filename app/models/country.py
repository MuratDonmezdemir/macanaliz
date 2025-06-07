from app.models.base import BaseModel
from app import db

class Country(BaseModel):
    """Country model representing different countries."""
    __tablename__ = 'countries'
    
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(3), unique=True)  # Example: TUR, ENG, ESP
    flag = db.Column(db.String(200))  # URL to flag icon
    
    # Relationships
    leagues = db.relationship('League', back_populates='country', lazy='dynamic')
    teams = db.relationship('Team', back_populates='country', lazy='dynamic')
    
    def __repr__(self):
        return f'<Country {self.name}>'
