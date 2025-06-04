from app import db
from models import Team, Match, Prediction
from datetime import datetime, timedelta
import random

def initialize_sample_data():
    """Initialize the database with sample football data"""
    
    # Check if data already exists
    if Team.query.count() > 0:
        return
    
    print("Initializing sample football data...")
    
    # Turkish Süper Lig teams
    teams_data = [
        {"name": "Galatasaray", "league": "Süper Lig", "city": "İstanbul", "country": "Turkey", 
         "founded": 1905, "stadium": "Türk Telekom Stadyumu", "attack_rating": 85, "defense_rating": 78, "home_advantage": 1.2, "current_form": 82},
        {"name": "Fenerbahçe", "league": "Süper Lig", "city": "İstanbul", "country": "Turkey", 
         "founded": 1907, "stadium": "Ülker Stadyumu", "attack_rating": 83, "defense_rating": 75, "home_advantage": 1.15, "current_form": 79},
        {"name": "Beşiktaş", "league": "Süper Lig", "city": "İstanbul", "country": "Turkey", 
         "founded": 1903, "stadium": "Vodafone Park", "attack_rating": 80, "defense_rating": 76, "home_advantage": 1.18, "current_form": 74},
        {"name": "Trabzonspor", "league": "Süper Lig", "city": "Trabzon", "country": "Turkey", 
         "founded": 1967, "stadium": "Medical Park Stadyumu", "attack_rating": 77, "defense_rating": 72, "home_advantage": 1.25, "current_form": 76},
        {"name": "Başakşehir", "league": "Süper Lig", "city": "İstanbul", "country": "Turkey", 
         "founded": 1990, "stadium": "Başakşehir Fatih Terim Stadyumu", "attack_rating": 74, "defense_rating": 80, "home_advantage": 1.1, "current_form": 68},
        {"name": "Konyaspor", "league": "Süper Lig", "city": "Konya", "country": "Turkey", 
         "founded": 1922, "stadium": "Konya Büyükşehir Stadyumu", "attack_rating": 65, "defense_rating": 70, "home_advantage": 1.15, "current_form": 61},
        {"name": "Antalyaspor", "league": "Süper Lig", "city": "Antalya", "country": "Turkey", 
         "founded": 1966, "stadium": "Antalya Stadyumu", "attack_rating": 68, "defense_rating": 65, "home_advantage": 1.12, "current_form": 58},
        {"name": "Alanyaspor", "league": "Süper Lig", "city": "Alanya", "country": "Turkey", 
         "founded": 1948, "stadium": "Bahçeşehir Okulları Stadyumu", "attack_rating": 70, "defense_rating": 68, "home_advantage": 1.08, "current_form": 62},
        {"name": "Kasımpaşa", "league": "Süper Lig", "city": "İstanbul", "country": "Turkey", 
         "founded": 1921, "stadium": "Recep Tayyip Erdoğan Stadyumu", "attack_rating": 66, "defense_rating": 64, "home_advantage": 1.05, "current_form": 55},
        {"name": "Sivasspor", "league": "Süper Lig", "city": "Sivas", "country": "Turkey", 
         "founded": 1967, "stadium": "Yeni 4 Eylül Stadyumu", "attack_rating": 63, "defense_rating": 69, "home_advantage": 1.14, "current_form": 57},
        {"name": "Gaziantep FK", "league": "Süper Lig", "city": "Gaziantep", "country": "Turkey", 
         "founded": 1988, "stadium": "Gaziantep Stadyumu", "attack_rating": 62, "defense_rating": 66, "home_advantage": 1.13, "current_form": 54},
        {"name": "Kayserispor", "league": "Süper Lig", "city": "Kayseri", "country": "Turkey", 
         "founded": 1966, "stadium": "RHG Enertürk Enerji Stadyumu", "attack_rating": 60, "defense_rating": 63, "home_advantage": 1.11, "current_form": 52}
    ]
    
    # Create teams
    teams = []
    for team_data in teams_data:
        team = Team(
            name=team_data['name'],
            short_name=team_data['name'][:3].upper(),
            country=team_data['country'],
            founded=team_data['founded'],
            stadium=team_data['stadium']
        )
        db.session.add(team)
        teams.append(team)
    
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
                
                match = Match(
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    match_date=match_date,
                    league='Süper Lig',
                    season='2024-25',
                    played=played
                )
                
                if played:
                    # Generate realistic match statistics
                    home_strength = (home_team.attack_rating + home_team.defense_rating) / 2
                    away_strength = (away_team.attack_rating + away_team.defense_rating) / 2
                    
                    # Home advantage
                    home_strength *= home_team.home_advantage
                    
                    # Generate scores based on team strength
                    home_expected = (home_strength / 100) * 2.5
                    away_expected = (away_strength / 100) * 2.5
                    
                    # Add randomness
                    home_score = max(0, int(random.gauss(home_expected, 1)))
                    away_score = max(0, int(random.gauss(away_expected, 1)))
                    
                    match.home_score = min(6, home_score)  # Cap at 6 goals
                    match.away_score = min(6, away_score)
                    
                    # Half-time scores
                    match.home_half_time_score = random.randint(0, match.home_score)
                    match.away_half_time_score = random.randint(0, match.away_score)
                    
                    # Match statistics
                    match.home_shots = random.randint(8, 25)
                    match.away_shots = random.randint(8, 25)
                    match.home_shots_on_target = random.randint(2, match.home_shots)
                    match.away_shots_on_target = random.randint(2, match.away_shots)
                    match.home_possession = random.randint(30, 70)
                    match.away_possession = 100 - match.home_possession
                    match.home_fouls = random.randint(5, 20)
                    match.away_fouls = random.randint(5, 20)
                    match.home_corners = random.randint(2, 12)
                    match.away_corners = random.randint(2, 12)
                    
                    # Weather and attendance
                    match.weather_condition = random.choice(['Sunny', 'Cloudy', 'Rainy', 'Clear'])
                    match.temperature = random.randint(5, 35)
                    match.attendance = random.randint(15000, 52000)
                
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
    """Reset the database (for development purposes)"""
    print("Resetting database...")
    db.drop_all()
    db.create_all()
    initialize_sample_data()
    print("Database reset completed!")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        reset_database()
