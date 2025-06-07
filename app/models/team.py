from app.models.base import BaseModel
from app import db
from sqlalchemy.orm import relationship

class Team(BaseModel):
    """Team model representing football teams."""
    __tablename__ = 'teams'
    
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    founded = db.Column(db.Integer)
    stadium = db.Column(db.String(100))
    logo = db.Column(db.String(200))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    attack_rating = db.Column(db.Integer, default=50)
    defense_rating = db.Column(db.Integer, default=50)
    home_advantage = db.Column(db.Float, default=1.1)
    current_form = db.Column(db.Integer, default=50)
    
    # Relationships
    country = db.relationship('Country', back_populates='teams')
    league = db.relationship('League', back_populates='teams')
    home_matches = relationship('Match', foreign_keys='Match.home_team_id', back_populates='home_team')
    away_matches = relationship('Match', foreign_keys='Match.away_team_id', back_populates='away_team')
    statistics = db.relationship('TeamStatistics', back_populates='team', lazy='dynamic')
    
    def __repr__(self):
        return f'<Team {self.name}>'
