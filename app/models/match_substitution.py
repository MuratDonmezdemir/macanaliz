from datetime import datetime
from typing import Optional, Dict, Any, TYPE_CHECKING

from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from .base import BaseModel
from app.extensions import db

if TYPE_CHECKING:
    from .match import Match
    from .player import Player

class MatchSubstitution(BaseModel):
    """Maç oyuncu değişikliği modeli"""
    __tablename__ = 'match_substitutions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # İlişkiler
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id', ondelete='CASCADE'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    player_in_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    player_out_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    
    # Değişiklik bilgileri
    minute = db.Column(Integer, nullable=False)
    injury = db.Column(db.Boolean, default=False, comment='Sakatlık nedeniyle değişiklik mi?')
    description = db.Column(Text, comment='Değişiklikle ilgili ek açıklamalar')
    
    # Zaman damgaları
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # İlişkiler
    match = relationship('Match', back_populates='substitutions')
    team = relationship('Team', back_populates='substitutions')
    player_in = relationship('Player', foreign_keys=[player_in_id], back_populates='substitutions_in')
    player_out = relationship('Player', foreign_keys=[player_out_id], back_populates='substitutions_out')
    
    def __repr__(self):
        return f'<MatchSubstitution {self.player_out_id} -> {self.player_in_id} @{self.minute}\'>'
    
    def to_dict(self) -> Dict[str, Any]:
        """Nesneyi sözlük olarak döndürür"""
        return {
            'id': self.id,
            'match_id': self.match_id,
            'team_id': self.team_id,
            'player_in_id': self.player_in_id,
            'player_out_id': self.player_out_id,
            'minute': self.minute,
            'injury': self.injury,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
