
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os
from tqdm import tqdm

# Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FootballDataCollector:
    """Futbol verilerini toplamak için sınıf"""
    
    def __init__(self, api_key: str = None):
        """
        Args:
            api_key: API anahtarı (opsiyonel, .env'den de alınabilir)
        """
        self.api_key = api_key or os.getenv('FOOTBALL_API_KEY')
        self.base_url = "https://api.football-data.org/v4"
        self.headers = {
            'X-Auth-Token': self.api_key,
            'Content-Type': 'application/json'
        }
        self.cache_dir = "data/cache"
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """API'ye istek yapar"""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API isteği başarısız: {e}")
            return {}
    
    def get_team_matches(self, team_id: int, limit: int = 10) -> List[Dict]:
        """Bir takımın son maçlarını getirir"""
        endpoint = f"teams/{team_id}/matches"
        params = {
            'limit': limit,
            'status': 'FINISHED',
            'dateFrom': (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
            'dateTo': datetime.now().strftime('%Y-%m-%d')
        }
        return self._make_request(endpoint, params).get('matches', [])
    
    def get_team_info(self, team_id: int) -> Dict:
        """Takım bilgilerini getirir"""
        endpoint = f"teams/{team_id}"
        return self._make_request(endpoint)
    
    def get_match_details(self, match_id: int) -> Dict:
        """Maç detaylarını getirir"""
        endpoint = f"matches/{match_id}"
        return self._make_request(endpoint)
    
    def get_league_standings(self, league_id: int, season: int = None) -> Dict:
        """Lig sıralamasını getirir"""
        if not season:
            season = datetime.now().year
        endpoint = f"competitions/{league_id}/standings"
        params = {'season': season}
        return self._make_request(endpoint, params)
    
    def get_team_players(self, team_id: int) -> List[Dict]:
        """Takım oyuncularını getirir"""
        endpoint = f"teams/{team_id}"
        data = self._make_request(endpoint)
        return data.get('squad', [])
    
    def get_head_to_head(self, team1_id: int, team2_id: int, limit: int = 5) -> List[Dict]:
        """İki takım arasındaki son karşılaşmaları getirir"""
        endpoint = f"teams/{team1_id}/matches"
        params = {
            'limit': limit,
            'status': 'FINISHED',
            'head2head': team2_id
        }
        return self._make_request(endpoint, params).get('matches', [])
    
    def cache_team_data(self, team_id: int, days: int = 30):
        """Takım verilerini önbelleğe alır"""
        cache_file = os.path.join(self.cache_dir, f"team_{team_id}.json")
        
        # Önbellekten veriyi yükle
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # API'den veriyi çek
        team_info = self.get_team_info(team_id)
        matches = self.get_team_matches(team_id, limit=20)  # Son 20 maç
        
        # Oyuncu bilgilerini al
        players = self.get_team_players(team_id)
        
        data = {
            'team': team_info,
            'matches': matches,
            'players': players,
            'last_updated': datetime.now().isoformat()
        }
        
        # Önbelleğe kaydet
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return data
