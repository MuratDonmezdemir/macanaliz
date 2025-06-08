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
from .match import Match, MatchStatistics, Prediction
from .team_statistics import TeamStatistics

# Tüm modelleri dışa aktar
__all__ = [
    'BaseModel',
    'User',
    'Stadium',
    'TeamStatistics',
    'League',
    'Season',
    'Standing',
    'Team',
    'Match',
    'MatchStatistics',
    'Prediction'
]
