import json
import requests
from datetime import datetime

# API endpoint (Flask development server default)
BASE_URL = "http://127.0.0.1:5000/api/v1"


# Örnek maç verisi
def get_sample_match():
    return {
        "league_id": 39,  # Premier League
        "home_team_id": 33,  # Manchester United
        "away_team_id": 34,  # Liverpool
        "home_team_strength": 82.5,
        "away_team_strength": 85.2,
        "home_form_last5": 2.0,  # Son 5 maçta ortalama puan
        "away_form_last5": 2.4,
        "h2h_home_wins": 3,
        "h2h_draws": 2,
        "h2h_away_wins": 5,
        "home_goals_avg": 1.8,
        "away_goals_avg": 2.1,
        "home_goals_conceded_avg": 0.9,
        "away_goals_conceded_avg": 1.2,
        "home_corners_avg": 5.8,
        "away_corners_avg": 6.2,
        "home_corners_conceded_avg": 4.5,
        "away_corners_conceded_avg": 3.8,
        "h2h_corners_avg": 10.5,
        "home_possession_avg": 58.2,
        "away_possession_avg": 62.7,
        "is_derby": True,
        "match_importance": 0.9,  # 0-1 arası önem derecesi
        "stadium_capacity": 74310,  # Old Trafford kapasitesi
        "home_attack_strength": 1.1,
        "away_attack_strength": 1.3,
        "home_defense_weakness": 0.8,
        "away_defense_weakness": 0.7,
        "weather_conditions": 2,  # 1: İyi, 2: Orta, 3: Kötü
    }


def test_match_result_prediction():
    """Maç sonucu tahmini testi"""
    url = f"{BASE_URL}/predictions/match_result"
    match_data = get_sample_match()

    print(f"\n{'='*50}")
    print("Maç Sonucu Tahmini İçin İstek Gönderiliyor...")
    print(
        f"Maç: {match_data['home_team_id']} (Ev) vs {match_data['away_team_id']} (Deplasman)"
    )

    response = requests.post(url, json=match_data)

    print(f"\nDurum Kodu: {response.status_code}")
    print("Yanıt:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def test_high_scoring_prediction():
    """Yüksek skor tahmini testi"""
    url = f"{BASE_URL}/predictions/high_scoring"
    match_data = get_sample_match()

    print(f"\n{'='*50}")
    print("Yüksek Skor Tahmini İçin İstek Gönderiliyor...")
    print(
        f"Maç: {match_data['home_team_id']} (Ev) vs {match_data['away_team_id']} (Deplasman)"
    )

    response = requests.post(url, json=match_data)

    print(f"\nDurum Kodu: {response.status_code}")
    print("Yanıt:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def test_corners_prediction():
    """Korner tahmini testi"""
    url = f"{BASE_URL}/predictions/corners"
    match_data = get_sample_match()

    print(f"\n{'='*50}")
    print("Korner Tahmini İçin İstek Gönderiliyor...")
    print(
        f"Maç: {match_data['home_team_id']} (Ev) vs {match_data['away_team_id']} (Deplasman)"
    )

    response = requests.post(url, json=match_data)

    print(f"\nDurum Kodu: {response.status_code}")
    print("Yanıt:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def test_all_predictions():
    """Tüm tahminleri bir arada test et"""
    url = f"{BASE_URL}/predictions/all"
    match_data = get_sample_match()

    print(f"\n{'='*50}")
    print("Tahminler İçin İstek Gönderiliyor...")
    print(
        f"Maç: {match_data['home_team_id']} (Ev) vs {match_data['away_team_id']} (Deplasman)"
    )

    response = requests.post(url, json=match_data)

    print(f"\nDurum Kodu: {response.status_code}")
    print("Yanıt:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def test_batch_predictions():
    """Toplu tahmin testi"""
    url = f"{BASE_URL}/predictions/batch_predict"

    # İki farklı maç için örnek veri
    matches = [
        get_sample_match(),
        {
            **get_sample_match(),
            "home_team_id": 40,  # Manchester City
            "home_team_strength": 88.7,
            "home_form_last5": 2.6,
            "home_goals_avg": 2.5,
            "home_goals_conceded_avg": 0.7,
            "home_corners_avg": 7.1,
            "home_possession_avg": 68.3,
        },
    ]

    print(f"\n{'='*50}")
    print("Toplu Tahmin İçin İstek Gönderiliyor...")

    response = requests.post(url, json={"matches": matches, "prediction_type": "all"})

    print(f"\nDurum Kodu: {response.status_code}")
    print("Yanıt:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    print(f"Tahmin API Testi - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # Tekli tahmin testleri
    test_match_result_prediction()
    test_high_scoring_prediction()
    test_corners_prediction()

    # Tüm tahminler
    test_all_predictions()

    # Toplu tahmin testi
    test_batch_predictions()

    print("\nTestler tamamlandı!")
