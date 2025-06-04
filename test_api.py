import os
import sys
from dotenv import load_dotenv
import requests

# Çevre değişkenlerini yükle
load_dotenv()

def test_api_baglantisi():
    """API bağlantısını test et"""
    url = "https://api-football-v1.p.rapidapi.com/v3/status"
    headers = {
        'x-rapidapi-key': os.getenv('RAPIDAPI_KEY'),
        'x-rapidapi-host': os.getenv('RAPIDAPI_HOST')
    }
    
    try:
        print("API bağlantısı test ediliyor...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # API'den gelen yanıtı kontrol et
        veri = response.json()
        
        print("\n✅ Başarılı: API'ye başarıyla bağlanıldı!")
        print(f"API Durumu: {veri.get('response', {}).get('requests', 'Bilinmiyor')}")
        print(f"Kalan İstek Hakkı: {veri.get('response', {}).get('requests_limit_day', 'Bilinmiyor')}")
        
        return True
        
    except Exception as hata:
        print("\n❌ Hata: API'ye bağlanılamadı!")
        print(f"Hata Detayı: {str(hata)}")
        if hasattr(hata, 'response') and hasattr(hata.response, 'text'):
            print(f"API Yanıtı: {hata.response.text}")
        return False

if __name__ == "__main__":
    # API anahtarını kontrol et
    if not os.getenv('RAPIDAPI_KEY') or not os.getenv('RAPIDAPI_HOST'):
        print("HATA: Lütfen .env dosyasında API anahtarlarınızı kontrol edin!")
        sys.exit(1)
    
    test_api_baglantisi()
