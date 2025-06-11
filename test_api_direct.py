import os
import requests
from dotenv import load_dotenv


def main():
    # API anahtarını doğrudan ayarla
    api_key = "7684c85228da411d89afd546cd3958f3"

    # API endpoint'leri
    base_url = "http://api.football-data.org/v4"
    headers = {"X-Auth-Token": api_key, "Content-Type": "application/json"}

    print("1. Süper Lig (Türkiye) bilgilerini çekiyorum...")
    try:
        # Süper Lig bilgilerini çek (ID: 2014)
        response = requests.get(f"{base_url}/competitions/2014/teams", headers=headers)
        response.raise_for_status()
        teams = response.json()

        print("\nSüper Lig Takımları:")
        for team in teams["teams"][:5]:  # İlk 5 takımı göster
            print(f"- {team['name']} ({team['shortName']})")

        # Yaklaşan maçları çek
        print("\n2. Yaklaşan maçları çekiyorum...")
        from datetime import datetime, timedelta

        today = datetime.now().strftime("%Y-%m-%d")
        next_week = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

        response = requests.get(
            f"{base_url}/competitions/2014/matches",
            headers=headers,
            params={"dateFrom": today, "dateTo": next_week, "status": "SCHEDULED"},
        )
        response.raise_for_status()
        matches = response.json()

        print("\nYaklaşan Maçlar:")
        for match in matches["matches"][:5]:  # İlk 5 maçı göster
            date = match["utcDate"].split("T")[0]
            print(
                f"{date}: {match['homeTeam']['shortName']} vs {match['awayTeam']['shortName']}"
            )

        # Puan durumunu çek
        print("\n3. Puan durumunu çekiyorum...")
        response = requests.get(
            f"{base_url}/competitions/2014/standings", headers=headers
        )
        response.raise_for_status()
        standings = response.json()

        print("\nSüper Lig Puan Durumu:")
        for team in standings["standings"][0]["table"][:5]:  # İlk 5 takım
            print(f"{team['position']}. {team['team']['name']} - {team['points']} puan")

    except requests.exceptions.RequestException as e:
        print(f"\nHATA: API isteği başarısız oldu: {str(e)}")
        if hasattr(e, "response") and e.response:
            print(f"Hata detayı: {e.response.text}")


if __name__ == "__main__":
    main()
