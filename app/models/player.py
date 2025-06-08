from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
from .base import BaseModel
from app.extensions import db

class Player(BaseModel):
    """Oyuncu modeli"""
    __tablename__ = 'players'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    position = db.Column(db.String(5))  # GK, DEF, MID, FWD
    nationality = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date)
    height = db.Column(db.Integer)  # cm cinsinden
    weight = db.Column(db.Integer)  # kg cinsinden
    jersey_number = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    team = db.relationship('Team', back_populates='players')
    statistics = db.relationship('PlayerStatistics', back_populates='player')
    
    def __repr__(self):
        return f'<Player {self.name}>'
    
    def to_dict(self):
        """Oyuncu bilgilerini sözlük olarak döndürür"""
        return {
            'id': self.id,
            'name': self.name,
            'team_id': self.team_id,
            'position': self.position,
            'nationality': self.nationality,
            'jersey_number': self.jersey_number
        }

class PlayerStatistics(BaseModel):
    """Oyuncu istatistikleri modeli"""
    __tablename__ = 'player_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))
    season_id = db.Column(db.Integer, db.ForeignKey('seasons.id'))
    
    # İlişkiler
    player = db.relationship('Player', back_populates='statistics')
    team = db.relationship('Team')
    match = db.relationship('Match')
    season = db.relationship('Season')
    
    # Temel istatistikler
    position = db.Column(db.String(5))  # GK, DEF, MID, FWD
    minutes_played = db.Column(db.Integer, default=0)
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    yellow_cards = db.Column(db.Integer, default=0)
    red_cards = db.Column(db.Integer, default=0)
    
    # Hücum istatistikleri
    shots = db.Column(db.Integer, default=0)
    shots_on_target = db.Column(db.Integer, default=0)
    key_passes = db.Column(db.Integer, default=0)
    dribbles = db.Column(db.Integer, default=0)
    dribbles_successful = db.Column(db.Integer, default=0)
    
    # Pas istatistikleri
    passes = db.Column(db.Integer, default=0)
    pass_accuracy = db.Column(db.Float)
    
    # Defans istatistikleri
    tackles = db.Column(db.Integer, default=0)
    interceptions = db.Column(db.Integer, default=0)
    clearances = db.Column(db.Integer, default=0)
    
    # Diğer
    rating = db.Column(db.Float)
    is_motm = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    pass_accuracy = db.Column(db.Float, default=0.0)  # Yüzde olarak
    long_balls = db.Column(db.Integer, default=0)
    crosses = db.Column(db.Integer, default=0)
    
    # Defans istatistikleri
    tackles = db.Column(db.Integer, default=0)
    interceptions = db.Column(db.Integer, default=0)
    clearances = db.Column(db.Integer, default=0)
    blocks = db.Column(db.Integer, default=0)
    
    # Kaleci istatistikleri
    saves = db.Column(db.Integer, default=0)
    goals_conceded = db.Column(db.Integer, default=0)
    clean_sheets = db.Column(db.Boolean, default=False)
    penalty_saves = db.Column(db.Integer, default=0)
    
    # Diğer
    fouls_committed = db.Column(db.Integer, default=0)
    fouls_suffered = db.Column(db.Integer, default=0)
    offsides = db.Column(db.Integer, default=0)
    
    # Puanlama ve değerlendirme
    rating = db.Column(db.Float, default=0.0)  # 1-10 arası performans puanı
    is_motm = db.Column(db.Boolean, default=False)  # Maçın adamı mı?
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    team = db.relationship('Team', backref=db.backref('player_statistics', lazy='dynamic'))
    match = db.relationship('Match', backref=db.backref('player_stats', lazy='dynamic'))
    season = db.relationship('Season')
    
    def __repr__(self):
        return f'<PlayerStatistics {self.player_name} - {self.match_id}>'
    
    def to_dict(self):
        """İstatistikleri sözlük olarak döndürür"""
        return {
            'player_name': self.player_name,
            'team_id': self.team_id,
            'match_id': self.match_id,
            'position': self.position,
            'goals': self.goals,
            'assists': self.assists,
            'rating': self.rating,
            'is_motm': self.is_motm
        }
