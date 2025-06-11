import os
import requests
from typing import Dict, Any, List, Optional
from .api_provider import BaseFootballAPI

class APINinjasAPI(BaseFootballAPI):
    """API-Ninjas Football API implementasyonu"""
    
    BASE_URL = "https://api.api-ninjas.com/v1/football"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("API_NINJAS_KEY")
        if not self.api_key:
            raise ValueError("API_NINJAS_KEY environment variable not set")
            
        self.headers = {"X-Api-Key": self.api_key}
    
    def _make_request(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """API'ye istek gönderir"""
        try:
            response = requests.get(
                self.BASE_URL,
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json() or []
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return []
    
    def get_league_teams(self, league: str, season: int) -> List[Dict[str, Any]]:
        """Ligdeki takımları getirir"""
        return self._make_request({
            "league": league,
            "season": str(season)
        })
    
    def get_team_matches(self, team: str, season: int) -> List[Dict[str, Any]]:
        """Takımın maçlarını getirir"""
        return self._make_request({
            "team": team,
            "season": str(season)
        })
    
    def get_head_to_head(self, team1: str, team2: str, season: Optional[int] = None) -> List[Dict[str, Any]]:
        """İki takım arasındaki maçları getirir"""
        params = {"team1": team1, "team2": team2}
        if season:
            params["season"] = str(season)
        return self._make_request(params)
