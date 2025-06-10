from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, TYPE_CHECKING

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from .base import BaseModel
from app.extensions import db

if TYPE_CHECKING:
    from .match import Match
    from .team import Team
    from .player import Player

class MatchEventType(Enum):
    """Maç olay tipleri"""
    GOAL = 'GOAL'  # Gol
    YELLOW_CARD = 'YELLOW_CARD'  # Sarı kart
    RED_CARD = 'RED_CARD'  # Kırmızı kart
    SUBSTITUTION = 'SUBSTITUTION'  # Oyuncu değişikliği
    INJURY = 'INJURY'  # Sakatlık
    PENALTY = 'PENALTY'  # Penaltı
    PENALTY_MISS = 'PENALTY_MISS'  # Penaltı kaçırma
    OWN_GOAL = 'OWN_GOAL'  # Kendi kalesine gol
    VAR = 'VAR'  # VAR kararı
    OTHER = 'OTHER'  # Diğer

class MatchEvent(BaseModel):
    """Maç olayları modeli"""
    __tablename__ = 'match_events'
    
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id', ondelete='CASCADE'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id', ondelete='CASCADE'))
    player_id = db.Column(db.Integer, db.ForeignKey('players.id', ondelete='CASCADE'))
    event_type = db.Column(SQLEnum(MatchEventType), nullable=False)
    minute = db.Column(db.Integer, nullable=False)
    extra_minute = db.Column(db.Integer)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # İlişkiler
    match = relationship('Match', back_populates='events')
    team = relationship('Team')
    player = relationship('Player')
    
    def __repr__(self):
        return f'<MatchEvent {self.event_type} - {self.minute}>'
    
    def to_dict(self) -> Dict[str, Any]:
        """Olay bilgilerini sözlük olarak döndürür"""
        return {
            'id': self.id,
            'match_id': self.match_id,
            'team_id': self.team_id,
            'player_id': self.player_id,
            'event_type': self.event_type.value,
            'minute': self.minute,
            'extra_minute': self.extra_minute,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
