/from .base import BaseModel
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime

class TeamStatistics(BaseModel):
    """Takım istatistikleri modeli"""
    
    __tablename__ = 'team_statistics'
    
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    season_id = Column(Integer, ForeignKey('seasons.id'), nullable=False)
    
    # Genel istatistikler
    total_matches = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    
    # Atak istatistikleri
    goals_scored = Column(Integer, default=0)
    shots = Column(Integer, default=0)
    shots_on_target = Column(Integer, default=0)
    
    # Savunma istatistikleri
    goals_conceded = Column(Integer, default=0)
    clean_sheets = Column(Integer, default=0)
    
    # Form istatistikleri
    recent_form = Column(String(10))  # Son maçlardaki form (W/D/L)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # İlişkiler
    team = relationship('Team', back_populates='statistics')
    season = relationship('Season')
