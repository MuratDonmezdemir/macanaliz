from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List, TYPE_CHECKING

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship

from .base import BaseModel
from app.extensions import db

if TYPE_CHECKING:
    from .match import Match
    from .player import Player
    from .team import Team

class GoalType(Enum):
    """Gol türleri"""
    REGULAR = 'REGULAR'          # Normal gol
    PENALTY = 'PENALTY'          # Penaltı golü
    OWN_GOAL = 'OWN_GOAL'        # Kendi kalesine gol
    FREE_KICK = 'FREE_KICK'      # Serbest vuruştan gol
    HEADER = 'HEADER'            # Kafa vuruşu ile gol
    LONG_SHOT = 'LONG_SHOT'      # Uak mesafeden gol

class MatchGoal(BaseModel):
    """Maç golleri modeli"""
    __tablename__ = 'match_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # İlişkiler
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id', ondelete='CASCADE'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    scorer_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=True)
    assist_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=True)
    
    # Gol bilgileri
    minute = db.Column(Integer, nullable=False)
    extra_minute = db.Column(Integer, comment='Uzatma dakikası')
    is_own_goal = db.Column(Boolean, default=False)
    is_penalty = db.Column(Boolean, default=False)
    goal_type = db.Column(String(20), default=GoalType.REGULAR.value)  # GoalType enum değeri
    description = db.Column(Text, comment='Golün detaylı açıklaması')
    
    # Zaman damgaları
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # İlişkiler
    match = relationship('Match', back_populates='goals')
    team = relationship('Team', back_populates='goals')
    scorer = relationship('Player', foreign_keys=[scorer_id], back_populates='goals_scored')
    assist = relationship('Player', foreign_keys=[assist_id], back_populates='goal_assists')
    
    def __repr__(self):
        scorer_name = self.scorer.name if hasattr(self.scorer, 'name') else str(self.scorer_id)
        return f'<MatchGoal {scorer_name} @{self.minute}\'>'
    
    def to_dict(self) -> Dict[str, Any]:
        """Nesneyi sözlük olarak döndürür"""
        return {
            'id': self.id,
            'match_id': self.match_id,
            'team_id': self.team_id,
            'scorer_id': self.scorer_id,
            'assist_id': self.assist_id,
            'minute': self.minute,
            'extra_minute': self.extra_minute,
            'is_own_goal': self.is_own_goal,
            'is_penalty': self.is_penalty,
            'goal_type': self.goal_type,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
