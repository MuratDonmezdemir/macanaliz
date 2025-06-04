from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property

db = SQLAlchemy()

# Utility functions
def calculate_win_percentage(wins, total):
    return round((wins / total) * 100, 2) if total > 0 else 0.0

# Move all model definitions below this line
# This prevents circular imports

class Team(db.Model):
    """Takım modeli"""
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    short_name = db.Column(db.String(10))
    country = db.Column(db.String(50))
    founded = db.Column(db.Integer)
    stadium = db.Column(db.String(100))
    logo = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    home_matches = db.relationship('Match', foreign_keys='Match.home_team_id', back_populates='home_team')
    away_matches = db.relationship('Match', foreign_keys='Match.away_team_id', back_populates='away_team')
    
    def __repr__(self):
        return f'<Team {self.name}>'

class Match(db.Model):
    """Maç modeli"""
    __tablename__ = 'matches'
    
    id = db.Column(db.Integer, primary_key=True)
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False, index=True)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False, index=True)
    
    # Maç detayları
    match_date = db.Column(db.DateTime, nullable=False, index=True)
    competition = db.Column(db.String(100), index=True)
    season = db.Column(db.String(20), index=True)  # Örn: '2023/2024'
    matchday = db.Column(db.Integer)  # Hafta numarası
    
    # Maç sonuçları
    home_goals = db.Column(db.Integer)
    away_goals = db.Column(db.Integer)
    home_ht_goals = db.Column(db.Integer)  # İlk yarı golleri
    away_ht_goals = db.Column(db.Integer)  # İlk yarı golleri
    
    # Detaylı istatistikler
    home_possession = db.Column(db.Float)  # Top hakimiyeti %
    away_possession = db.Column(db.Float)
    home_shots = db.Column(db.Integer)     # Toplam şut
    away_shots = db.Column(db.Integer)
    home_shots_on_target = db.Column(db.Integer)  # İsabetli şut
    away_shots_on_target = db.Column(db.Integer)
    home_corners = db.Column(db.Integer)   # Korner
    away_corners = db.Column(db.Integer)
    home_fouls = db.Column(db.Integer)     # Fauller
    away_fouls = db.Column(db.Integer)
    home_yellows = db.Column(db.Integer)   # Sarı kartlar
    away_yellows = db.Column(db.Integer)
    home_reds = db.Column(db.Integer)      # Kırmızı kartlar
    away_reds = db.Column(db.Integer)
    home_offsides = db.Column(db.Integer)  # Ofsayt
    away_offsides = db.Column(db.Integer)
    
    # Durum
    status = db.Column(db.String(20), default='Scheduled')  # Scheduled, Live, HT, Finished
    
    # Zaman damgaları
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    home_team = db.relationship('Team', foreign_keys=[home_team_id], back_populates='home_matches')
    away_team = db.relationship('Team', foreign_keys=[away_team_id], back_populates='away_matches')
    predictions = db.relationship('Prediction', back_populates='match', lazy='dynamic')
    
    # Hesaplanan özellikler
    @hybrid_property
    def total_goals(self):
        if self.home_goals is not None and self.away_goals is not None:
            return self.home_goals + self.away_goals
        return None
    
    @hybrid_property
    def result(self):
        if self.home_goals is None or self.away_goals is None:
            return None
        if self.home_goals > self.away_goals:
            return 'H'  # Home win
        elif self.home_goals < self.away_goals:
            return 'A'  # Away win
        return 'D'  # Draw
    
    @hybrid_property
    def half_time_result(self):
        if self.home_ht_goals is None or self.away_ht_goals is None:
            return None
        if self.home_ht_goals > self.away_ht_goals:
            return 'H'  # Home win at HT
        elif self.home_ht_goals < self.away_ht_goals:
            return 'A'  # Away win at HT
        return 'D'  # Draw at HT
    
    def to_dict(self):
        """Maç verilerini sözlük olarak döndürür"""
        return {
            'id': self.id,
            'home_team': self.home_team.name,
            'away_team': self.away_team.name,
            'match_date': self.match_date.isoformat(),
            'competition': self.competition,
            'season': self.season,
            'home_goals': self.home_goals,
            'away_goals': self.away_goals,
            'home_ht_goals': self.home_ht_goals,
            'away_ht_goals': self.away_ht_goals,
            'status': self.status,
            'stats': {
                'possession': {'home': self.home_possession, 'away': self.away_possession},
                'shots': {'home': self.home_shots, 'away': self.away_shots},
                'shots_on_target': {'home': self.home_shots_on_target, 'away': self.away_shots_on_target},
                'corners': {'home': self.home_corners, 'away': self.away_corners},
                'fouls': {'home': self.home_fouls, 'away': self.away_fouls},
                'cards': {
                    'yellows': {'home': self.home_yellows, 'away': self.away_yellows},
                    'reds': {'home': self.home_reds, 'away': self.away_reds}
                },
                'offsides': {'home': self.home_offsides, 'away': self.away_offsides}
            }
        }
    
    def __repr__(self):
        return f'<Match {self.home_team.name} {self.home_goals or "?"} - {self.away_goals or "?"} {self.away_team.name} ({self.match_date.strftime("%d.%m.%Y")})>'

class Prediction(db.Model):
    """Tahmin modeli"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False, index=True)
    
    # Temel tahminler
    home_goals = db.Column(db.Float, nullable=False)
    away_goals = db.Column(db.Float, nullable=False)
    home_win = db.Column(db.Float, nullable=False)  # Ev sahibi galibiyet olasılığı
    draw = db.Column(db.Float, nullable=False)       # Beraberlik olasılığı
    away_win = db.Column(db.Float, nullable=False)   # Deplasman galibiyet olasılığı
    
    # İlk yarı tahminleri
    home_ht_goals = db.Column(db.Float)  # İlk yarı ev golleri
    away_ht_goals = db.Column(db.Float)  # İlk yarı deplasman golleri
    ht_home_win = db.Column(db.Float)    # İlk yarı ev galibiyet
    ht_draw = db.Column(db.Float)        # İlk yarı beraberlik
    ht_away_win = db.Column(db.Float)    # İlk yarı deplasman galibiyet
    
    # Skor tahminleri ve olasılıkları
    most_likely_score = db.Column(db.String(10))  # En olası skor (örn: '2-1')
    score_probability = db.Column(db.Float)       # En olası skorun gerçekleşme olasılığı
    
    # İstatistiksel özetler
    over_05 = db.Column(db.Float)  # 0.5 üstü gol olasılığı
    over_15 = db.Column(db.Float)  # 1.5 üstü gol olasılığı
    over_25 = db.Column(db.Float)  # 2.5 üstü gol olasılığı
    btts_yes = db.Column(db.Float)  # İki takımın da gol atma olasılığı
    
    # Model bilgileri
    algorithm = db.Column(db.String(50), nullable=False)  # Kullanılan algoritma
    model_version = db.Column(db.String(20))             # Model versiyonu
    confidence = db.Column(db.Float)                      # Genel güven skoru (0-1)
    
    # Zaman damgaları
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    match = db.relationship('Match', back_populates='predictions')
    
    # Hesaplanan özellikler
    @hybrid_property
    def total_goals(self):
        return self.home_goals + self.away_goals
    
    @hybrid_property
    def predicted_result(self):
        if self.home_win >= self.away_win and self.home_win >= self.draw:
            return 'H'  # Home win
        elif self.away_win >= self.home_win and self.away_win >= self.draw:
            return 'A'  # Away win
        return 'D'  # Draw
    
    def to_dict(self):
        """Tahmin verilerini sözlük olarak döndürür"""
        return {
            'id': self.id,
            'match_id': self.match_id,
            'prediction': {
                'full_time': {
                    'home_goals': round(self.home_goals, 2),
                    'away_goals': round(self.away_goals, 2),
                    'home_win': round(self.home_win * 100, 1),
                    'draw': round(self.draw * 100, 1),
                    'away_win': round(self.away_win * 100, 1),
                    'total_goals': round(self.total_goals, 2)
                },
                'half_time': {
                    'home_goals': round(self.home_ht_goals, 2) if self.home_ht_goals is not None else None,
                    'away_goals': round(self.away_ht_goals, 2) if self.away_ht_goals is not None else None,
                    'home_win': round(self.ht_home_win * 100, 1) if self.ht_home_win is not None else None,
                    'draw': round(self.ht_draw * 100, 1) if self.ht_draw is not None else None,
                    'away_win': round(self.ht_away_win * 100, 1) if self.ht_away_win is not None else None
                },
                'score_prediction': {
                    'most_likely': self.most_likely_score,
                    'probability': round(self.score_probability * 100, 1) if self.score_probability else None
                },
                'statistics': {
                    'over_05': round(self.over_05 * 100, 1) if self.over_05 is not None else None,
                    'over_15': round(self.over_15 * 100, 1) if self.over_15 is not None else None,
                    'over_25': round(self.over_25 * 100, 1) if self.over_25 is not None else None,
                    'btts_yes': round(self.btts_yes * 100, 1) if self.btts_yes is not None else None
                }
            },
            'model_info': {
                'algorithm': self.algorithm,
                'version': self.model_version,
                'confidence': round(self.confidence * 100, 1) if self.confidence else None
            },
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Prediction {self.algorithm} v{self.model_version} - {self.home_goals:.1f}-{self.away_goals:.1f} (H:{self.home_win*100:.1f}% D:{self.draw*100:.1f}% A:{self.away_win*100:.1f}%)>'

class TeamStatistics(db.Model):
    __tablename__ = 'team_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    season = db.Column(db.String(20), nullable=False)
    
    # Overall Statistics
    matches_played = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    goals_for = db.Column(db.Integer, default=0)
    goals_against = db.Column(db.Integer, default=0)
    
    # Home Statistics
    home_matches = db.Column(db.Integer, default=0)
    home_wins = db.Column(db.Integer, default=0)
    home_draws = db.Column(db.Integer, default=0)
    home_losses = db.Column(db.Integer, default=0)
    home_goals_for = db.Column(db.Integer, default=0)
    home_goals_against = db.Column(db.Integer, default=0)
    
    # Away Statistics
    away_matches = db.Column(db.Integer, default=0)
    away_wins = db.Column(db.Integer, default=0)
    away_draws = db.Column(db.Integer, default=0)
    away_losses = db.Column(db.Integer, default=0)
    away_goals_for = db.Column(db.Integer, default=0)
    away_goals_against = db.Column(db.Integer, default=0)
    
    # Advanced Metrics
    average_goals_per_match = db.Column(db.Float, default=0.0)
    average_goals_conceded = db.Column(db.Float, default=0.0)
    clean_sheets = db.Column(db.Integer, default=0)
    
    # Relationships
    team = relationship('Team')
    
    def __repr__(self):
        return f'<TeamStatistics {self.team.name} - {self.season}>'
