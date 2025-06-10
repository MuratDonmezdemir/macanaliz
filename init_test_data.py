from app import create_app, db
from app.models import Team, Match, Prediction, TeamStatistics, BaseModel, User
from datetime import datetime, timedelta
import random

def create_test_data():
    app = create_app()
    app.app_context().push()
    
    # Veritabanını temizle
    db.drop_all()
    db.create_all()
    
    print("Veritabanı tabloları oluşturuldu.")
    
    # Test kullanıcıları oluştur
    users = [
        User(username='admin', email='admin@example.com', is_admin=True),
        User(username='user1', email='user1@example.com'),
        User(username='user2', email='user2@example.com')
    ]
    
    for user in users:
        user.set_password('password123')
        db.session.add(user)
    
    # Test takımları oluştur
    teams = [
        Team(name='Galatasaray', short_name='GS', country='Türkiye', founded=1905),
        Team(name='Fenerbahçe', short_name='FB', country='Türkiye', founded=1907),
        Team(name='Beşiktaş', short_name='BJK', country='Türkiye', founded=1903),
        Team(name='Trabzonspor', short_name='TS', country='Türkiye', founded=1967)
    ]
    
    for team in teams:
        db.session.add(team)
    
    db.session.commit()
    print(f"{len(teams)} takım oluşturuldu.")
    
    # Test maçları oluştur
    matches = []
    today = datetime.utcnow()
    
    for i in range(10):
        home_team = random.choice(teams)
        away_team = random.choice([t for t in teams if t.id != home_team.id])
        
        match = Match(
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            match_date=today + timedelta(days=i),
            status='SCHEDULED',
            home_goals=0,
            away_goals=0
        )
        matches.append(match)
        db.session.add(match)
    
    db.session.commit()
    print(f"{len(matches)} maç oluşturuldu.")
    
    # Test tahminleri oluştur
    for match in matches:
        for user in users:
            prediction = Prediction(
                match_id=match.id,
                user_id=user.id,
                home_goals=random.randint(0, 3),
                away_goals=random.randint(0, 3),
                home_win_prob=random.uniform(0.2, 0.8),
                draw_prob=random.uniform(0.1, 0.3),
                away_win_prob=random.uniform(0.1, 0.5),
                over_2_5_prob=random.uniform(0.3, 0.7),
                btts_prob=random.uniform(0.3, 0.7),
                model_version='1.0',
                confidence=random.uniform(0.6, 0.95)
            )
            db.session.add(prediction)
    
    db.session.commit()
    print(f"Tahminler oluşturuldu.")
    
    print("Test verileri başarıyla oluşturuldu!")
    away_win_prob = db.Column(db.Float, nullable=False)  # Deplasman kazanma olasılığı
    over_2_5_prob = db.Column(db.Float, nullable=False)  # 2.5 üstü gol olasılığı
    btts_prob = db.Column(db.Float, nullable=False)      # İki takımın da gol atma olasılığı
    model_version = db.Column(db.String(50), nullable=False)  # Kullanılan model versiyonu
    confidence = db.Column(db.Float)  # Modelin bu tahmindeki güveni
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # İlişkiler
    match = db.relationship('Match', back_populates='predictions')
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        print("Creating test data...")
        
        # Create teams
        teams = []
        team_names = [
            "Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor",
            "Başakşehir", "Adana Demirspor", "Konyaspor", "Alanyaspor",
            "Sivasspor", "Kayserispor", "Gaziantep FK", "Antalyaspor",
            "Kasımpaşa", "Hatayspor", "Giresunspor", "Ümraniyespor",
            "Ankaragücü", "İstanbulspor", "Göztepe", "Altay"
        ]
        
        for name in team_names:
            team = Team(name=name, short_name=name[:3].upper())
            teams.append(team)
            db.session.add(team)
        
        db.session.commit()
        print(f"Created {len(teams)} teams")
        
        # Create matches for the last 2 years
        today = datetime.now()
        start_date = today - timedelta(days=730)  # 2 years ago
        
        matches = []
        match_date = start_date
        match_id = 1
        
        # Create matches for each week
        while match_date < today + timedelta(days=30):  # Include next month
            # Skip if it's not a weekend (Saturday or Sunday)
            if match_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                # Create matches between teams
                for i in range(0, len(teams), 2):
                    if i+1 < len(teams):
                        home_team = teams[i]
                        away_team = teams[i+1]
                        
                        # Determine match status and scores
                        if match_date > today:
                            status = 'Scheduled'
                            home_goals = None
                            away_goals = None
                        else:
                            status = 'Finished'
                            home_goals = random.randint(0, 4)
                            away_goals = random.randint(0, 3)
                        
                        match = Match(
                            home_team_id=home_team.id,
                            away_team_id=away_team.id,
                            match_date=match_date,
                            competition="Süper Lig",
                            season=f"{match_date.year}/{match_date.year+1}",
                            home_goals=home_goals,
                            away_goals=away_goals,
                            home_shots=random.randint(8, 20),
                            away_shots=random.randint(6, 18),
                            home_shots_on_target=random.randint(2, 10),
                            away_shots_on_target=random.randint(1, 8),
                            home_possession=random.uniform(40, 70),
                            away_possession=100 - random.uniform(40, 70),
                            home_corners=random.randint(2, 10),
                            away_corners=random.randint(1, 8),
                            home_fouls=random.randint(8, 20),
                            away_fouls=random.randint(8, 20),
                            home_yellows=random.randint(0, 4),
                            away_yellows=random.randint(0, 4),
                            home_reds=random.randint(0, 1),
                            away_reds=random.randint(0, 1),
                            home_offsides=random.randint(0, 5),
                            away_offsides=random.randint(0, 5),
                            status=status
                        )
                        
                        # Add half-time scores for finished matches
                        if status == 'Finished':
                            match.home_ht_goals = random.randint(0, min(3, home_goals))
                            match.away_ht_goals = random.randint(0, min(2, away_goals))
                        
                        matches.append(match)
                        db.session.add(match)
                        
                        # Add prediction for the match
                        if match_date > today - timedelta(days=7):  # Only predict recent and future matches
                            prediction = Prediction(
                                match_id=match.id,
                                home_goals=round(random.uniform(0.5, 3.5), 1),
                                away_goals=round(random.uniform(0.5, 2.5), 1),
                                home_win=random.uniform(0.3, 0.7),
                                draw=random.uniform(0.1, 0.4),
                                away_win=random.uniform(0.1, 0.5),
                                home_ht_goals=round(random.uniform(0.2, 2.0), 1),
                                away_ht_goals=round(random.uniform(0.1, 1.5), 1),
                                ht_home_win=random.uniform(0.2, 0.6),
                                ht_draw=random.uniform(0.2, 0.5),
                                ht_away_win=random.uniform(0.1, 0.4),
                                most_likely_score=f"{random.randint(1,3)}-{random.randint(0,2)}",
                                score_probability=random.uniform(0.05, 0.15),
                                over_05=random.uniform(0.7, 0.95),
                                over_15=random.uniform(0.4, 0.8),
                                over_25=random.uniform(0.2, 0.6),
                                btts_yes=random.uniform(0.3, 0.7),
                                algorithm="random_forest",
                                model_version="1.0",
                                confidence=random.uniform(0.6, 0.9)
                            )
                            db.session.add(prediction)
            
            # Move to next week
            match_date += timedelta(days=7)
        
        db.session.commit()
        print(f"Created {len(matches)} matches")
        
        # Create team statistics
        for team in teams:
            stats = TeamStatistics(
                team_id=team.id,
                season="2023/2024",
                matches_played=random.randint(10, 34),
                wins=random.randint(3, 25),
                draws=random.randint(3, 15),
                losses=random.randint(0, 10),
                goals_for=random.randint(15, 70),
                goals_against=random.randint(10, 40),
                clean_sheets=random.randint(3, 15),
                failed_to_score=random.randint(2, 10),
                avg_possession=random.uniform(40, 65),
                shots_per_game=random.uniform(8, 18),
                shots_on_target_per_game=random.uniform(3, 8),
                pass_accuracy=random.uniform(70, 90),
                aerials_won=random.uniform(10, 25),
                tackles_per_game=random.uniform(10, 25),
                interceptions_per_game=random.uniform(8, 20),
                fouls_per_game=random.uniform(8, 20),
                corners_per_game=random.uniform(3, 8)
            )
            db.session.add(stats)
        
        db.session.commit()
        print("Created team statistics")
        
        print("\nTest data created successfully!")
        print(f"Total teams: {Team.query.count()}")
        print(f"Total matches: {Match.query.count()}")
        print(f"Total predictions: {Prediction.query.count()}")
        print(f"Total team statistics: {TeamStatistics.query.count()}")

if __name__ == "__main__":
    create_test_data()
