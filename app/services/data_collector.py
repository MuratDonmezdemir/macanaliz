import os
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
from app.services.api_provider import APIType, get_football_api

class DataCollector:
    """Futbol maç verilerini toplar"""
    
    def __init__(self, api_type: APIType = APIType.APININJAS):
        """Veri toplayıcıyı başlatır"""
        load_dotenv()
        self.api = get_football_api(api_type)
        self.current_season = datetime.now().year
    
    def get_team_last_matches(self, team_name: str, num_matches: int = 7) -> List[Dict[str, Any]]:
        """Bir takımın son maçlarını getirir"""
        try:
            matches = self.api.get_team_matches(team_name, self.current_season)
            # En son maçlardan istenen kadarını al
            return sorted(
                matches,
                key=lambda x: x.get('date', ''),
                reverse=True
            )[:num_matches]
        except Exception as e:
            print(f"Hata: {e}")
            return []
    
    def get_head_to_head(self, team1: str, team2: str) -> List[Dict[str, Any]]:
        """İki takım arasındaki son maçları getirir"""
        try:
            return self.api.get_head_to_head(team1, team2, self.current_season)
        except Exception as e:
            print(f"Hata: {e}")
            return []

# Kullanım örneği
if __name__ == "__main__":
    collector = DataCollector()
    
    # Örnek: Galatasaray'ın son 5 maçını getir
    print("Galatasaray'ın son maçları:")
    matches = collector.get_team_last_matches("Galatasaray", 5)
    for match in matches:
        print(f"{match.get('home_team')} {match.get('home_score')}-{match.get('away_score')} {match.get('away_team')}")
    
    # Örnek: Galatasaray-Fenerbahçe maçları
    print("\nGalatasaray - Fenerbahçe maçları:")
    h2h = collector.get_head_to_head("Galatasaray", "Fenerbahce")
    for match in h2h:
        print(f"{match.get('home_team')} {match.get('home_score')}-{match.get('away_score')} {match.get('away_team')}")
