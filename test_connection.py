import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API configuration
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "api-football-v1.p.rapidapi.com")
RAPIDAPI_BASE_URL = os.getenv(
    "RAPIDAPI_BASE_URL", "https://api-football-v1.p.rapidapi.com/v3"
)


def test_connection():
    """Test connection to RapidAPI"""
    if not RAPIDAPI_KEY:
        print("HATA: RAPIDAPI_KEY bulunamadi. Lutfen .env dosyanizi kontrol edin.")
        return

    headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": RAPIDAPI_HOST}

    try:
        print("RapidAPI'ye baglanti testi yapiliyor...")
        response = requests.get(f"{RAPIDAPI_BASE_URL}/status", headers=headers)
        response.raise_for_status()

        print("BAGLANTI BASARILI!")
        print("\nMevcut endpoint'ler:")
        for endpoint in (
            response.json().get("response", {}).get("endpoints", [])[:5]
        ):  # Sadece ilk 5 endpoint'i goster
            print(f"- {endpoint}")
        print("... ve daha fazlasi")

    except Exception as e:
        print(f"\nHATA: {str(e)}")
        if hasattr(e, "response"):
            print(f"Hata detayi: {e.response.text}")


if __name__ == "__main__":
    test_connection()
