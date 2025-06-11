from datetime import datetime
from ..extensions import db
from .base import BaseModel
from .enums import MatchStatus

class Match(BaseModel):
    """Futbol maçlarını temsil eden model."""
    __tablename__ = 'matches'
    
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'))
    match_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.Enum(MatchStatus), default=MatchStatus.SCHEDULED)
    home_goals = db.Column(db.Integer, default=0)
    away_goals = db.Column(db.Integer, default=0)
    half_time_home_goals = db.Column(db.Integer, default=0)
    half_time_away_goals = db.Column(db.Integer, default=0)
    
    # İlişkiler
    predictions = db.relationship('Prediction', backref='match', lazy=True)
    
    def __repr__(self):
        return f'<Match {self.home_team.name} vs {self.away_team.name} - {self.match_date}>'
