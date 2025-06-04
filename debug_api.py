import os
import requests
from dotenv import load_dotenv

# Çevre değişkenlerini yükle
load_dotenv()

def test_futbolcu_arama():
    url = "https://free-api-live-football-data.p.rapidapi.com/football-players-search"
    
    headers = {
        'x-rapidapi-key': os.getenv('RAPIDAPI_KEY'),
        'x-rapidapi-host': os.getenv('RAPIDAPI_HOST')
    }
    
    params = {'search': 'messi'}
    
    print("API İsteği Gönderiliyor...")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Params: {params}")
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        print("\nAPI Yanıtı:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print("\nYanıt İçeriği:")
        print(response.text)
        
        # JSON olarak ayrıştırılmış hali
        try:
            json_data = response.json()
            print("\nJSON Verisi:")
            print(json_data)
            
            # Eğer liste ise ilk birkaç öğeyi göster
            if isinstance(json_data, list):
                print(f"\nToplam {len(json_data)} sonuç bulundu.")
                for i, item in enumerate(json_data[:3], 1):
                    print(f"\n{i}. Öğe:")
                    for key, value in item.items():
                        print(f"  {key}: {value}")
            
        except ValueError as e:
            print(f"\nJSON Ayrıştırma Hatası: {e}")
        
    except requests.exceptions.RequestException as e:
        print(f"\nİstek Hatası: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Hata Detayı: {e.response.text}")

if __name__ == "__main__":
    print("API Testi Başlatılıyor...")
    test_futbolcu_arama()
