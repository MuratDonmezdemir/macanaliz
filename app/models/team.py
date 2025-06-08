from datetime import datetime
from .base import BaseModel
from app.extensions import db

class Team(BaseModel):
    """Futbol takımı modeli"""
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    short_name = db.Column(db.String(20))
    country = db.Column(db.String(50))
    city = db.Column(db.String(50))
    founded = db.Column(db.Integer)
    logo = db.Column(db.String(200))
    stadium_id = db.Column(db.Integer, db.ForeignKey('stadiums.id'))
    website = db.Column(db.String(200))
    colors = db.Column(db.String(100))  # JSON formatında renkler
    coach = db.Column(db.String(100))
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'))
    is_national = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    home_matches = db.relationship('Match', foreign_keys='Match.home_team_id', backref=db.backref('home_team', lazy='joined'), lazy='dynamic')
    away_matches = db.relationship('Match', foreign_keys='Match.away_team_id', backref=db.backref('away_team', lazy='joined'), lazy='dynamic')
    players = db.relationship('Player', backref='team', lazy='dynamic')
    league = db.relationship('League', back_populates='teams')
    stadium = db.relationship('Stadium', back_populates='teams')
    
    def __repr__(self):
        return f'<Team {self.name}>'
    
    def to_dict(self):
        """Takım bilgilerini sözlük olarak döndürür"""
        return {
            'id': self.id,
            'name': self.name,
            'short_name': self.short_name,
            'country': self.country,
            'logo': self.logo,
            'stadium': self.stadium.name if self.stadium else None,
            'league': self.league.name if self.league else None,
            'founded': self.founded,
            'coach': self.coach
        }
    
    def get_recent_matches(self, limit=5):
        """Takımın son maçlarını getirir"""
        return Match.query.filter(
            (Match.home_team_id == self.id) | (Match.away_team_id == self.id)
        ).order_by(Match.match_date.desc()).limit(limit).all()
    
    def get_next_match(self):
        """Takımın bir sonraki maçını getirir"""
        return Match.query.filter(
            ((Match.home_team_id == self.id) | (Match.away_team_id == self.id)) &
            (Match.status == 'SCHEDULED')
        ).order_by(Match.match_date.asc()).first()
    
    def get_standings(self, season_id):
        """Takımın lig sıralamasındaki durumunu getirir"""
        from .standing import Standing
        return Standing.query.filter_by(
            team_id=self.id,
            season_id=season_id
        ).first()
    
    def get_statistics(self):
        """Takım istatistiklerini getirir"""
        from .match_statistics import MatchStatistics
        return MatchStatistics.query.filter_by(team_id=self.id).first()
