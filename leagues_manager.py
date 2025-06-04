from models import Team, Match, Player
from app import db
import requests
import os

class LeaguesManager:
    """Manage multiple leagues and competitions worldwide"""
    
    def __init__(self):
        self.api_key = os.environ.get('FOOTBALL_API_KEY')
        self.base_url = "https://api.football-data.org/v4"
        self.headers = {
            'X-Auth-Token': self.api_key
        } if self.api_key else {}
        
        # Major world leagues
        self.supported_leagues = {
            'Premier League': {
                'code': 'PL',
                'country': 'England',
                'api_id': 2021,
                'season': '2024-25'
            },
            'La Liga': {
                'code': 'PD',
                'country': 'Spain', 
                'api_id': 2014,
                'season': '2024-25'
            },
            'Bundesliga': {
                'code': 'BL1',
                'country': 'Germany',
                'api_id': 2002,
                'season': '2024-25'
            },
            'Serie A': {
                'code': 'SA',
                'country': 'Italy',
                'api_id': 2019,
                'season': '2024-25'
            },
            'Ligue 1': {
                'code': 'FL1',
                'country': 'France',
                'api_id': 2015,
                'season': '2024-25'
            },
            'Süper Lig': {
                'code': 'TR1',
                'country': 'Turkey',
                'api_id': 2017,
                'season': '2024-25'
            },
            'Eredivisie': {
                'code': 'DED',
                'country': 'Netherlands',
                'api_id': 2003,
                'season': '2024-25'
            },
            'Primeira Liga': {
                'code': 'PPL',
                'country': 'Portugal',
                'api_id': 2017,
                'season': '2024-25'
            },
            'Champions League': {
                'code': 'CL',
                'country': 'Europe',
                'api_id': 2001,
                'season': '2024-25'
            },
            'Europa League': {
                'code': 'EL',
                'country': 'Europe',
                'api_id': 2018,
                'season': '2024-25'
            }
        }
    
    def get_all_leagues(self):
        """Get all supported leagues"""
        return list(self.supported_leagues.keys())
    
    def get_league_teams(self, league_name):
        """Get teams from a specific league"""
        if league_name not in self.supported_leagues:
            return self._get_sample_teams_for_league(league_name)
        
        if not self.api_key:
            return self._get_sample_teams_for_league(league_name)
        
        league_info = self.supported_leagues[league_name]
        
        try:
            # Get teams from specific league
            teams_url = f"{self.base_url}/competitions/{league_info['api_id']}/teams"
            response = requests.get(teams_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                teams_data = response.json()['teams']
                return self._process_league_teams(teams_data, league_name, league_info['country'])
            else:
                print(f"API Error for {league_name}: {response.status_code}")
                return self._get_sample_teams_for_league(league_name)
                
        except Exception as e:
            print(f"Exception getting {league_name} teams: {e}")
            return self._get_sample_teams_for_league(league_name)
    
    def _process_league_teams(self, teams_data, league_name, country):
        """Process API team data for a specific league"""
        processed_teams = []
        
        for team_data in teams_data:
            team_info = {
                'name': team_data.get('name', 'Unknown Team'),
                'country': country,
                'league': league_name,
                'founded': team_data.get('founded'),
                'stadium': team_data.get('venue', 'Unknown Stadium'),
                'attack_strength': self._calculate_league_attack_strength(league_name),
                'defense_strength': self._calculate_league_defense_strength(league_name),
                'home_advantage': self._calculate_league_home_advantage(league_name),
                'current_form': 50.0
            }
            processed_teams.append(team_info)
        
        return processed_teams
    
    def _calculate_league_attack_strength(self, league_name):
        """Calculate attack strength based on league quality"""
        import random
        
        league_quality = {
            'Premier League': (75, 95),
            'La Liga': (75, 95),
            'Bundesliga': (70, 90),
            'Serie A': (70, 90),
            'Ligue 1': (65, 85),
            'Süper Lig': (60, 80),
            'Eredivisie': (65, 80),
            'Primeira Liga': (60, 75),
            'Champions League': (80, 98),
            'Europa League': (70, 85)
        }
        
        min_val, max_val = league_quality.get(league_name, (50, 70))
        return random.randint(min_val, max_val)
    
    def _calculate_league_defense_strength(self, league_name):
        """Calculate defense strength based on league quality"""
        import random
        
        league_quality = {
            'Premier League': (70, 90),
            'La Liga': (70, 90),
            'Bundesliga': (65, 85),
            'Serie A': (75, 95),  # Italian teams known for defense
            'Ligue 1': (60, 80),
            'Süper Lig': (55, 75),
            'Eredivisie': (60, 75),
            'Primeira Liga': (55, 70),
            'Champions League': (75, 95),
            'Europa League': (65, 80)
        }
        
        min_val, max_val = league_quality.get(league_name, (45, 65))
        return random.randint(min_val, max_val)
    
    def _calculate_league_home_advantage(self, league_name):
        """Calculate home advantage based on league characteristics"""
        import random
        
        home_advantage = {
            'Premier League': (3, 8),
            'La Liga': (4, 10),
            'Bundesliga': (5, 12),  # Strong fan culture
            'Serie A': (4, 9),
            'Ligue 1': (3, 7),
            'Süper Lig': (6, 15),  # Very passionate fans
            'Eredivisie': (3, 8),
            'Primeira Liga': (4, 10),
            'Champions League': (2, 6),  # Neutral venues sometimes
            'Europa League': (3, 8)
        }
        
        min_val, max_val = home_advantage.get(league_name, (2, 6))
        return random.randint(min_val, max_val)
    
    def _get_sample_teams_for_league(self, league_name):
        """Get sample teams for each league"""
        sample_teams = {
            'Premier League': [
                {"name": "Manchester City", "country": "England", "league": "Premier League", "founded": 1880, "stadium": "Etihad Stadium", "attack_strength": 92, "defense_strength": 85, "home_advantage": 6, "current_form": 85},
                {"name": "Arsenal", "country": "England", "league": "Premier League", "founded": 1886, "stadium": "Emirates Stadium", "attack_strength": 88, "defense_strength": 80, "home_advantage": 7, "current_form": 82},
                {"name": "Liverpool", "country": "England", "league": "Premier League", "founded": 1892, "stadium": "Anfield", "attack_strength": 90, "defense_strength": 82, "home_advantage": 8, "current_form": 80},
                {"name": "Manchester United", "country": "England", "league": "Premier League", "founded": 1878, "stadium": "Old Trafford", "attack_strength": 85, "defense_strength": 75, "home_advantage": 7, "current_form": 75},
                {"name": "Chelsea", "country": "England", "league": "Premier League", "founded": 1905, "stadium": "Stamford Bridge", "attack_strength": 83, "defense_strength": 78, "home_advantage": 6, "current_form": 72}
            ],
            'La Liga': [
                {"name": "Real Madrid", "country": "Spain", "league": "La Liga", "founded": 1902, "stadium": "Santiago Bernabéu", "attack_strength": 95, "defense_strength": 88, "home_advantage": 8, "current_form": 88},
                {"name": "Barcelona", "country": "Spain", "league": "La Liga", "founded": 1899, "stadium": "Camp Nou", "attack_strength": 90, "defense_strength": 82, "home_advantage": 9, "current_form": 83},
                {"name": "Atlético Madrid", "country": "Spain", "league": "La Liga", "founded": 1903, "stadium": "Metropolitano", "attack_strength": 82, "defense_strength": 90, "home_advantage": 7, "current_form": 78},
                {"name": "Sevilla", "country": "Spain", "league": "La Liga", "founded": 1890, "stadium": "Ramón Sánchez Pizjuán", "attack_strength": 78, "defense_strength": 80, "home_advantage": 6, "current_form": 75},
                {"name": "Real Sociedad", "country": "Spain", "league": "La Liga", "founded": 1909, "stadium": "Anoeta", "attack_strength": 75, "defense_strength": 75, "home_advantage": 5, "current_form": 72}
            ],
            'Bundesliga': [
                {"name": "Bayern Munich", "country": "Germany", "league": "Bundesliga", "founded": 1900, "stadium": "Allianz Arena", "attack_strength": 93, "defense_strength": 85, "home_advantage": 8, "current_form": 87},
                {"name": "Borussia Dortmund", "country": "Germany", "league": "Bundesliga", "founded": 1909, "stadium": "Signal Iduna Park", "attack_strength": 85, "defense_strength": 78, "home_advantage": 12, "current_form": 80},
                {"name": "RB Leipzig", "country": "Germany", "league": "Bundesliga", "founded": 2009, "stadium": "Red Bull Arena", "attack_strength": 80, "defense_strength": 82, "home_advantage": 5, "current_form": 76},
                {"name": "Bayer Leverkusen", "country": "Germany", "league": "Bundesliga", "founded": 1904, "stadium": "BayArena", "attack_strength": 82, "defense_strength": 75, "home_advantage": 6, "current_form": 78},
                {"name": "Eintracht Frankfurt", "country": "Germany", "league": "Bundesliga", "founded": 1899, "stadium": "Deutsche Bank Park", "attack_strength": 75, "defense_strength": 72, "home_advantage": 8, "current_form": 73}
            ],
            'Serie A': [
                {"name": "Inter Milan", "country": "Italy", "league": "Serie A", "founded": 1908, "stadium": "San Siro", "attack_strength": 88, "defense_strength": 90, "home_advantage": 7, "current_form": 85},
                {"name": "Juventus", "country": "Italy", "league": "Serie A", "founded": 1897, "stadium": "Allianz Stadium", "attack_strength": 82, "defense_strength": 88, "home_advantage": 6, "current_form": 78},
                {"name": "AC Milan", "country": "Italy", "league": "Serie A", "founded": 1899, "stadium": "San Siro", "attack_strength": 85, "defense_strength": 85, "home_advantage": 8, "current_form": 80},
                {"name": "Napoli", "country": "Italy", "league": "Serie A", "founded": 1926, "stadium": "Diego Armando Maradona", "attack_strength": 87, "defense_strength": 82, "home_advantage": 9, "current_form": 82},
                {"name": "Roma", "country": "Italy", "league": "Serie A", "founded": 1927, "stadium": "Stadio Olimpico", "attack_strength": 78, "defense_strength": 80, "home_advantage": 7, "current_form": 75}
            ],
            'Süper Lig': [
                {"name": "Galatasaray", "country": "Turkey", "league": "Süper Lig", "founded": 1905, "stadium": "Türk Telekom Stadium", "attack_strength": 85, "defense_strength": 75, "home_advantage": 8, "current_form": 78},
                {"name": "Fenerbahçe", "country": "Turkey", "league": "Süper Lig", "founded": 1907, "stadium": "Şükrü Saracoğlu Stadium", "attack_strength": 82, "defense_strength": 77, "home_advantage": 7, "current_form": 75},
                {"name": "Beşiktaş", "country": "Turkey", "league": "Süper Lig", "founded": 1903, "stadium": "Vodafone Park", "attack_strength": 78, "defense_strength": 72, "home_advantage": 9, "current_form": 70},
                {"name": "Trabzonspor", "country": "Turkey", "league": "Süper Lig", "founded": 1967, "stadium": "Medical Park Stadium", "attack_strength": 75, "defense_strength": 74, "home_advantage": 10, "current_form": 72},
                {"name": "Başakşehir", "country": "Turkey", "league": "Süper Lig", "founded": 1990, "stadium": "Başakşehir Fatih Terim Stadium", "attack_strength": 70, "defense_strength": 75, "home_advantage": 5, "current_form": 68}
            ]
        }
        
        return sample_teams.get(league_name, [])
    
    def update_all_leagues(self):
        """Update teams from all supported leagues"""
        total_updated = 0
        
        for league_name in self.supported_leagues:
            print(f"Updating {league_name}...")
            teams_data = self.get_league_teams(league_name)
            
            for team_data in teams_data:
                existing_team = Team.query.filter_by(name=team_data['name']).first()
                
                if existing_team:
                    # Update existing team
                    existing_team.attack_strength = team_data['attack_strength']
                    existing_team.defense_strength = team_data['defense_strength']
                    existing_team.home_advantage = team_data['home_advantage']
                    existing_team.current_form = team_data['current_form']
                else:
                    # Create new team
                    new_team = Team(**team_data)
                    db.session.add(new_team)
                
                total_updated += 1
        
        try:
            db.session.commit()
            print(f"Successfully updated {total_updated} teams across all leagues")
            return True, total_updated
        except Exception as e:
            db.session.rollback()
            print(f"Error updating leagues: {e}")
            return False, 0
    
    def get_league_info(self):
        """Get information about all supported leagues"""
        return {
            'total_leagues': len(self.supported_leagues),
            'leagues': self.supported_leagues,
            'api_status': 'Connected' if self.api_key else 'No API Key',
            'coverage': 'Global - Major European & Turkish leagues'
        }