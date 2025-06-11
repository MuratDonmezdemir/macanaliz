import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API configuration
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")
RAPIDAPI_BASE_URL = os.getenv("RAPIDAPI_BASE_URL")

# Headers for RapidAPI
headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": RAPIDAPI_HOST}


def test_connection():
    """Test connection to RapidAPI"""
    try:
        # Test endpoint - get available endpoints
        response = requests.get(f"{RAPIDAPI_BASE_URL}/status", headers=headers)
        response.raise_for_status()

        print("✅ Bağlantı başarılı!")
        print("Mevcut endpoint'ler:")
        for endpoint in response.json().get("response", {}).get("endpoints", []):
            print(f"- {endpoint}")

    except Exception as e:
        print(f"❌ Hata oluştu: {str(e)}")
        if hasattr(e, "response"):
            print(f"Hata detayı: {e.response.text}")


if __name__ == "__main__":
    print("RapidAPI bağlantı testi başlatılıyor...")
    print(
        f"API Anahtarı: {RAPIDAPI_KEY[:10]}..."
        if RAPIDAPI_KEY
        else "❌ API anahtarı bulunamadı!"
    )

    if RAPIDAPI_KEY:
        test_connection()
