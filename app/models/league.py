from datetime import datetime
from .base import BaseModel
from app.extensions import db

class League(BaseModel):
    """Lig modeli"""
    __tablename__ = 'leagues'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(50))
    logo = db.Column(db.String(200))
    season = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<League {self.name}>'


class Season(BaseModel):
    """Sezon modeli"""
    __tablename__ = 'seasons'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # Örn: 2023-2024
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_current = db.Column(db.Boolean, default=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    league = db.relationship('League', backref=db.backref('seasons', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Season {self.name}>'


class Standing(BaseModel):
    """Puan durumu modeli"""
    __tablename__ = 'standings'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('seasons.id'), nullable=False)
    played = db.Column(db.Integer, default=0)
    won = db.Column(db.Integer, default=0)
    drawn = db.Column(db.Integer, default=0)
    lost = db.Column(db.Integer, default=0)
    goals_for = db.Column(db.Integer, default=0)
    goals_against = db.Column(db.Integer, default=0)
    goal_difference = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)
    position = db.Column(db.Integer)
    form = db.Column(db.String(10))  # Son 5 maç formu (Örn: "WWDLD")
    
    team = db.relationship('Team', backref=db.backref('standings', lazy='dynamic'))
    season = db.relationship('Season', backref=db.backref('standings', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Standing {self.team.name} - {self.season.name}>'
