from api_client import FutbolAPI


def main():
    # API istemcisini başlat
    api = FutbolAPI()

    # 1. Futbolcu arama örneği
    print("1. Futbolcu Arama")
    print("================")
    arama_sonucu = api.futbolcu_ara("messi")

    if arama_sonucu:
        print(f"\n{len(arama_sonucu)} sonuç bulundu. İlk 5 sonuç:")
        for i, futbolcu in enumerate(arama_sonucu[:5], 1):
            print(
                f"{i}. {futbolcu.get('name')} - {futbolcu.get('team')} ({futbolcu.get('nationality')})"
            )

        # İlk futbolcunun detaylarını getir
        if arama_sonucu:
            ilk_futbolcu_id = arama_sonucu[0].get("id")
            if ilk_futbolcu_id:
                futbolcu_detay = api.futbolcu_detay(ilk_futbolcu_id)
                if futbolcu_detay:
                    print("\nFutbolcu Detayları:")
                    print(f"İsim: {futbolcu_detay.get('name')}")
                    print(f"Yaş: {futbolcu_detay.get('age')}")
                    print(f"Boy: {futbolcu_detay.get('height')}")
                    print(f"Kilo: {futbolcu_detay.get('weight')}")
                    print(f"Mevki: {futbolcu_detay.get('position')}")
                    print(f"Takım: {futbolcu_detay.get('team')}")

    # 2. Takım arama örneği
    print("\n2. Takım Arama")
    print("==============")
    takim_sonucu = api.takim_ara("barcelona")

    if takim_sonucu:
        print(f"\n{len(takim_sonucu)} sonuç bulundu. İlk 3 sonuç:")
        for i, takim in enumerate(takim_sonucu[:3], 1):
            print(
                f"{i}. {takim.get('name')} - {takim.get('country')} ({takim.get('founded')})"
            )

    # 3. Maç arama örneği
    print("\n3. Maç Arama")
    print("============")
    mac_sonucu = api.mac_ara("champions league")

    if mac_sonucu:
        print(f"\n{len(mac_sonucu)} sonuç bulundu. İlk 3 maç:")
        for i, mac in enumerate(mac_sonucu[:3], 1):
            print(f"{i}. {mac.get('home_team')} vs {mac.get('away_team')}")
            print(f"   Tarih: {mac.get('date')}")
            print(f"   Turnuva: {mac.get('competition')}")
            print(f"   Skor: {mac.get('home_goals', '?')}-{mac.get('away_goals', '?')}")
            print()


if __name__ == "__main__":
    main()
