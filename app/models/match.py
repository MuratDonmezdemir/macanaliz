from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

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
    
    # Relationships
    stadium = db.relationship('Stadium', backref='match_list')
    season = db.relationship('Season', backref='match_list')
    home_team = db.relationship('Team', foreign_keys=[home_team_id])
    away_team = db.relationship('Team', foreign_keys=[away_team_id])
    predictions = db.relationship(
        'Prediction', 
        back_populates='match',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    def __repr__(self):
        return f'<Match {self.home_team_id} vs {self.away_team_id} ({self.match_date})>'
    
    def to_dict(self):
        """Maç bilgilerini sözlük olarak döndürür"""
        return {
            'id': self.id,
            'home_team': self.home_team.to_dict() if self.home_team else None,
            'away_team': self.away_team.to_dict() if self.away_team else None,
            'match_date': self.match_date.isoformat() if self.match_date else None,
            'status': self.status,
            'home_score': self.home_score,
            'away_score': self.away_score,
            'stadium': self.stadium.to_dict() if self.stadium else None,
            'season': self.season.to_dict() if self.season else None
        }
        
    def get_prediction_for_user(self, user_id):
        """Kullanıcının bu maç için yaptığı tahmini döndürür"""
        return self.predictions.filter_by(user_id=user_id).first()


class MatchStatistics(BaseModel):
    """Maç istatistikleri modeli"""
    __tablename__ = 'match_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    statistics = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    match = db.relationship(
        'Match',
        back_populates='match_statistics',
        foreign_keys=[match_id]
    )
    team = db.relationship('Team', back_populates='match_statistics')
    
    def __repr__(self):
        return f'<MatchStatistics {self.match_id} - Team {self.team_id}>'
    
    def to_dict(self):
        """İstatistikleri sözlük olarak döndürür"""
        return {
            'id': self.id,
            'match_id': self.match_id,
            'team_id': self.team_id,
            'statistics': self.statistics,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }