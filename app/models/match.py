from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
from .base import BaseModel
from app.extensions import db

class Match(BaseModel):
    """Maç modeli"""
    __tablename__ = 'matches'
    
    id = db.Column(db.Integer, primary_key=True)
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    match_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='SCHEDULED')  # SCHEDULED, LIVE, FINISHED
    home_score = db.Column(db.Integer, default=0)
    away_score = db.Column(db.Integer, default=0)
    stadium_id = db.Column(db.Integer, db.ForeignKey('stadiums.id'))
    season_id = db.Column(db.Integer, db.ForeignKey('seasons.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships are defined in Team model
    stadium = db.relationship('Stadium', back_populates='matches')
    season = db.relationship('Season', back_populates='matches')
    
    def __repr__(self):
        return f'<Match {self.home_team_id} vs {self.away_team_id}>'
    
    def to_dict(self):
        """Maç bilgilerini sözlük olarak döndürür"""
        return {
            'id': self.id,
            'home_team': self.home_team.to_dict(),
            'away_team': self.away_team.to_dict(),
            'match_date': self.match_date.isoformat(),
            'status': self.status,
            'home_score': self.home_score,
            'away_score': self.away_score,
            'stadium': self.stadium.to_dict() if self.stadium else None,
            'season': self.season.to_dict() if self.season else None
        }


class MatchStatistics(BaseModel):
    """Maç istatistikleri modeli"""
    __tablename__ = 'match_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    statistics = db.Column(JSON)  # JSON formatında istatistikler
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    match = db.relationship('Match', backref=db.backref('match_statistics', lazy='dynamic'))
    team = db.relationship('Team')
    
    def __repr__(self):
        return f'<MatchStatistics {self.match_id} - {self.team_id}>'
    
    def to_dict(self):
        """İstatistikleri sözlük olarak döndürür"""
        return {
            'id': self.id,
            'match_id': self.match_id,
            'team_id': self.team_id,
            'statistics': self.statistics,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Prediction(BaseModel):
    """Maç tahmin modeli"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    home_goals = db.Column(db.Integer, nullable=False)
    away_goals = db.Column(db.Integer, nullable=False)
    confidence = db.Column(db.Float)  # Tahmin güven skoru
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    match = db.relationship('Match', backref=db.backref('predictions', lazy='dynamic'))
    user = db.relationship('User')
    
    def __repr__(self):
        return f'<Prediction {self.match_id} - {self.home_goals}:{self.away_goals}>'
    
    def to_dict(self):
        """Tahmin bilgilerini sözlük olarak döndürür"""
        return {
            'id': self.id,
            'match_id': self.match_id,
            'user_id': self.user_id,
            'home_goals': self.home_goals,
            'away_goals': self.away_goals,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
