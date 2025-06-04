from app import db
from models import Team, Player, Match, InjuryReport, Prediction
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
        team = Team(**team_data)
        db.session.add(team)
        teams.append(team)
    
    db.session.commit()
    print(f"Created {len(teams)} teams")
    
    # Create players for each team
    positions = ['GK', 'CB', 'CB', 'LB', 'RB', 'CDM', 'CM', 'CAM', 'LW', 'RW', 'ST']
    turkish_names = [
        "Ahmet Yılmaz", "Mehmet Kaya", "Mustafa Demir", "Ali Çelik", "Hasan Şahin",
        "Hüseyin Yıldız", "İbrahim Özkan", "Osman Arslan", "Emre Doğan", "Burak Koç",
        "Serkan Aydın", "Tolga Polat", "Kemal Erdoğan", "Fatih Çakır", "Onur Güneş",
        "Selçuk Bulut", "Gökhan Aslan", "Volkan Kurt", "Eren Özdemir", "Can Aktaş"
    ]
    
    for team in teams:
        for i, position in enumerate(positions):
            player = Player(
                name=f"{random.choice(turkish_names)} {i+1}",
                position=position,
                age=random.randint(18, 35),
                team_id=team.id,
                skill_rating=random.randint(50, 95),
                games_played=random.randint(0, 30),
                goals_scored=random.randint(0, 15) if position in ['ST', 'CAM', 'LW', 'RW'] else random.randint(0, 5),
                assists=random.randint(0, 10) if position not in ['GK', 'CB'] else random.randint(0, 2)
            )
            db.session.add(player)
    
    db.session.commit()
    print(f"Created {Player.query.count()} players")
    
    # Create some injury reports
    players = Player.query.all()
    injury_types = ["Hamstring", "Ankle", "Knee", "Muscle", "Groin", "Back", "Shoulder"]
    
    for _ in range(15):  # Create 15 random injuries
        player = random.choice(players)
        injury = InjuryReport(
            player_id=player.id,
            injury_type=random.choice(injury_types),
            severity=random.randint(1, 8),
            injury_date=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            expected_return_date=datetime.utcnow() + timedelta(days=random.randint(1, 60)),
            status='injured'
        )
        db.session.add(injury)
        
        # Update player injury status
        player.injury_status = True
        player.injury_severity = injury.severity
    
    db.session.commit()
    print(f"Created {InjuryReport.query.count()} injury reports")
    
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
