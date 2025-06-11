from app.services.futbol_veri_yoneticisi import FutbolVeriYoneticisi


def main():
    print("Football-Data.org API Testi")
    print("==========================")

    yonetici = FutbolVeriYoneticisi()

    # 1. Takımları listele
    print("\n1. Süper Lig Takımları:")
    takimlar = yonetici.takim_verilerini_al()
    for i, takim in enumerate(takimlar[:5], 1):  # İlk 5 takım
        print(f"{i}. {takim['name']} ({takim['shortName']})")

    # 2. Yaklaşan maçlar
    print("\n2. Önümüzdeki 14 Günde Oynanacak Maçlar:")
    maclar = yonetici.mac_verilerini_al("super_lig", gun_sayisi=14)
    for i, mac in enumerate(maclar[:5], 1):  # İlk 5 maç
        tarih = mac["tarih"].split("T")[0]  # Sadece tarih kısmını al
        print(f"{i}. {tarih}: {mac['ev_sahibi']} vs {mac['konuk']}")

    # 3. Puan durumu
    print("\n3. Süper Lig Puan Durumu:")
    puan_durumu = yonetici.puan_durumu_getir("super_lig")
    for takim in puan_durumu[:5]:  # İlk 5 takım
        print(f"{takim['sira']}. {takim['takim']} - {takim['puan']} puan")


if __name__ == "__main__":
    main()
