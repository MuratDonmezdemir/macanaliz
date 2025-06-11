"""
API Kullanım Örneği

Bu dosya, farklı API sağlayıcılarıyla nasıl çalışılacağını gösterir.
"""
import os
from dotenv import load_dotenv
from app.services.api_provider import APIType, get_football_api

def main():
    # .env dosyasından API anahtarlarını yükle
    load_dotenv()
    
    # 1. API-Ninjas ile örnek
    print("\n=== API-Ninjas Örneği ===")
    try:
        api_ninjas = get_football_api(APIType.APININJAS)
        
        # Süper Lig takımlarını getir
        print("\nSüper Lig Takımları:")
        teams = api_ninjas.get_league_teams("turkish_super_lig", 2024)
        for team in teams[:5]:  # İlk 5 takım
            print(f"- {team.get('name')}")
        
        # Örnek maç sorgusu
        print("\nGalatasaray'ın son maçları:")
        matches = api_ninjas.get_team_matches("Galatasaray", 2024)
        for match in matches[:3]:  # Son 3 maç
            print(f"{match.get('matchday', '?')}. Hafta: {match.get('home_team')} {match.get('home_score', '?')}-{match.get('away_score', '?')} {match.get('away_team')}")
    
    except Exception as e:
        print(f"API-Ninjas hatası: {e}")
    
    # 2. Football-Data ile örnek
    print("\n=== Football-Data Örneği ===")
    try:
        football_data = get_football_api(APIType.FOOTBALL_DATA)
        
        # Premier Lig takımlarını getir
        print("\nPremier Lig Takımları:")
        teams = football_data.get_league_teams("premier_league", 2024)
        for team in teams[:5]:  # İlk 5 takım
            print(f"- {team.get('name')}")
        
        # Örnek maç sorgusu
        print("\nArsenal'ın son maçları:")
        matches = football_data.get_team_matches("Arsenal", 2024)
        for match in matches[:3]:  # Son 3 maç
            home_team = match.get('homeTeam', {}).get('name', '?')
            away_team = match.get('awayTeam', {}).get('name', '?')
            score = match.get('score', {})
            print(f"{home_team} {score.get('fullTime', {}).get('home')}-{score.get('fullTime', {}).get('away')} {away_team}")
    
    except Exception as e:
        print(f"Football-Data hatası: {e}")

if __name__ == "__main__":
    main()
