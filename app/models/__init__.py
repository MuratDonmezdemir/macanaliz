"""
Modeller paketi

Bu paket, uygulamanın veritabanı modellerini içerir.
"""

# Temel modeller
from .base import BaseModel

# Model sınıflarını içe aktar
from .user import User
from .stadium import Stadium
from .league import League, Season, Standing
from .team import Team
from .match import Match
from .match import MatchStatistics
from .prediction import Prediction
from .team_statistics import TeamStatistics
from .player import Player, PlayerStatistics
from .athlete import Athlete

# Veritabanı uzantısını içe aktar
from app.extensions import db

# Tüm modelleri dışa aktar
__all__ = [
    'BaseModel',
    'User',
    'Stadium',
    'League',
    'Season',
    'Standing',
    'Team',
    'Match',
    'MatchStatistics',
    'Prediction',
    'TeamStatistics',
    'Player',
    'PlayerStatistics',
    'Athlete',
    'init_models'
]

def init_models():
    """Modeller arası ilişkileri başlatır"""
    # Dairesel import sorunlarını önlemek için burada import ediyoruz
    from .league import Season
    from .team import Team
    
    # Takım istatistikleri ilişkileri
    Team.statistics = db.relationship(
        'TeamStatistics', 
        back_populates='team',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='TeamStatistics.team_id'
    )
    
    # Sezon istatistikleri ilişkileri
    Season.team_statistics = db.relationship(
        'TeamStatistics',
        back_populates='season',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='TeamStatistics.season_id'
    )
    
    # Diğer model ilişkileri buraya eklenecek
