from app import create_app, db
from app.models import Team, Match, PlayerStatistics, League, Season, Standing
from datetime import datetime, timedelta
import random

app = create_app('development')

def init_db():
    with app.app_context():
        # Tüm tabloları sil
        db.drop_all()
        
        # Tüm tabloları oluştur
        db.create_all()
        
        # Örnek lig ekle
        league = League(
            name="Süper Lig",
            country="Türkiye",
            season="2023-2024",
            is_active=True
        )
        db.session.add(league)
        
        # Örnek sezon ekle
        season = Season(
            name="2023-2024",
            start_date=datetime(2023, 8, 1).date(),
            end_date=datetime(2024, 5, 31).date(),
            is_current=True,
            league=league
        )
        db.session.add(season)
        
        # Örnek takımlar ekle
        teams = [
            Team(name="Galatasaray", short_name="GS", country="Türkiye", founded=1905, stadium_id=1),
            Team(name="Fenerbahçe", short_name="FB", country="Türkiye", founded=1907, stadium_id=2),
            Team(name="Beşiktaş", short_name="BJK", country="Türkiye", founded=1903, stadium_id=3),
            Team(name="Trabzonspor", short_name="TS", country="Türkiye", founded=1967, stadium_id=4),
        ]
        
        for team in teams:
            db.session.add(team)
        
        db.session.commit()
        
        # Örnek maçlar ekle
        now = datetime.now()
        matches = [
            Match(
                home_team_id=1,  # Galatasaray
                away_team_id=2,  # Fenerbahçe
                match_date=now + timedelta(days=7),
                status='SCHEDULED',
                season_id=season.id
            ),
            Match(
                home_team_id=3,  # Beşiktaş
                away_team_id=4,  # Trabzonspor
                match_date=now + timedelta(days=8),
                status='SCHEDULED',
                season_id=season.id
            ),
        ]
        
        for match in matches:
            db.session.add(match)
        
        db.session.commit()
        
        # Örnek oyuncu istatistikleri ekle
        players = ["Arda Güler", "Hakan Çalhanoğlu", "Cengiz Ünder", "Cenk Tosun"]
        
        for i, player_name in enumerate(players, 1):
            stats = PlayerStatistics(
                player_name=player_name,
                team_id=(i % 4) + 1,  # 1-4 arası takım ID'leri
                match_id=1 if i % 2 == 0 else 2,
                season_id=season.id,
                position='MID' if i % 2 == 0 else 'FWD',
                minutes_played=random.randint(60, 90),
                goals=random.randint(0, 2),
                assists=random.randint(0, 2),
                shots=random.randint(1, 5),
                shots_on_target=random.randint(0, 3),
                passes=random.randint(20, 50),
                pass_accuracy=random.uniform(70.0, 90.0),
                tackles=random.randint(0, 5),
                rating=random.uniform(6.0, 9.5),
                is_motm=random.choice([True, False])
            )
            db.session.add(stats)
        
        db.session.commit()
        
        print("Veritabanı başarıyla oluşturuldu ve örnek veriler eklendi!")

if __name__ == '__main__':
    init_db()