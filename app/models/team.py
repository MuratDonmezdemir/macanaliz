from ..extensions import db
from .base import BaseModel
from .enums import TeamStatus

class Team(BaseModel):
    """Futbol takımlarını temsil eden model."""
    __tablename__ = 'teams'
    
    name = db.Column(db.String(100), nullable=False, unique=True)
    short_name = db.Column(db.String(10))
    country = db.Column(db.String(50))
    founded = db.Column(db.Integer)
    logo = db.Column(db.String(255))
    status = db.Column(db.Enum(TeamStatus), default=TeamStatus.ACTIVE)
    
    # İlişkiler
    home_matches = db.relationship('Match', foreign_keys='Match.home_team_id', backref='home_team', lazy=True)
    away_matches = db.relationship('Match', foreign_keys='Match.away_team_id', backref='away_team', lazy=True)
    
    def __repr__(self):
        return f'<Team {self.name}>'
