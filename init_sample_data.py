from datetime import datetime, timedelta

from flask_migrate import upgrade

from app import create_app, dbpython -m pip install --upgrade pip
pip install -r requirements.txtpython -m venv venv
.\venv\Scripts\activatepython -m venv venv
.\venv\Scripts\activate
from app.models.country import Country
from app.models.league import League
from app.models.team import Team
from app.models.match import Match
from app.models.prediction import Prediction
from app.models.team_statistics import TeamStatistics

def create_sample_data():
    app = create_app()
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create countries
        turkey = Country(name='Turkey', code='TUR', flag='🇹🇷')
        england = Country(name='England', code='ENG', flag='🏴󠁧󠁢󠁥󠁮󠁧󠁿')
        spain = Country(name='Spain', code='ESP', flag='🇪🇸')
        
        db.session.add_all([turkey, england, spain])
        db.session.commit()
        
        # Create leagues
        super_lig = League(
            name='Süper Lig',
            short_name='SL',
            country_id=turkey.id,
            level=1,
            current_season='2024-2025'
        )
        
        premier_league = League(
            name='Premier League',
            short_name='EPL',
            country_id=england.id,
            level=1,
            current_season='2024-2025'
        )
        
        laliga = League(
            name='La Liga',
            short_name='LL',
            country_id=spain.id,
            level=1,
            current_season='2024-2025'
        )
        
        db.session.add_all([super_lig, premier_league, laliga])
        db.session.commit()
        
        # Create teams
        teams_data = [
            # Turkish teams
            ('Galatasaray', 'GAL', turkey.id, super_lig.id, 1905, 'Nef Stadyumu', 65, 60, 1.2, 70),
            ('Fenerbahçe', 'FNB', turkey.id, super_lig.id, 1907, 'Ülker Stadyumu', 70, 55, 1.1, 65),
            ('Beşiktaş', 'BJK', turkey.id, super_lig.id, 1903, 'Vodafone Park', 68, 58, 1.15, 68),
            
            # English teams
            ('Manchester City', 'MCI', england.id, premier_league.id, 1880, 'Etihad Stadium', 80, 75, 1.1, 85),
            ('Liverpool', 'LIV', england.id, premier_league.id, 1892, 'Anfield', 78, 72, 1.2, 82),
            ('Chelsea', 'CHE', england.id, premier_league.id, 1905, 'Stamford Bridge', 75, 70, 1.15, 78),
            
            # Spanish teams
            ('Barcelona', 'BAR', spain.id, laliga.id, 1899, 'Camp Nou', 82, 75, 1.1, 88),
            ('Real Madrid', 'RMA', spain.id, laliga.id, 1902, 'Santiago Bernabéu', 85, 78, 1.15, 90),
            ('Atletico Madrid', 'ATM', spain.id, laliga.id, 1903, 'Wanda Metropolitano', 75, 80, 1.2, 85)
        ]
        
        teams = []
        for name, short_name, country_id, league_id, founded, stadium, attack, defense, home_adv, form in teams_data:
            team = Team(
                name=name,
                short_name=short_name,
                country_id=country_id,
                league_id=league_id,
                founded=founded,
                stadium=stadium,
                attack_rating=attack,
                defense_rating=defense,
                home_advantage=home_adv,
                current_form=form
            )
            teams.append(team)
        
        db.session.add_all(teams)
        db.session.commit()
        
        # Create some upcoming matches
        today = datetime.utcnow()
        matches = []
        
        # Turkish league matches
        matches.append(Match(
            home_team_id=teams[0].id,  # Galatasaray
            away_team_id=teams[1].id,  # Fenerbahçe
            match_date=today + timedelta(days=2),
            season='2024-2025',
            matchday=1,
            status='Scheduled',
            league_id=super_lig.id
        ))
        
        matches.append(Match(
            home_team_id=teams[2].id,  # Beşiktaş
            away_team_id=teams[0].id,  # Galatasaray
            match_date=today + timedelta(days=9),
            season='2024-2025',
            matchday=2,
            status='Scheduled',
            league_id=super_lig.id
        ))
        
        # English Premier League matches
        matches.append(Match(
            home_team_id=teams[3].id,  # Man City
            away_team_id=teams[4].id,  # Liverpool
            match_date=today + timedelta(days=3),
            season='2024-2025',
            matchday=1,
            status='Scheduled',
            league_id=premier_league.id
        ))
        
        # Spanish La Liga matches
        matches.append(Match(
            home_team_id=teams[6].id,  # Barcelona
            away_team_id=teams[7].id,  # Real Madrid
            match_date=today + timedelta(days=4),
            season='2024-2025',
            matchday=1,
            status='Scheduled',
            league_id=laliga.id
        ))
        
        db.session.add_all(matches)
        db.session.commit()
        
        print("Sample data has been created successfully!")

if __name__ == '__main__':
    create_sample_data()
