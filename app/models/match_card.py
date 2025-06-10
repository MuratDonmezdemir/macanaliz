from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, TYPE_CHECKING

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship

from .base import BaseModel
from app.extensions import db

if TYPE_CHECKING:
    from .match import Match
    from .player import Player
    from .team import Team

class CardType(Enum):
    """Kart türleri"""
    YELLOW = 'YELLOW'        # Sarı kart
    YELLOW_RED = 'YELLOW_RED'  # İkinci sarı kart (kırmızı)
    RED = 'RED'              # Direkt kırmızı kart

class MatchCard(BaseModel):
    """Maç kartları modeli"""
    __tablename__ = 'match_cards'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # İlişkiler
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id', ondelete='CASCADE'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    
    # Kart bilgileri
    card_type = db.Column(db.String(20), nullable=False)  # CardType enum değeri
    minute = db.Column(Integer, nullable=False)
    reason = db.Column(Text, comment='Kartın nedeni')
    is_second_yellow = db.Column(Boolean, default=False, comment='İkinci sarı kart mı?')
    
    # Zaman damgaları
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # İlişkiler
    match = relationship('Match', back_populates='cards')
    team = relationship('Team', back_populates='cards')
    player = relationship('Player', back_populates='cards')
    
    def __repr__(self):
        return f'<MatchCard {self.player.name if hasattr(self, "player") else self.player_id} - {self.card_type} @{self.minute}\'>'
    
    def to_dict(self) -> Dict[str, Any]:
        """Nesneyi sözlük olarak döndürür"""
        return {
            'id': self.id,
            'match_id': self.match_id,
            'team_id': self.team_id,
            'player_id': self.player_id,
            'card_type': self.card_type,
            'minute': self.minute,
            'reason': self.reason,
            'is_second_yellow': self.is_second_yellow,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
