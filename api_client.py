import os
import time
import requests
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Çevre değişkenlerini yükle
load_dotenv()


class FutbolAPI:
    def __init__(self):
        """Futbol API istemcisini başlat"""
        self.base_url = "https://free-api-live-football-data.p.rapidapi.com"
        self.headers = {
            "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
            "x-rapidapi-host": os.getenv("RAPIDAPI_HOST"),
        }
        self.rate_limit_remaining = 100  # Varsayılan değer
        self.last_request_time = 0

    def _bekle(self):
        """Rate limit kontrolü yap ve gerekirse bekle"""
        simdiki_zaman = time.time()
        gecen_sure = simdiki_zaman - self.last_request_time

        # Saniyede 10 istek sınırı için bekleme
        if gecen_sure < 0.1:  # 100ms'den az süre geçmişse bekle
            time.sleep(0.1 - gecen_sure)

        self.last_request_time = time.time()

    def _istek_yap(
        self, endpoint: str, params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """API'ye istek yap ve sonucu döndür"""
        self._bekle()
        url = f"{self.base_url}/{endpoint}"

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            # Rate limit bilgilerini güncelle
            self.rate_limit_remaining = int(
                response.headers.get("x-ratelimit-requests-remaining", 100)
            )

            return response.json()

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP Hatası: {http_err}")
            if hasattr(http_err, "response") and hasattr(http_err.response, "text"):
                print(f"Hata Detayı: {http_err.response.text}")
            return None

        except Exception as err:
            print(f"Beklenmeyen Hata: {err}")
            return None

    # FUTBOLCULAR
    def futbolcu_ara(self, arama_metni: str) -> List[Dict]:
        """Futbolcu ara

        Args:
            arama_metni: Aranacak futbolcu adı veya soyadı

        Returns:
            List[Dict]: Eşleşen futbolcuların listesi
        """
        params = {"search": arama_metni}
        yanit = self._istek_yap("football-players-search", params)
        if yanit and yanit.get("status") == "success":
            return yanit.get("response", {}).get("suggestions", [])
        return []

    def futbolcu_detay(self, oyuncu_id: str) -> Optional[Dict]:
        """Futbolcu detaylarını getir

        Args:
            oyuncu_id: Futbolcu ID'si

        Returns:
            Optional[Dict]: Futbolcu detayları veya None
        """
        yanit = self._istek_yap(f"football-players/{oyuncu_id}")
        return yanit if yanit else None

    # LİGLER VE TAKIMLAR
    def takim_ara(self, takim_adi: str) -> List[Dict]:
        """Takım ara

        Args:
            takim_adi: Aranacak takım adı

        Returns:
            List[Dict]: Eşleşen takımların listesi
        """
        params = {"search": takim_adi}
        yanit = self._istek_yap("teams-search", params)
        if yanit and yanit.get("status") == "success":
            return yanit.get("response", {}).get("suggestions", [])
        return []

    def takim_detay(self, takim_id: str) -> Optional[Dict]:
        """Takım detaylarını getir

        Args:
            takim_id: Takım ID'si

        Returns:
            Optional[Dict]: Takım detayları veya None
        """
        yanit = self._istek_yap(f"teams/{takim_id}")
        return yanit if yanit else None

    # MAÇLAR
    def mac_ara(self, arama_metni: str) -> List[Dict]:
        """Maç ara

        Args:
            arama_metni: Aranacak maç bilgisi (takım adı, lig adı vb.)

        Returns:
            List[Dict]: Eşleşen maçların listesi
        """
        params = {"search": arama_metni}
        yanit = self._istek_yap("matches-search", params)
        if yanit and yanit.get("status") == "success":
            return yanit.get("response", {}).get("suggestions", [])
        return []

    def mac_detay(self, mac_id: str) -> Optional[Dict]:
        """Maç detaylarını getir

        Args:
            mac_id: Maç ID'si

        Returns:
            Optional[Dict]: Maç detayları veya None
        """
        yanit = self._istek_yap(f"matches/{mac_id}")
        return yanit if yanit else None


# Kullanım örneği
if __name__ == "__main__":
    # API istemcisini başlat
    api = FutbolAPI()

    # Futbolcu arama örneği
    print("Futbolcu arama örneği (Aranan: 'messi'):")
    futbolcular = api.futbolcu_ara("messi")
    for futbolcu in futbolcular[:5]:  # İlk 5 sonucu göster
        print(
            f"- {futbolcu.get('name')} ({futbolcu.get('team')}, {futbolcu.get('nationality')})"
        )

    # Takım arama örneği
    print("\nTakım arama örneği (Aranan: 'barcelona'):")
    takimlar = api.takim_ara("barcelona")
    for takim in takimlar[:3]:  # İlk 3 sonucu göster
        print(f"- {takim.get('name')} ({takim.get('country')})")

    # Maç arama örneği
    print("\nMaç arama örneği (Aranan: 'champions league'):")
    maclar = api.mac_ara("champions league")
    for mac in maclar[:3]:  # İlk 3 sonucu göster
        print(
            f"- {mac.get('home_team')} vs {mac.get('away_team')} - {mac.get('competition')}"
        )
