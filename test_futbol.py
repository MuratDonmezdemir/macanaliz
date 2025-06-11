import os
import sys
import json
from datetime import datetime, timedelta

# Karakter kodlaması sorunlarını çözmek için
import sys
import codecs

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")

# Proje kök dizinini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.futbol_veri_yoneticisi import FutbolVeriYoneticisi


def print_bold(text):
    """Kalın yazı için yardımcı fonksiyon"""
    print(f"\033[1m{text}\033[0m")


def main():
    print_bold("\nFutbol Veri Yöneticisi Testi - TheSportsDB")
    print("=" * 40)

    yonetici = FutbolVeriYoneticisi()

    # 1. Tüm ligleri listele
    print_bold("\n1. Tüm Ligler:")
    for lig_adi, lig_bilgisi in yonetici.ligler.items():
        print(f"- {lig_bilgisi['ad']} (ID: {lig_bilgisi['id']})")

    # 2. Premier League takımlarını getir (daha güvenilir veri için)
    print_bold("\n2. Premier League Takımları:")
    try:
        takimlar = yonetici.takim_verilerini_al(lig_adi="premier_league")
        if not takimlar:
            print("Takım bulunamadı.")
        else:
            for i, takim in enumerate(takimlar[:10], 1):  # İlk 10 takım
                print(
                    f"{i}. {takim.get('strTeam', 'Bilinmeyen')} - {takim.get('strStadium', 'Bilinmeyen Stadyum')}"
                )
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")

    # 3. Premier League maçlarını getir
    print_bold("\n3. Önümüzdeki 30 Günde Oynanacak Maçlar (Premier League):")
    try:
        maclar = yonetici.mac_verilerini_al("premier_league", gun_sayisi=30)
        if not maclar:
            print("Maç bulunamadı.")
        else:
            for i, mac in enumerate(maclar[:5], 1):  # İlk 5 maç
                print(
                    f"{i}. {mac.get('tarih', '?')} {mac.get('saat', '')} - {mac.get('ev_sahibi', '?')} vs {mac.get('konuk', '?')}"
                )
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")

    # 4. Premier League puan durumu
    print_bold("\n4. Premier League Puan Durumu:")
    try:
        puan_durumu = yonetici.puan_durumu_getir("premier_league")
        if not puan_durumu:
            print("Puan durumu bulunamadı.")
        else:
            for takim in puan_durumu[:5]:  # İlk 5 takım
                print(
                    f"{takim.get('sira', '?')}. {takim.get('takim', 'Bilinmeyen')} - {takim.get('puan', 0)} puan"
                )
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")


if __name__ == "__main__":
    main()
