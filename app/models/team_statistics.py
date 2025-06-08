from datetime import datetime
from .base import BaseModel
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, backref
from datetime import datetime

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
    
    # Zorunlu alanlar
    team_id = Column(Integer, ForeignKey('teams.id', ondelete='CASCADE'), nullable=False, index=True)
    season_id = Column(Integer, ForeignKey('seasons.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Genel istatistikler
    total_matches = Column(Integer, default=0, nullable=False, comment='Toplam oynanan maç sayısı')
    wins = Column(Integer, default=0, nullable=False, comment='Galibiyet sayısı')
    draws = Column(Integer, default=0, nullable=False, comment='Beraberlik sayısı')
    losses = Column(Integer, default=0, nullable=False, comment='Mağlubiyet sayısı')
    
    # Atak istatistikleri
    goals_scored = Column(Integer, default=0, nullable=False, comment='Atılan gol sayısı')
    shots = Column(Integer, default=0, nullable=False, comment='Toplam şut sayısı')
    shots_on_target = Column(Integer, default=0, nullable=False, comment='İsabetli şut sayısı')
    
    # Savunma istatistikleri
    goals_conceded = Column(Integer, default=0, nullable=False, comment='Yenilen gol sayısı')
    clean_sheets = Column(Integer, default=0, nullable=False, comment='Kalesinde gol görmediği maç sayısı')
    
    # Diğer istatistikler
    yellow_cards = Column(Integer, default=0, nullable=False, comment='Sarı kart sayısı')
    red_cards = Column(Integer, default=0, nullable=False, comment='Kırmızı kart sayısı')
    
    # Form ve güncelleme bilgileri
    recent_form = Column(String(10), default='', nullable=False, comment='Son 5 maç formu (Örn: WWDLW)')
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                         nullable=False, comment='Son güncelleme tarihi')
    
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
