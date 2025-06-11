from enum import Enum
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class APIType(Enum):
    """Desteklenen API türleri"""
    APININJAS = "api_ninjas"
    FOOTBALL_DATA = "football_data"

class BaseFootballAPI(ABC):
    """Tüm API servisleri için temel arayüz"""
    
    @abstractmethod
    def get_league_teams(self, league: str, season: int) -> List[Dict[str, Any]]:
        """Ligdeki takımları getirir"""
        pass
    
    @abstractmethod
    def get_team_matches(self, team: str, season: int) -> List[Dict[str, Any]]:
        """Takımın maçlarını getirir"""
        pass
    
    @abstractmethod
    def get_head_to_head(self, team1: str, team2: str, season: Optional[int] = None) -> List[Dict[str, Any]]:
        """İki takım arasındaki maçları getirir"""
        pass

def get_football_api(api_type: APIType, **kwargs) -> BaseFootballAPI:
    """İstenen türde bir API istemcisi döndürür"""
    if api_type == APIType.APININJAS:
        from .api_ninjas import APINinjasAPI
        return APINinjasAPI(**kwargs)
    elif api_type == APIType.FOOTBALL_DATA:
        from .football_data import FootballDataAPI
        return FootballDataAPI(**kwargs)
    else:
        raise ValueError(f"Desteklenmeyen API türü: {api_type}")
