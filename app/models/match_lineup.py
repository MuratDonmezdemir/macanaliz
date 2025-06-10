from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List, TYPE_CHECKING

from sqlalchemy import Column, Integer, String, Boolean, Text, JSON, Boolean
from sqlalchemy.orm import relationship

from .base import BaseModel
from app.extensions import db

if TYPE_CHECKING:
    from .match import Match
    from .player import Player

class PlayerPosition(Enum):
    """Oyuncu pozisyonları"""
    GOALKEEPER = 'GOALKEEPER'  # Kaleci
    DEFENDER = 'DEFENDER'      # Defans
    MIDFIELDER = 'MIDFIELDER'  # Orta saha
    FORWARD = 'FORWARD'        # Forvet

class MatchLineup(BaseModel):
    """Maç kadrosu modeli"""
    __tablename__ = 'match_lineups'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # İlişkiler
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id', ondelete='CASCADE'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    
    # Kadro bilgileri
    position = db.Column(db.String(50), nullable=False)  # PlayerPosition enum değeri
    shirt_number = db.Column(db.Integer)
    is_captain = db.Column(db.Boolean, default=False)
    is_substitute = db.Column(Boolean, default=False)
    
    # İstatistikler (opsiyonel)
    stats = db.Column(JSON, default=dict)
    
    # Zaman damgaları
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # İlişkiler
    match = relationship('Match', back_populates='lineups')
    player = relationship('Player', back_populates='lineups')
    team = relationship('Team', back_populates='lineups')
    
    def __repr__(self):
        return f'<MatchLineup {self.player.name if hasattr(self, "player") else self.player_id} - {self.position}>'
    
    def to_dict(self) -> Dict[str, Any]:
        """Nesneyi sözlük olarak döndürür"""
        return {
            'id': self.id,
            'match_id': self.match_id,
            'player_id': self.player_id,
            'team_id': self.team_id,
            'position': self.position,
            'shirt_number': self.shirt_number,
            'is_captain': self.is_captain,
            'is_substitute': self.is_substitute,
            'stats': self.stats,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
