from app import db, teams
from database_utils import initialize_sample_data
from models import Team, Match, Prediction, Country, League, TeamStatistics
from datetime import datetime, timedelta
import random

def create_countries():
    """Ülkeleri oluştur"""
    countries = [
        {"name": "Türkiye", "code": "TUR", "flag": "https://flagcdn.com/tr.svg"},
        {"name": "İngiltere", "code": "ENG", "flag": "https://flagcdn.com/gb-eng.svg"},
        {"name": "İspanya", "code": "ESP", "flag": "https://flagcdn.com/es.svg"},
        {"name": "İtalya", "code": "ITA", "flag": "https://flagcdn.com/it.svg"},
        {"name": "Almanya", "code": "GER", "flag": "https://flagcdn.com/de.svg"},
        {"name": "Fransa", "code": "FRA", "flag": "https://flagcdn.com/fr.svg"}
    ]
    
    country_objs = []
    for country_data in countries:
        country = Country.query.filter_by(code=country_data['code']).first()
        if not country:
            country = Country(
                name=country_data['name'],
                code=country_data['code'],
                flag=country_data['flag']
            )
            db.session.add(country)
        country_objs.append(country)
    
    db.session.commit()
    return country_objs

def create_leagues(countries):
    """Ligleri oluştur"""
    leagues_data = [
        {"name": "Süper Lig", "short_name": "SL", "country_code": "TUR", "level": 1, "logo": "https://example.com/logo/superlig.png"},
        {"name": "1. Lig", "short_name": "1L", "country_code": "TUR", "level": 2, "logo": "https://example.com/logo/1lig.png"},
        {"name": "Premier League", "short_name": "EPL", "country_code": "ENG", "level": 1, "logo": "https://example.com/logo/premierleague.png"},
        {"name": "La Liga", "short_name": "LL", "country_code": "ESP", "level": 1, "logo": "https://example.com/logo/laliga.png"},
        {"name": "Serie A", "short_name": "SA", "country_code": "ITA", "level": 1, "logo": "https://example.com/logo/seriea.png"},
        {"name": "Bundesliga", "short_name": "BL", "country_code": "GER", "level": 1, "logo": "https://example.com/logo/bundesliga.png"},
        {"name": "Ligue 1", "short_name": "L1", "country_code": "FRA", "level": 1, "logo": "https://example.com/logo/ligue1.png"}
    ]
    
    league_objs = {}
    for league_data in leagues_data:
        country = next((c for c in countries if c.code == league_data['country_code']), None)
        if not country:
            continue
            
        league = League(
            name=league_data['name'],
            short_name=league_data['short_name'],
            country_id=country.id,
            level=league_data['level'],
            logo=league_data['logo'],
            current_season="2024/2025"
        )
        db.session.add(league)
        league_objs[league_data['short_name']] = league
    
    db.session.commit()
    return league_objs

def create_teams(leagues):
    """Takımları oluştur ve maç programını hazırla"""
    teams_data = [
        # Süper Lig takımları
        {"name": "Galatasaray", "short_name": "GAL", "founded": 1905, "stadium": "RAMS Park", 
         "logo": "https://example.com/logos/galatasaray.png", "league_short": "SL",
         "attack_rating": 85, "defense_rating": 82, "home_advantage": 1.2, "current_form": 82},
        {"name": "Fenerbahçe", "short_name": "FB", "founded": 1907, "stadium": "Ülker Stadyumu",
         "logo": "https://example.com/logos/fenerbahce.png", "league_short": "SL",
         "attack_rating": 84, "defense_rating": 80, "home_advantage": 1.18, "current_form": 85},
        {"name": "Beşiktaş", "short_name": "BJK", "founded": 1903, "stadium": "Vodafone Park",
         "logo": "https://example.com/logos/besiktas.png", "league_short": "SL",
         "attack_rating": 82, "defense_rating": 78, "home_advantage": 1.15, "current_form": 78},
        {"name": "Trabzonspor", "short_name": "TS", "founded": 1967, "stadium": "Medical Park Stadyumu",
         "logo": "https://example.com/logos/trabzonspor.png", "league_short": "SL",
         "attack_rating": 78, "defense_rating": 75, "home_advantage": 1.25, "current_form": 74},
        
        # Premier Lig takımları
        {"name": "Manchester City", "short_name": "MCI", "founded": 1880, "stadium": "Etihad Stadyumu",
         "logo": "https://example.com/logos/mancity.png", "league_short": "EPL",
         "attack_rating": 92, "defense_rating": 88, "home_advantage": 1.15, "current_form": 90},
        {"name": "Liverpool", "short_name": "LIV", "founded": 1892, "stadium": "Anfield",
         "logo": "https://example.com/logos/liverpool.png", "league_short": "EPL",
         "attack_rating": 90, "defense_rating": 86, "home_advantage": 1.2, "current_form": 88},
        {"name": "Arsenal", "short_name": "ARS", "founded": 1886, "stadium": "Emirates Stadyumu",
         "logo": "https://example.com/logos/arsenal.png", "league_short": "EPL",
         "attack_rating": 89, "defense_rating": 85, "home_advantage": 1.18, "current_form": 87},
         
        # La Liga takımları
        {"name": "Real Madrid", "short_name": "RMA", "founded": 1902, "stadium": "Santiago Bernabéu",
         "logo": "https://example.com/logos/realmadrid.png", "league_short": "LL",
         "attack_rating": 91, "defense_rating": 87, "home_advantage": 1.2, "current_form": 89},
        {"name": "Barcelona", "short_name": "FCB", "founded": 1899, "stadium": "Spotify Camp Nou",
         "logo": "https://example.com/logos/barcelona.png", "league_short": "LL",
         "attack_rating": 90, "defense_rating": 85, "home_advantage": 1.22, "current_form": 88}
    ]
    
    # Takımları oluştur
    team_objs = {}
    for team_data in teams_data:
        league = leagues.get(team_data['league_short'])
        if not league:
            continue
            
        team = Team(
            name=team_data['name'],
            short_name=team_data['short_name'],
            founded=team_data['founded'],
            stadium=team_data['stadium'],
            logo=team_data['logo'],
            country_id=league.country_id,
            league_id=league.id,
            attack_rating=team_data['attack_rating'],
            defense_rating=team_data['defense_rating'],
            home_advantage=team_data['home_advantage'],
            current_form=team_data['current_form']
        )
        db.session.add(team)
        team_objs[team.short_name] = team
    
    db.session.commit()
    print(f"Created {len(teams)} teams")
    
    print("Skipping player and injury report creation as models are not available")
    players = []
    
    # Create historical matches
    current_date = datetime.utcnow()
    season_start = current_date - timedelta(days=120)  # Season started 4 months ago
    
    # Create round-robin matches (each team plays others)
    match_count = 0
    for i, home_team in enumerate(teams):
        for j, away_team in enumerate(teams):
            if i != j:  # Teams don't play against themselves
                # Create match date (random within season)
                match_date = season_start + timedelta(days=random.randint(0, 100))
                
                # 80% of matches are already played
                played = random.random() < 0.8
                
                # Maç durumunu belirle
                durum = 'Finished' if played else 'Scheduled'
                
                match = Match(
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    match_date=match_date,
                    competition='Süper Lig',
                    season='2024-25',
                    status=durum,
                    matchday=random.randint(1, 34)  # 1-34 hafta arası rastgele maç günü
                )
                
                if played:
                    # Gerçekçi maç istatistikleri oluştur
                    home_strength = (home_team.attack_rating + home_team.defense_rating) / 2
                    away_strength = (away_team.attack_rating + away_team.defense_rating) / 2
                    
                    # Ev sahibi avantajı
                    home_strength *= home_team.home_advantage
                    
                    # Takım gücüne göre skor oluştur
                    home_expected = (home_strength / 100) * 2.5
                    away_expected = (away_strength / 100) * 2.5
                    
                    # Rastgelelik ekle
                    home_goals = max(0, int(random.gauss(home_expected, 1)))
                    away_goals = max(0, int(random.gauss(away_expected, 1)))
                    
                    # Skorları sınırla (en fazla 6 gol)
                    match.home_goals = min(6, home_goals)
                    match.away_goals = min(6, away_goals)
                    
                    # İlk yarı skorları
                    match.home_ht_goals = random.randint(0, match.home_goals)
                    match.away_ht_goals = random.randint(0, match.away_goals)
                    
                    # Maç istatistikleri
                    toplam_gol = match.home_goals + match.away_goals
                    match.home_shots = random.randint(5, 25)
                    match.away_shots = random.randint(5, 25)
                    match.home_shots_on_target = random.randint(1, match.home_goals + 5)
                    match.away_shots_on_target = random.randint(1, match.away_goals + 5)
                    
                    # Top hakimiyeti (ev sahibi avantajıyla birlikte)
                    temel_hakimiyet = random.randint(40, 60)
                    ev_avantaji = random.randint(0, 15)
                    match.home_possession = min(80, temel_hakimiyet + ev_avantaji)
                    match.away_possession = 100 - match.home_possession
                    
                    # Diğer istatistikler
                    match.home_fouls = random.randint(5, 25)
                    match.away_fouls = random.randint(5, 25)
                    match.home_yellows = random.randint(0, 5)
                    match.away_yellows = random.randint(0, 5)
                    match.home_reds = 1 if random.random() > 0.9 else 0  # %10 kırmızı kart şansı
                    match.away_reds = 1 if random.random() > 0.9 else 0
                    match.home_corners = random.randint(0, 12)
                    match.away_corners = random.randint(0, 12)
                    match.home_offsides = random.randint(0, 5)
                    match.away_offsides = random.randint(0, 5)
                
                db.session.add(match)
                match_count += 1
                
                # Limit total matches to avoid too much data
                if match_count >= 100:
                    break
        
        if match_count >= 100:
            break
    
    db.session.commit()
    print(f"Created {Match.query.count()} matches")
    
    print("Sample data initialization completed!")

def reset_database():
    """Veritabanını sıfırla (geliştirme amaçlı)"""
    print("Veritabanı sıfırlanıyor...")
    
    # Tüm tabloları sil ve yeniden oluştur
    db.drop_all()
    db.create_all()
    print("Veritabanı tabloları oluşturuldu")
    
    # Ülkeleri oluştur
    print("Ülkeler oluşturuluyor...")
    countries = create_countries()
    print(f"{len(countries)} ülke oluşturuldu")
    
    # Ligleri oluştur
    print("Ligler oluşturuluyor...")
    leagues = create_leagues(countries)
    print(f"{len(leagues)} lig oluşturuldu")
    
    # Takımları oluştur (bu fonksiyon aynı zamanda maçları da oluşturur)
    print("Takımlar ve maçlar oluşturuluyor...")
    teams = create_teams(leagues)
    print(f"{len(teams)} takım oluşturuldu")
    
    # Değişiklikleri kaydet
    db.session.commit()
    print("Veritabanı başarıyla sıfırlandı")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        reset_database()
