from datetime import datetime
from app.models.base import BaseModel
from app import db

class Match(BaseModel):
    """Match model representing football matches."""
    __tablename__ = 'matches'
    
    # Basic match information
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False, index=True)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False, index=True)
    match_date = db.Column(db.DateTime, nullable=False, index=True)
    season = db.Column(db.String(20), index=True)  # e.g., "2024-2025"
    matchday = db.Column(db.Integer)  # Match week/number
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    status = db.Column(db.String(20), default='Scheduled')  # Scheduled, Live, FT, etc.
    
    # Match statistics
    home_goals = db.Column(db.Integer)
    away_goals = db.Column(db.Integer)
    home_ht_goals = db.Column(db.Integer)  # Half-time goals
    away_ht_goals = db.Column(db.Integer)
    home_possession = db.Column(db.Float)  # Percentage
    away_possession = db.Column(db.Float)
    home_shots = db.Column(db.Integer)
    away_shots = db.Column(db.Integer)
    home_shots_on_target = db.Column(db.Integer)
    away_shots_on_target = db.Column(db.Integer)
    home_corners = db.Column(db.Integer)
    away_corners = db.Column(db.Integer)
    home_fouls = db.Column(db.Integer)
    away_fouls = db.Column(db.Integer)
    home_yellows = db.Column(db.Integer)
    away_yellows = db.Column(db.Integer)
    home_reds = db.Column(db.Integer)
    away_reds = db.Column(db.Integer)
    home_offsides = db.Column(db.Integer)
    away_offsides = db.Column(db.Integer)
    
    # Relationships
    home_team = db.relationship('Team', foreign_keys=[home_team_id], back_populates='home_matches')
    away_team = db.relationship('Team', foreign_keys=[away_team_id], back_populates='away_matches')
    league = db.relationship('League', back_populates='matches')
    predictions = db.relationship('Prediction', back_populates='match', uselist=False)
    
    def __repr__(self):
        return f'<Match {self.home_team.name} vs {self.away_team.name} - {self.match_date}>'
