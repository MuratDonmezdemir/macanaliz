import os
import requests
from typing import Dict, Any, List, Optional
from .api_provider import BaseFootballAPI

class FootballDataAPI(BaseFootballAPI):
    """Football-Data.org API implementasyonu"""
    
    BASE_URL = "http://api.football-data.org/v4"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("FOOTBALL_DATA_KEY")
        if not self.api_key:
            raise ValueError("FOOTBALL_DATA_KEY environment variable not set")
            
        self.headers = {"X-Auth-Token": self.api_key}
    
    def _make_request(self, endpoint: str) -> Dict[str, Any]:
        """API'ye istek gönderir"""
        try:
            response = requests.get(
                f"{self.BASE_URL}{endpoint}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return {}
    
    def get_league_teams(self, league: str, season: int) -> List[Dict[str, Any]]:
        """Ligdeki takımları getirir"""
        # Football-Data için lig kodlarını eşleştirme
        league_codes = {
            "premier_league": "PL",
            "la_liga": "PD",
            "bundesliga": "BL1",
            "serie_a": "SA",
            "ligue_1": "FL1"
        }
        
        league_code = league_codes.get(league.lower())
        if not league_code:
            return []
            
        data = self._make_request(f"/competitions/{league_code}/teams")
        return data.get("teams", [])
    
    def get_team_matches(self, team: str, season: int) -> List[Dict[str, Any]]:
        """Takımın maçlarını getirir"""
        # Önce takım ID'sini bulalım
        teams_data = self._make_request(f"/teams?name={team}")
        if not teams_data.get("teams"):
            return []
            
        team_id = teams_data["teams"][0]["id"]
        
        # Sonra maçları çekelim
        matches_data = self._make_request(f"/teams/{team_id}/matches")
        return matches_data.get("matches", [])
    
    def get_head_to_head(self, team1: str, team2: str, season: Optional[int] = None) -> List[Dict[str, Any]]:
        """İki takım arasındaki maçları getirir"""
        # Bu API'de doğrudan head-to-head endpoint'i yok,
        # bu yüzden her iki takımın da maçlarını çekip filtreleyeceğiz
        team1_matches = self.get_team_matches(team1, season or 2024)
        
        # Takım2'nin ID'sini bulalım
        teams_data = self._make_request(f"/teams?name={team2}")
        if not teams_data.get("teams"):
            return []
            
        team2_id = teams_data["teams"][0]["id"]
        
        # Sadece iki takım arasındaki maçları filtrele
        return [
            match for match in team1_matches 
            if match["homeTeam"]["id"] == team2_id or match["awayTeam"]["id"] == team2_id
        ]
