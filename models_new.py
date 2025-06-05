from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func

db = SQLAlchemy()

# Utility functions
def calculate_win_percentage(wins, total):
    return round((wins / total) * 100, 2) if total > 0 else 0.0

# Move all model definitions below this line
# This prevents circular imports

class Country(db.Model):
    """Ülke modeli"""
    __tablename__ = 'countries'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(3), unique=True)  # Örn: TUR, ENG, ESP
    flag = db.Column(db.String(200))  # Bayrak ikonu URL'si
    
    # İlişkiler
    leagues = db.relationship('League', back_populates='country')
    teams = db.relationship('Team', back_populates='country')
    
    def __repr__(self):
        return f'<Country {self.name}>'


class League(db.Model):
    """Lig modeli"""
    __tablename__ = 'leagues'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    level = db.Column(db.Integer, default=1)  # 1: Süper Lig, 2: 1. Lig gibi
    logo = db.Column(db.String(200))
    current_season = db.Column(db.String(20))  # Örn: 2024-2025
    
    # İlişkiler
    country = db.relationship('Country', back_populates='leagues')
    teams = db.relationship('Team', back_populates='league')
    matches = db.relationship('Match', back_populates='league')
    
    def __repr__(self):
        return f'<League {self.name} ({self.country.code})>'


class Team(db.Model):
    """Takım modeli"""
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    founded = db.Column(db.Integer)
    stadium = db.Column(db.String(100))
    logo = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkisel alanlar
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    
    # Takım özellikleri (veri üretimi için)
    attack_rating = db.Column(db.Integer, default=50)  # 1-100 arası hücum gücü
    defense_rating = db.Column(db.Integer, default=50)  # 1-100 arası savunma gücü
    home_advantage = db.Column(db.Float, default=1.1)  # Ev sahibi avantajı çarpanı
    current_form = db.Column(db.Integer, default=50)  # 1-100 arası form durumu
    
    # İlişkiler
    country = db.relationship('Country', back_populates='teams')
    league = db.relationship('League', back_populates='teams')
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
    season = db.Column(db.String(20), index=True)  # Örn: '2023/2024'
    matchday = db.Column(db.Integer)  # Hafta numarası
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    status = db.Column(db.String(20), default='Scheduled')  # Scheduled, Live, HT, Finished, Postponed, Cancelled
    
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
    
    # Zaman damgaları
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    home_team = db.relationship('Team', foreign_keys=[home_team_id], back_populates='home_matches')
    away_team = db.relationship('Team', foreign_keys=[away_team_id], back_populates='away_matches')
    league = db.relationship('League', back_populates='matches')
    
    def __repr__(self):
        return f'<Match {self.home_team.name} vs {self.away_team.name} ({self.match_date})>'


class Prediction(db.Model):
    """Tahmin modeli"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False, index=True)
    
    # Tahmin sonuçları
    home_goals = db.Column(db.Float, nullable=False)
    away_goals = db.Column(db.Float, nullable=False)
    
    # Maç sonucu ihtimalleri
    home_win = db.Column(db.Float, nullable=False)  # Ev sahibi galibiyet ihtimali
    draw = db.Column(db.Float, nullable=False)      # Beraberlik ihtimali
    away_win = db.Column(db.Float, nullable=False)  # Deplasman galibiyet ihtimali
    
    # İlk yarı tahminleri
    home_ht_goals = db.Column(db.Float)
    away_ht_goals = db.Column(db.Float)
    ht_home_win = db.Column(db.Float)  # İlk yarı ev galibiyet ihtimali
    ht_draw = db.Column(db.Float)      # İlk yarı beraberlik ihtimali
    ht_away_win = db.Column(db.Float)  # İlk yarı deplasman galibiyet ihtimali
    
    # Özel bahisler
    most_likely_score = db.Column(db.String(10))  # En olası skor (örn: '2-1')
    score_probability = db.Column(db.Float)      # Bu skorun olasılığı
    over_05 = db.Column(db.Float)  # 0.5 üstü gol ihtimali
    over_15 = db.Column(db.Float)  # 1.5 üstü gol ihtimali
    over_25 = db.Column(db.Float)  # 2.5 üstü gol ihtimali
    btts_yes = db.Column(db.Float)  # İki takım da gol atar ihtimali
    
    # Model bilgileri
    algorithm = db.Column(db.String(50), nullable=False)  # Kullanılan algoritma
    model_version = db.Column(db.String(20))  # Model versiyonu
    confidence = db.Column(db.Float)  # Tahmin güveni
    
    # Zaman damgaları
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    match = db.relationship('Match', back_populates='predictions')
    
    @property
    def total_goals(self):
        """Toplam gol sayısını döndürür"""
        return self.home_goals + self.away_goals
    
    @property
    def predicted_result(self):
        """Tahmin edilen maç sonucunu döndürür"""
        if self.home_win > self.away_win and self.home_win > self.draw:
            return '1'
        elif self.away_win > self.home_win and self.away_win > self.draw:
            return '2'
        else:
            return 'X'
    
    def to_dict(self):
        """Tahmin verilerini sözlük olarak döndürür"""
        return {
            'id': self.id,
            'match_id': self.match_id,
            'home_goals': self.home_goals,
            'away_goals': self.away_goals,
            'home_win': self.home_win,
            'draw': self.draw,
            'away_win': self.away_win,
            'predicted_result': self.predicted_result,
            'most_likely_score': self.most_likely_score,
            'score_probability': self.score_probability,
            'over_05': self.over_05,
            'over_15': self.over_15,
            'over_25': self.over_25,
            'btts_yes': self.btts_yes,
            'algorithm': self.algorithm,
            'model_version': self.model_version,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Prediction {self.match} - {self.predicted_result} ({self.confidence:.0%})>'


class TeamStatistics(db.Model):
    """Takım istatistikleri modeli"""
    __tablename__ = 'team_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    season = db.Column(db.String(20), nullable=False)  # Örn: '2023/2024'
    
    # Genel istatistikler
    matches_played = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    goals_for = db.Column(db.Integer, default=0)
    goals_against = db.Column(db.Integer, default=0)
    
    # İç saha istatistikleri
    home_matches = db.Column(db.Integer, default=0)
    home_wins = db.Column(db.Integer, default=0)
    home_draws = db.Column(db.Integer, default=0)
    home_losses = db.Column(db.Integer, default=0)
    home_goals_for = db.Column(db.Integer, default=0)
    home_goals_against = db.Column(db.Integer, default=0)
    
    # Deplasman istatistikleri
    away_matches = db.Column(db.Integer, default=0)
    away_wins = db.Column(db.Integer, default=0)
    away_draws = db.Column(db.Integer, default=0)
    away_losses = db.Column(db.Integer, default=0)
    away_goals_for = db.Column(db.Integer, default=0)
    away_goals_against = db.Column(db.Integer, default=0)
    
    # İstatistiksel değerler
    average_goals_per_match = db.Column(db.Float, default=0.0)
    average_goals_conceded = db.Column(db.Float, default=0.0)
    clean_sheets = db.Column(db.Integer, default=0)  # Sıfır çekilen maç sayısı
    
    # İlişkiler
    team = relationship('Team')
    
    @property
    def goal_difference(self):
        """Averaj değerini döndürür"""
        return self.goals_for - self.goals_against
    
    @property
    def points(self):
        """Puan toplamını hesaplar"""
        return (self.wins * 3) + (self.draws * 1)
    
    @property
    def win_percentage(self):
        """Galibiyet yüzdesini hesaplar"""
        return calculate_win_percentage(self.wins, self.matches_played)
    
    def update_statistics(self, match, is_home):
        """İstatistikleri günceller"""
        if is_home:
            self.home_matches += 1
            self.home_goals_for += match.home_goals
            self.home_goals_against += match.away_goals
            
            if match.home_goals > match.away_goals:
                self.home_wins += 1
            elif match.home_goals < match.away_goals:
                self.home_losses += 1
            else:
                self.home_draws += 1
        else:
            self.away_matches += 1
            self.away_goals_for += match.away_goals
            self.away_goals_against += match.home_goals
            
            if match.away_goals > match.home_goals:
                self.away_wins += 1
            elif match.away_goals < match.home_goals:
                self.away_losses += 1
            else:
                self.away_draws += 1
        
        # Genel istatistikleri güncelle
        self.matches_played = self.home_matches + self.away_matches
        self.wins = self.home_wins + self.away_wins
        self.draws = self.home_draws + self.away_draws
        self.losses = self.home_losses + self.away_losses
        self.goals_for = self.home_goals_for + self.away_goals_for
        self.goals_against = self.home_goals_against + self.away_goals_against
        
        # Ortalama değerleri güncelle
        if self.matches_played > 0:
            self.average_goals_per_match = round(self.goals_for / self.matches_played, 2)
            self.average_goals_conceded = round(self.goals_against / self.matches_played, 2)
        
        # Temiz sayı güncelleme
        if (is_home and match.away_goals == 0) or (not is_home and match.home_goals == 0):
            self.clean_sheets += 1
    
    def __repr__(self):
        return f'<TeamStatistics {self.team.name} - {self.season} - PTS: {self.points}'>'
