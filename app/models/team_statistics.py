from datetime import datetime
from typing import Optional, Dict, Any, TYPE_CHECKING

from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import relationship, backref

from .base import BaseModel
from app.extensions import db

class TeamStatistics(BaseModel):
    """Takım istatistikleri modeli
    
    Attributes:
        team_id (int): İlişkili takımın ID'si
        season_id (int): İlişkili sezonun ID'si
        total_matches (int): Toplam maç sayısı
        wins (int): Galibiyet sayısı
        draws (int): Beraberlik sayısı
        losses (int): Mağlubiyet sayısı
        goals_scored (int): Atılan gol sayısı
        goals_conceded (int): Yenilen gol sayısı
        clean_sheets (int): Kalesinde gol görmediği maç sayısı
        recent_form (str): Son 5 maç formu (Örn: 'WWDLW')
        last_updated (datetime): Son güncelleme tarihi
    """
    __tablename__ = 'team_statistics'
    
    # Tekil anahtar
    id = db.Column(db.Integer, primary_key=True)
    
    # Dış anahtarlar
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False, index=True)
    season_id = db.Column(db.Integer, db.ForeignKey('seasons.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Genel istatistikler
    total_matches = db.Column(db.Integer, default=0, nullable=False, comment='Toplam oynanan maç sayısı')
    wins = db.Column(db.Integer, default=0, nullable=False, comment='Galibiyet sayısı')
    draws = db.Column(db.Integer, default=0, nullable=False, comment='Beraberlik sayısı')
    losses = db.Column(db.Integer, default=0, nullable=False, comment='Mağlubiyet sayısı')
    
    # Atak istatistikleri
    goals_scored = db.Column(db.Integer, default=0, nullable=False, comment='Atılan gol sayısı')
    shots = db.Column(db.Integer, default=0, nullable=False, comment='Toplam şut sayısı')
    shots_on_target = db.Column(db.Integer, default=0, nullable=False, comment='İsabetli şut sayısı')
    
    # Savunma istatistikleri
    goals_conceded = db.Column(db.Integer, default=0, nullable=False, comment='Yenilen gol sayısı')
    clean_sheets = db.Column(db.Integer, default=0, nullable=False, comment='Kalesinde gol görmediği maç sayısı')
    
    # Diğer istatistikler
    yellow_cards = db.Column(db.Integer, default=0, nullable=False, comment='Sarı kart sayısı')
    red_cards = db.Column(db.Integer, default=0, nullable=False, comment='Kırmızı kart sayısı')
    
    # Form ve güncelleme bilgileri
    recent_form = db.Column(db.String(10), default='', nullable=False, comment='Son 5 maç formu (Örn: WWDLW)')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                            nullable=False, comment='Son güncelleme tarihi')
    
    # İlişkiler
    team = db.relationship('Team', back_populates='statistics', foreign_keys=[team_id])
    season = db.relationship('Season', back_populates='team_statistics', foreign_keys=[season_id])
    
    def __repr__(self):
        return f'<TeamStatistics {self.team.name} - {self.season.name}>'
    
    def to_dict(self) -> Dict[str, Any]:
        """İstatistikleri sözlük olarak döndürür"""
        return {
            'id': self.id,
            'team_id': self.team_id,
            'team_name': self.team.name if self.team else None,
            'season_id': self.season_id,
            'season_name': self.season.name if self.season else None,
            'total_matches': self.total_matches,
            'wins': self.wins,
            'draws': self.draws,
            'losses': self.losses,
            'goals_scored': self.goals_scored,
            'goals_conceded': self.goals_conceded,
            'goal_difference': self.goals_scored - self.goals_conceded,
            'clean_sheets': self.clean_sheets,
            'yellow_cards': self.yellow_cards,
            'red_cards': self.red_cards,
            'recent_form': self.recent_form,
            'points': (self.wins * 3) + self.draws,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
    
    def update_form(self, match_result: str) -> None:
        """Takımın form durumunu günceller
        
        Args:
            match_result (str): Maç sonucu (W=Kazanma, D=Beraberlik, L=Mağlubiyet)
        """
        if not self.recent_form:
            self.recent_form = match_result
        else:
            # Son 5 maçı tutacak şekilde güncelle
            self.recent_form = (self.recent_form + match_result)[-5:]
    
    @classmethod
    def get_team_season_stats(cls, team_id: int, season_id: int) -> 'TeamStatistics':
        """Belirli bir takımın sezon istatistiklerini getirir"""
        return cls.query.filter_by(team_id=team_id, season_id=season_id).first()
    
    # Zorunlu alanlar zaten yukarıda tanımlanmış
    
    # İlişkiler
    # Team ve Season ilişkileri backref ile tanımlanıyor
    team = relationship('Team', backref='team_stats')
    season = relationship('Season', backref='season_stats')
    
    def __repr__(self):
        return f'<TeamStatistics {self.team.name} - Sezon {self.season.name}>'
    
    def calculate_win_rate(self) -> float:
        """Takımın galibiyet yüzdesini hesaplar"""
        if self.total_matches == 0:
            return 0.0
        return round((self.wins / self.total_matches) * 100, 2)
    
    def update_form(self, result: str):
        """Takımın form durumunu günceller
        
        Args:
            result (str): Maç sonucu ('W'=Galibiyet, 'D'=Beraberlik, 'L'=Mağlubiyet)
        """
        if result.upper() not in ['W', 'D', 'L']:
            raise ValueError("Geçersiz sonuç. 'W', 'D' veya 'L' olmalıdır.")
            
        # Son 5 maçı koruyarak yeni sonucu ekle
        self.recent_form = (self.recent_form + result.upper())[-5:]
        
    def get_form_streak(self) -> int:
        """Takımın son maçlardaki form serisini döndürür"""
        if not self.recent_form:
            return 0
            
        last_result = self.recent_form[-1]
        streak = 0
        
        for result in reversed(self.recent_form):
            if result == last_result:
                streak += 1
            else:
                break
                
        return streak if last_result == 'W' else -streak
