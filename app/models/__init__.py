"""
Modeller paketi

Bu paket, uygulamanın veritabanı modellerini içerir.
"""
from .athlete import Athlete
# Temel modeller
from .base import BaseModel, db

# Enums
from .enums import (
    PlayerPosition, PlayerStatus, PlayerFoot,
    CardType, MatchStatus, InjuryStatus, InjuryType, 
    TransferType, TransferStatus
)

# Model sınıflarını içe aktar
from .user import User
from .stadium import Stadium
from .season import Season
from .league import League
from .standing import Standing
from .team import Team
from .match import Match, MatchStatistics, MatchStatus
from .match_event import MatchEvent, MatchEventType
from .match_lineup import MatchLineup
from .match_substitution import MatchSubstitution
from .match_card import MatchCard
from .match_goal import MatchGoal, GoalType
from .prediction import Prediction
from .team_statistics import TeamStatistics

# Player related models
from .player import Player
from .player_injury import PlayerInjury, InjuryStatus, InjuryType
from .player_transfer import PlayerTransfer, TransferType, TransferStatus
from .player_statistics import PlayerStatistics

# Tüm modelleri dışa aktar
__all__ = [
    # Base
    'BaseModel',
    'db',
    
    # Enums
    'PlayerPosition',
    'PlayerStatus',
    'PlayerFoot',
    'CardType',
    'MatchStatus',
    'InjuryStatus',
    'InjuryType',
    'TransferType',
    'TransferStatus',
    
    # Core models
    'User',
    'Stadium',
    'League',
    'Season',
    'Standing',
    'Team',
    'Match',
    'MatchStatistics',
    'MatchEvent',
    'MatchEventType',
    'MatchLineup',
    'MatchSubstitution',
    'MatchCard',
    'MatchGoal',
    'GoalType',
    'Prediction',
    'TeamStatistics',
    
    # Player models
    'Player',
    'PlayerInjury',
    'PlayerTransfer',
    'PlayerStatistics',
    'TeamStatistics',
    'Athlete',
    'init_models'
]

def init_models():
    """Modeller arası ilişkileri başlatır"""
    # Dairesel import sorunlarını önlemek için burada import ediyoruz
    from .team import Team
    from .season import Season
    from .standing import Standing
    from .match import Match
    from .team_statistics import TeamStatistics
    from .league import League
    from .stadium import Stadium
    
    # Takım istatistikleri ilişkileri
    Team.statistics = db.relationship(
        'TeamStatistics', 
        back_populates='team',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='TeamStatistics.team_id'
    )
    
    # Stadyum ilişkileri
    Stadium.teams = db.relationship(
        'Team',
        back_populates='stadium',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    # Lig ilişkileri
    League.teams = db.relationship(
        'Team',
        back_populates='league',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

def init_models():
    """Modeller arası ilişkileri başlatır"""
    # Dairesel import sorunlarını önlemek için burada import ediyoruz
    from .team import Team
    from .season import Season
    from .standing import Standing
    from .match import Match
    from .team_statistics import TeamStatistics
    from .league import League
    from .stadium import Stadium
    
    # Takım istatistikleri ilişkileri
    Team.statistics = db.relationship(
        'TeamStatistics', 
        back_populates='team',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='TeamStatistics.team_id'
    )
    
    # Stadyum ilişkileri
    Stadium.teams = db.relationship(
        'Team',
        back_populates='stadium',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    # Lig ilişkileri
    League.teams = db.relationship(
        'Team',
        back_populates='league',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    # Sezon istatistikleri ilişkileri
    Season.team_statistics = db.relationship(
        'TeamStatistics',
        back_populates='season',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='TeamStatistics.season_id'
    )
    
    # Sezon maç ilişkisi
    Season.matches = db.relationship(
        'Match',
        back_populates='season',
        lazy='dynamic',
        foreign_keys='Match.season_id'
    )
    
    # Sezon puan durumu ilişkisi
    Season.standings = db.relationship(
        'Standing',
        back_populates='season',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='Standing.season_id'
    )
