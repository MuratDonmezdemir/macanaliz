"""Lig modeli"""
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from .base import BaseModel
from app.extensions import db

if TYPE_CHECKING:
    from .team import Team
    from .season import Season

class League(BaseModel):
    """Lig modeli"""
    __tablename__ = 'leagues'
    __table_args__ = (
        db.Index('idx_leagues_country', 'country'),
        db.Index('idx_leagues_active', 'is_active'),
        {'comment': 'Futbol liglerinin kaydedildiği tablo'}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(100), 
        nullable=False, 
        index=True,
        comment='Ligin tam adı'
    )
    code = db.Column(
        db.String(10), 
        unique=True, 
        nullable=False,
        comment='Lig kısaltması (Örn: PL, SL, SA)'
    )
    country = db.Column(
        db.String(50),
        index=True,
        comment='Ligin ülkesi'
    )
    logo = db.Column(
        db.String(200),
        comment='Lig logosu URL'
    )
    season = db.Column(
        db.String(20),
        comment='Mevcut sezon (Örn: 2023/2024)'
    )
    current_champion = db.Column(
        db.String(100),
        comment='Son şampiyon takım'
    )
    founded = db.Column(
        db.Integer,
        comment='Kuruluş yılı'
    )
    is_active = db.Column(
        db.Boolean, 
        default=True,
        index=True,
        comment='Aktif lig mi?'
    )
    created_at = db.Column(
        db.DateTime, 
        default=datetime.utcnow,
        nullable=False,
        comment='Oluşturulma tarihi'
    )
    updated_at = db.Column(
        db.DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow,
        nullable=False,
        comment='Son güncelleme tarihi'
    )
    
    # İlişkiler
    teams = db.relationship(
        'Team', 
        back_populates='league', 
        lazy='dynamic',
        cascade='all, delete-orphan',
        passive_deletes=True
    )
    seasons = db.relationship(
        'Season', 
        back_populates='league', 
        lazy='dynamic',
        cascade='all, delete-orphan',
        passive_deletes=True
    )
    
    def __repr__(self):
        return f'<League {self.name}>'
    
    def to_dict(self):
        """Lig bilgilerini sözlük olarak döndürür"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'country': self.country,
            'logo': self.logo,
            'season': self.season,
            'current_champion': self.current_champion,
            'founded': self.founded,
            'is_active': self.is_active
        }
