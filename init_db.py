from app import app
from models import db, Team, Match, Prediction
from datetime import datetime, timedelta

def init_db():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Add sample teams
        teams = [
            Team(name="Galatasaray", short_name="GS", country="Türkiye", founded=1905, stadium="Rams Park"),
            Team(name="Fenerbahçe", short_name="FB", country="Türkiye", founded=1907, stadium="Ülker Stadyumu"),
            Team(name="Beşiktaş", short_name="BJK", country="Türkiye", founded=1903, stadium="Vodafone Park"),
            Team(name="Trabzonspor", short_name="TS", country="Türkiye", founded=1967, stadium="Şenol Güneş Stadyumu"),
        ]
        
        for team in teams:
            db.session.add(team)
        
        db.session.commit()
        
        # Add sample matches
        now = datetime.now()
        matches = [
            Match(
                home_team_id=1,  # Galatasaray
                away_team_id=2,  # Fenerbahçe
                match_date=now + timedelta(days=7),
                competition="Süper Lig",
                status="Scheduled"
            ),
            Match(
                home_team_id=3,  # Beşiktaş
                away_team_id=4,  # Trabzonspor
                match_date=now + timedelta(days=8),
                competition="Süper Lig",
                status="Scheduled"
            ),
        ]
        
        for match in matches:
            db.session.add(match)
        
        db.session.commit()
        
        print("Veritabanı başarıyla oluşturuldu ve örnek veriler eklendi!")

if __name__ == '__main__':
    init_db()
