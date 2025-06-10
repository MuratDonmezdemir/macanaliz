#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Maç modeli modülü.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from .base import db

class MatchStatus(Enum):
    """Maç durumları"""
    SCHEDULED = 'scheduled'      # Planlandı
    LIVE = 'live'                # Oynanıyor
    HALF_TIME = 'half_time'      # Devre arası
    EXTRA_TIME = 'extra_time'    # Uzatma
    PENALTIES = 'penalties'      # Penaltılar
    FINISHED = 'finished'        # Bitti
    POSTPONED = 'postponed'      # Ertelendi
    SUSPENDED = 'suspended'      # Durduruldu
    CANCELED = 'canceled'        # İptal edildi
    AWARDED = 'awarded'          # Hükmen

@dataclass
class MatchStatistics:
    """Maç istatistikleri"""
    possession: float = 0.0
    shots: int = 0
    shots_on_target: int = 0
    shots_off_target: int = 0
    shots_blocked: int = 0
    passes: int = 0
    accurate_passes: int = 0
    pass_accuracy: float = 0.0
    fouls: int = 0
    corners: int = 0
    offsides: int = 0
    yellow_cards: int = 0
    red_cards: int = 0
    saves: int = 0
    goal_kicks: int = 0
    throw_ins: int = 0
    free_kicks: int = 0

class Match(db.Model):
    """Maç modeli"""
    __tablename__ = 'matches'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Temel bilgiler
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    stadium_id = db.Column(db.Integer, db.ForeignKey('stadiums.id'))
    
    # Skor bilgileri
    home_goals = db.Column(db.Integer, default=0)
    away_goals = db.Column(db.Integer, default=0)
    home_ht_goals = db.Column(db.Integer)  # İlk yarı golleri
    away_ht_goals = db.Column(db.Integer)
    home_ft_goals = db.Column(db.Integer)  # İkinci yarı golleri
    away_ft_goals = db.Column(db.Integer)
    home_et_goals = db.Column(db.Integer)  # Uzatma golleri
    away_et_goals = db.Column(db.Integer)
    home_penalties = db.Column(db.Integer)  # Penaltı golleri
    away_penalties = db.Column(db.Integer)
    
    # Maç bilgileri
    match_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(MatchStatus), default=MatchStatus.SCHEDULED)
    matchday = db.Column(db.Integer)  # Hafta sayısı
    stage = db.Column(db.String(50))  # Grup aşaması, çeyrek final vb.
    group = db.Column(db.String(10))  # Grup adı (A, B, C...)
    
    # İstatistikler (JSON olarak saklanacak)
    home_stats = db.Column(db.JSON)
    away_stats = db.Column(db.JSON)
    
    # Zaman damgaları
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    home_team = db.relationship('Team', foreign_keys=[home_team_id], backref='home_matches')
    away_team = db.relationship('Team', foreign_keys=[away_team_id], backref='away_matches')
    league = db.relationship('League', backref='matches')
    stadium = db.relationship('Stadium', backref='matches')
    
    @property
    def is_finished(self) -> bool:
        """Maçın bitip bitmediğini döndürür"""
        return self.status == MatchStatus.FINISHED
    
    @property
    def is_live(self) -> bool:
        """Maçın canlı olup olmadığını döndürür"""
        return self.status in [MatchStatus.LIVE, MatchStatus.HALF_TIME, 
                              MatchStatus.EXTRA_TIME, MatchStatus.PENALTIES]
    
    def get_winner(self) -> Optional[int]:
        """Maçı kazanan takımın ID'sini döndürür, berabere ise None"""
        if not self.is_finished:
            return None
            
        if self.home_goals > self.away_goals:
            return self.home_team_id
        elif self.away_goals > self.home_goals:
            return self.away_team_id
        
        # Beraberlik durumunda uzatma veya penaltı kontrolü
        if self.home_et_goals is not None and self.away_et_goals is not None:
            if self.home_et_goals > self.away_et_goals:
                return self.home_team_id
            elif self.away_et_goals > self.home_et_goals:
                return self.away_team_id
        
        if self.home_penalties is not None and self.away_penalties is not None:
            if self.home_penalties > self.away_penalties:
                return self.home_team_id
            elif self.away_penalties > self.home_penalties:
                return self.away_team_id
        
        return None  # Beraberlik
    
    def to_dict(self) -> Dict[str, Any]:
        """Nesneyi sözlük olarak döndürür"""
        return {
            'id': self.id,
            'home_team_id': self.home_team_id,
            'away_team_id': self.away_team_id,
            'league_id': self.league_id,
            'stadium_id': self.stadium_id,
            'home_goals': self.home_goals,
            'away_goals': self.away_goals,
            'match_date': self.match_date.isoformat() if self.match_date else None,
            'status': self.status.value if self.status else None,
            'matchday': self.matchday,
            'stage': self.stage,
            'group': self.group,
            'home_stats': self.home_stats,
            'away_stats': self.away_stats,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }