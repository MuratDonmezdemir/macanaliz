import os
import requests
from datetime import datetime, timedelta
from dateutil import parser
from flask import current_app

class FootballDataService:
    BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"
    
    def __init__(self, api_key=None, api_host=None):
        self.api_key = api_key or os.getenv('FOOTBALL_DATA_API_KEY') or os.getenv('X_RAPIDAPI_KEY')
        self.api_host = api_host or os.getenv('FOOTBALL_DATA_API_HOST') or os.getenv('X_RAPIDAPI_HOST')
        
        if not self.api_key or not self.api_host:
            raise ValueError("API anahtarı veya host adı eksik. Lütfen .env dosyanızı kontrol edin.")
            
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': self.api_host,
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, endpoint, params=None):
        """API isteği yapar ve yanıtı döndürür"""
        try:
            current_app.logger.debug(f"Making request to: {self.BASE_URL}{endpoint}")
            current_app.logger.debug(f"Headers: {self.headers}")
            current_app.logger.debug(f"Params: {params}")
            
            response = requests.get(
                f"{self.BASE_URL}{endpoint}",
                headers=self.headers,
                params=params or {},
                timeout=10  # 10 saniye timeout
            )
            
            current_app.logger.debug(f"Response status: {response.status_code}")
            current_app.logger.debug(f"Response headers: {response.headers}")
            
            response.raise_for_status()
            
            # Yanıtı JSON'a çevirmeden önce içeriğini logla
            response_data = response.json()
            current_app.logger.debug(f"Response data: {response_data}")
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"API isteği başarısız: {type(e).__name__}")
            current_app.logger.error(f"Hata detayı: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                current_app.logger.error(f"Status code: {e.response.status_code}")
                current_app.logger.error(f"Response headers: {e.response.headers}")
                try:
                    error_body = e.response.json()
                    current_app.logger.error(f"Error response: {error_body}")
                except:
                    current_app.logger.error(f"Response text: {e.response.text[:500]}...")
            return None
    
    def get_todays_matches(self):
        """Bugünün maçlarını getirir"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            current_app.logger.info(f"Bugünün maçları getiriliyor: {today}")
            
            endpoint = '/fixtures'
            params = {'date': today}
            
            current_app.logger.debug("API isteği yapılıyor...")
            response = self._make_request(endpoint, params)
            
            if not response:
                current_app.logger.warning("API'den yanıt alınamadı")
                return []
                
            if 'response' not in response:
                current_app.logger.error(f"Beklenmeyen yanıt formatı: {response}")
                return []
            
            matches = response['response']
            current_app.logger.info(f"Başarıyla {len(matches)} maç getirildi")
            return matches
            
        except Exception as e:
            current_app.logger.error(f"get_todays_matches hatası: {str(e)}", exc_info=True)
            return []
    
    def get_competitions(self, country_code=None, include_all=True):
        """Tüm ligleri ve turnuvaları getirir
        
        Args:
            country_code (str, optional): Ülke kodu (örn: 'TR', 'EN')
            include_all (bool): Tüm ligleri ve turnuvaları getir (Varsayılan: True)
            
        Returns:
            list: Lig ve turnuva listesi
        """
        competitions = []
        
        # 1. Öncelikle API'den mevcut sezonun liglerini çek
        try:
            endpoint = "/leagues"
            params = {'current': 'true'}
            
            if country_code:
                params['code'] = country_code.upper()
                
            response = self._make_request(endpoint, params=params)
            if response and 'response' in response:
                for comp in response['response']:
                    league = comp.get('league', {})
                    country = comp.get('country', {})
                    
                    # Lig türünü belirle
                    league_type = 'domestic'  # Varsayılan olarak yerel lig
                    league_name = league.get('name', '').lower()
                    
                    # Özel turnuvaları tespit et
                    if any(x in league_name for x in ['champions league', 'europa league', 'europa conference']):
                        league_type = 'european'
                    elif 'nations league' in league_name:
                        league_type = 'national_team'
                    elif any(x in league_name for x in ['world cup', 'euro', 'copa america', 'africa cup', 'asian cup']):
                        league_type = 'international'
                    
                    competitions.append({
                        'id': league.get('id'),
                        'name': league.get('name'),
                        'type': league_type,
                        'logo': league.get('logo'),
                        'country': country.get('name'),
                        'country_code': country.get('code'),
                        'flag': country.get('flag'),
                        'season': comp.get('seasons', [{}])[-1].get('year') if comp.get('seasons') else None
                    })
        except Exception as e:
            current_app.logger.error(f'Ligler çekilirken hata: {str(e)}')
        
        # 2. Eğer özel ligler de isteniyorsa ekle
        if include_all:
            special_competitions = [
                # UEFA Turnuvaları
                {
                    'id': 2,  # UEFA Champions League
                    'name': 'UEFA Champions League',
                    'type': 'european',
                    'country': 'Europe',
                    'country_code': 'EU',
                    'logo': 'path/to/ucl.png'
                },
                {
                    'id': 3,  # UEFA Europa League
                    'name': 'UEFA Europa League',
                    'type': 'european',
                    'country': 'Europe',
                    'country_code': 'EU',
                    'logo': 'path/to/uel.png'
                },
                # UEFA Nations League
                {
                    'id': 5,
                    'name': 'UEFA Nations League A',
                    'type': 'national_team',
                    'country': 'Europe',
                    'country_code': 'EU',
                    'logo': 'path/to/unl.png'
                },
                # Diğer kıta turnuvaları
                {
                    'id': 10,
                    'name': 'FIFA World Cup',
                    'type': 'international',
                    'country': 'World',
                    'country_code': 'INT',
                    'logo': 'path/to/worldcup.png'
                },
                # Daha fazla özel turnuva eklenebilir
            ]
            
            # Eğer ülke kodu belirtilmişse, sadece o ülkeye ait ligleri ekle
            if not country_code:
                competitions.extend(special_competitions)
            
        return competitions
    
    def get_teams(self, league_id, season=None):
        """Belirli bir ligdeki takımları getirir
        
        Args:
            league_id (int): Lig ID'si
            season (int, optional): Sezon yılı (örn: 2023). Belirtilmezse mevcut sezon kullanılır.
            
        Returns:
            list: Takım listesi
        """
        try:
            if not season:
                season = datetime.now().year
                
            endpoint = "/teams"
            params = {
                'league': league_id,
                'season': season
            }
            
            response = self._make_request(endpoint, params=params)
            if not response or 'response' not in response:
                return []
                
            teams = []
            for team_data in response['response']:
                team = team_data.get('team', {})
                venue = team_data.get('venue', {})
                
                teams.append({
                    'id': team.get('id'),
                    'name': team.get('name'),
                    'code': team.get('code'),
                    'country': team.get('country'),
                    'founded': team.get('founded'),
                    'national': team.get('national', False),
                    'logo': team.get('logo'),
                    'venue': {
                        'name': venue.get('name'),
                        'address': venue.get('address'),
                        'city': venue.get('city'),
                        'capacity': venue.get('capacity'),
                        'surface': venue.get('surface'),
                        'image': venue.get('image')
                    }
                })
                
            return teams
            
        except Exception as e:
            current_app.logger.error(f'Takımlar çekilirken hata (Lig ID: {league_id}): {str(e)}')
            return []
    
    def get_matches(self, league_id=None, season=None, date_from=None, date_to=None, team_id=None, status=None):
        """Maçları getirir
        
        Args:
            league_id (int, optional): Lig ID'si. Belirtilmezse tüm liglerdeki maçlar getirilir.
            season (int, optional): Sezon yılı (örn: 2023). Belirtilmezse mevcut sezon kullanılır.
            date_from (str, optional): Başlangıç tarihi (YYYY-MM-DD formatında). Varsayılan: bugün
            date_to (str, optional): Bitiş tarihi (YYYY-MM-DD formatında). Varsayılan: bugünden 7 gün sonrası
            team_id (int, optional): Belirli bir takımın maçlarını getirmek için takım ID'si
            status (str, optional): Maç durumu (FT, NS, 1H, 2H, HT, ET, BT, PT, SUSP, INT, CANC, AWD, WO, ABD, AET, PEN, PST, TBD, NS, LIVE)
            
        Returns:
            list: Maç listesi
        """
        try:
            if not season:
                season = datetime.now().year
                
            endpoint = "/fixtures"
            params = {
                'season': season
            }
            
            if league_id:
                params['league'] = league_id
                
            if date_from:
                params['from'] = date_from
            else:
                params['from'] = datetime.now().strftime('%Y-%m-%d')
                
            if date_to:
                params['to'] = date_to
            else:
                params['to'] = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
                
            if team_id:
                params['team'] = team_id
                
            if status:
                params['status'] = status
            
            response = self._make_request(endpoint, params=params)
            if not response or 'response' not in response:
                return []
                
            matches = []
            for match_data in response['response']:
                fixture = match_data.get('fixture', {})
                league = match_data.get('league', {})
                teams = match_data.get('teams', {})
                goals = match_data.get('goals', {})
                score = match_data.get('score', {})
                
                # Maç durumunu belirle
                status_code = fixture.get('status', {}).get('short')
                match_status = {
                    'FT': 'Maç Bitti',
                    'NS': 'Başlamadı',
                    '1H': '1. Devre',
                    '2H': '2. Devre',
                    'HT': 'Devre Arası',
                    'ET': 'Uzatmalar',
                    'BT': 'Devre Arası',
                    'P': 'Penaltılar',
                    'SUSP': 'Durduruldu',
                    'INT': 'Yarıda Kaldı',
                    'CANC': 'İptal Edildi',
                    'AWD': 'Hükmen',
                    'WO': 'Hükmen',
                    'ABD': 'Ertelendi',
                    'AET': 'Uzatmalar Bitti',
                    'PEN': 'Penaltılar',
                    'PST': 'Ertelendi',
                    'TBD': 'Belli Değil',
                    'NS': 'Başlamadı',
                    'LIVE': 'Canlı'
                }.get(status_code, status_code)
                
                matches.append({
                    'fixture': {
                        'id': fixture.get('id'),
                        'date': fixture.get('date'),
                        'timestamp': fixture.get('timestamp'),
                        'status': {
                            'short': status_code,
                            'long': fixture.get('status', {}).get('long'),
                            'elapsed': fixture.get('status', {}).get('elapsed'),
                            'translated': match_status
                        },
                        'referee': fixture.get('referee'),
                        'venue': fixture.get('venue', {}).get('name'),
                        'city': fixture.get('venue', {}).get('city')
                    },
                    'league': {
                        'id': league.get('id'),
                        'name': league.get('name'),
                        'country': league.get('country'),
                        'logo': league.get('logo'),
                        'flag': league.get('flag'),
                        'season': league.get('season'),
                        'round': league.get('round')
                    },
                    'teams': {
                        'home': {
                            'id': teams.get('home', {}).get('id'),
                            'name': teams.get('home', {}).get('name'),
                            'logo': teams.get('home', {}).get('logo'),
                            'winner': teams.get('home', {}).get('winner')
                        },
                        'away': {
                            'id': teams.get('away', {}).get('id'),
                            'name': teams.get('away', {}).get('name'),
                            'logo': teams.get('away', {}).get('logo'),
                            'winner': teams.get('away', {}).get('winner')
                        }
                    },
                    'goals': {
                        'home': goals.get('home'),
                        'away': goals.get('away')
                    },
                    'score': {
                        'halftime': {
                            'home': score.get('halftime', {}).get('home'),
                            'away': score.get('halftime', {}).get('away')
                        },
                        'fulltime': {
                            'home': score.get('fulltime', {}).get('home'),
                            'away': score.get('fulltime', {}).get('away')
                        },
                        'extratime': {
                            'home': score.get('extratime', {}).get('home'),
                            'away': score.get('extratime', {}).get('away')
                        },
                        'penalty': {
                            'home': score.get('penalty', {}).get('home'),
                            'away': score.get('penalty', {}).get('away')
                        }
                    }
                })
                
            return matches
            
        except Exception as e:
            current_app.logger.error(f'Maçlar çekilirken hata (Lig ID: {league_id}): {str(e)}')
            return []
    
    def get_team_matches(self, team_id, season=None, date_from=None, date_to=None, status=None):
        """Belirli bir takımın maçlarını getirir
        
        Args:
            team_id (int): Takım ID'si
            season (int, optional): Sezon yılı (örn: 2023). Belirtilmezse mevcut sezon kullanılır.
            date_from (str, optional): Başlangıç tarihi (YYYY-MM-DD formatında). Varsayılan: 30 gün öncesi
            date_to (str, optional): Bitiş tarihi (YYYY-MM-DD formatında). Varsayılan: bugün
            status (str, optional): Maç durumu (FT, NS, 1H, 2H, HT, ET, BT, PT, SUSP, INT, CANC, AWD, WO, ABD, AET, PEN, PST, TBD, NS, LIVE)
            
        Returns:
            list: Takımın maç listesi
        """
        try:
            # Varsayılan tarih aralığını ayarla
            if not date_from:
                date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if not date_to:
                date_to = datetime.now().strftime('%Y-%m-%d')
                
            # get_matches metodunu kullanarak takım maçlarını getir
            return self.get_matches(
                team_id=team_id,
                season=season,
                date_from=date_from,
                date_to=date_to,
                status=status
            )
            
        except Exception as e:
            current_app.logger.error(f'Takım maçları çekilirken hata (Takım ID: {team_id}): {str(e)}')
            return []
    
    def get_standings(self, league_id, season=None):
        """Lig sıralamalarını getirir
        
        Args:
            league_id (int): Lig ID'si
            season (int, optional): Sezon yılı (örn: 2023). Belirtilmezse mevcut sezon kullanılır.
            
        Returns:
            dict: Lig sıralama bilgileri
        """
        try:
            if not season:
                season = datetime.now().year
                
            endpoint = "/standings"
            params = {
                'league': league_id,
                'season': season
            }
            
            response = self._make_request(endpoint, params=params)
            if not response or 'response' not in response or not response['response']:
                return {}
                
            # İlk yanıtı al (genellikle sadece bir lig döner)
            standings_data = response['response'][0]
            league_info = standings_data.get('league', {})
            
            # Lig bilgilerini çıkar
            league = {
                'id': league_info.get('id'),
                'name': league_info.get('name'),
                'country': league_info.get('country'),
                'logo': league_info.get('logo'),
                'flag': league_info.get('flag'),
                'season': league_info.get('season'),
                'standings': []
            }
            
            # Her grup için sıralamayı işle
            for standing in standings_data.get('standings', []):
                group_name = standing.get('group', 'Genel Sıralama')
                standings = []
                
                for rank in standing.get('all', []):
                    team = rank.get('team', {})
                    stats = {
                        'rank': rank.get('rank'),
                        'team': {
                            'id': team.get('id'),
                            'name': team.get('name'),
                            'logo': team.get('logo')
                        },
                        'points': rank.get('points'),
                        'goalsDiff': rank.get('goalsDiff'),
                        'form': rank.get('form'),
                        'played': rank.get('all', {}).get('played'),
                        'win': rank.get('all', {}).get('win'),
                        'draw': rank.get('all', {}).get('draw'),
                        'lose': rank.get('all', {}).get('lose'),
                        'goalsFor': rank.get('all', {}).get('goals', {}).get('for'),
                        'goalsAgainst': rank.get('all', {}).get('goals', {}).get('against'),
                        'clean_sheet': rank.get('clean_sheet', {}).get('total', 0),
                        'failed_to_score': rank.get('failed_to_score', {}).get('total', 0)
                    }
                    standings.append(stats)
                
                league['standings'].append({
                    'group': group_name,
                    'table': standings
                })
            
            return league
            
        except Exception as e:
            current_app.logger.error(f'Sıralama bilgileri çekilirken hata (Lig ID: {league_id}): {str(e)}')
            return {}
    
    def get_todays_matches(self, league_id=None):
        """Bugünkü maçları getirir
        
        Args:
            league_id (int, optional): Belirli bir lig ID'si
            
        Returns:
            dict: Bugünkü maçlar, lige göre gruplanmış şekilde
        """
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Bugünkü maçları getir
            matches = self.get_matches(
                league_id=league_id,
                date_from=today,
                date_to=today
            )
            
            # Maçları lige göre grupla
            matches_by_league = {}
            
            for match in matches:
                league_id = match.get('league', {}).get('id')
                if league_id not in matches_by_league:
                    matches_by_league[league_id] = {
                        'league': match.get('league', {}),
                        'matches': []
                    }
                matches_by_league[league_id]['matches'].append(match)
            
            # Sözlüğü listeye çevir ve sırala (önem sırasına göre)
            result = list(matches_by_league.values())
            
            # Lige göre sırala (önem sırasına göre)
            league_priority = {
                'UEFA Champions League': 1,
                'UEFA Europa League': 2,
                'Premier League': 3,
                'La Liga': 4,
                'Bundesliga': 5,
                'Serie A': 6,
                'Ligue 1': 7,
                'Süper Lig': 8,
                'UEFA Europa Conference League': 9,
                'UEFA Nations League': 10
            }
            
            result.sort(key=lambda x: league_priority.get(x['league'].get('name'), 99) if x['league'] else 100)
            
            return {
                'status': 'success',
                'date': today,
                'leagues': result,
                'total_matches': sum(len(league['matches']) for league in result)
            }
            
        except Exception as e:
            current_app.logger.error(f'Bugünkü maçlar çekilirken hata: {str(e)}')
            return {
                'status': 'error',
                'message': 'Bugünkü maçlar çekilirken bir hata oluştu',
                'error': str(e)
            }
    
    def get_match(self, match_id):
        """Belirli bir maçın detaylarını getirir
        
        Args:
            match_id (int): Maç ID'si
            
        Returns:
            dict: Maç detayları, istatistikler, kadrolar ve diğer bilgiler
        """
        try:
            # Temel maç bilgilerini getir
            endpoint = "/fixtures"
            params = {'id': match_id}
            
            response = self._make_request(endpoint, params=params)
            if not response or 'response' not in response or not response['response']:
                return {'status': 'error', 'message': 'Maç bulunamadı'}
                
            match_data = response['response'][0]
            
            # Maç detaylarını işle
            fixture = match_data.get('fixture', {})
            league = match_data.get('league', {})
            teams = match_data.get('teams', {})
            goals = match_data.get('goals', {})
            score = match_data.get('score', {})
            
            # Maç durumunu belirle
            status_code = fixture.get('status', {}).get('short')
            match_status = {
                'FT': 'Maç Bitti', 'NS': 'Başlamadı', '1H': '1. Devre', '2H': '2. Devre',
                'HT': 'Devre Arası', 'ET': 'Uzatmalar', 'BT': 'Devre Arası', 'P': 'Penaltılar',
                'SUSP': 'Durduruldu', 'INT': 'Yarıda Kaldı', 'CANC': 'İptal Edildi',
                'AWD': 'Hükmen', 'WO': 'Hükmen', 'ABD': 'Ertelendi', 'AET': 'Uzatmalar Bitti',
                'PEN': 'Penaltılar', 'PST': 'Ertelendi', 'TBD': 'Belli Değil', 'LIVE': 'Canlı'
            }.get(status_code, status_code)
            
            # Maç detaylarını oluştur
            match_info = {
                'fixture': {
                    'id': fixture.get('id'),
                    'date': fixture.get('date'),
                    'timestamp': fixture.get('timestamp'),
                    'status': {
                        'short': status_code,
                        'long': fixture.get('status', {}).get('long'),
                        'elapsed': fixture.get('status', {}).get('elapsed'),
                        'translated': match_status
                    },
                    'referee': fixture.get('referee'),
                    'venue': {
                        'id': fixture.get('venue', {}).get('id'),
                        'name': fixture.get('venue', {}).get('name'),
                        'city': fixture.get('venue', {}).get('city')
                    },
                    'attendance': fixture.get('attendance'),
                    'periods': fixture.get('periods', {})
                },
                'league': {
                    'id': league.get('id'),
                    'name': league.get('name'),
                    'country': league.get('country'),
                    'logo': league.get('logo'),
                    'flag': league.get('flag'),
                    'season': league.get('season'),
                    'round': league.get('round')
                },
                'teams': {
                    'home': {
                        'id': teams.get('home', {}).get('id'),
                        'name': teams.get('home', {}).get('name'),
                        'logo': teams.get('home', {}).get('logo'),
                        'winner': teams.get('home', {}).get('winner')
                    },
                    'away': {
                        'id': teams.get('away', {}).get('id'),
                        'name': teams.get('away', {}).get('name'),
                        'logo': teams.get('away', {}).get('logo'),
                        'winner': teams.get('away', {}).get('winner')
                    }
                },
                'goals': {
                    'home': goals.get('home'),
                    'away': goals.get('away')
                },
                'score': {
                    'halftime': score.get('halftime', {}),
                    'fulltime': score.get('fulltime', {}),
                    'extratime': score.get('extratime', {}),
                    'penalty': score.get('penalty', {})
                },
                'events': [],
                'lineups': {
                    'home': {'starting_xi': [], 'substitutes': [], 'coach': None, 'formation': None},
                    'away': {'starting_xi': [], 'substitutes': [], 'coach': None, 'formation': None}
                },
                'statistics': {
                    'home': [],
                    'away': []
                },
                'players': {
                    'home': [],
                    'away': []
                }
            }
            
            # Maç olaylarını getir
            events_endpoint = f"/fixtures/events?fixture={match_id}"
            events_response = self._make_request(events_endpoint)
            if events_response and 'response' in events_response:
                match_info['events'] = events_response['response']
            
            # Kadro bilgilerini getir
            lineups_endpoint = f"/fixtures/lineups?fixture={match_id}"
            lineups_response = self._make_request(lineups_endpoint)
            if lineups_response and 'response' in lineups_response:
                for team_lineup in lineups_response['response']:
                    team_side = 'home' if team_lineup.get('team', {}).get('id') == match_info['teams']['home']['id'] else 'away'
                    
                    # Teknik direktör bilgisi
                    if 'coach' in team_lineup:
                        match_info['lineups'][team_side]['coach'] = {
                            'id': team_lineup['coach'].get('id'),
                            'name': team_lineup['coach'].get('name'),
                            'photo': team_lineup['coach'].get('photo')
                        }
                    
                    # Formasyon
                    match_info['lineups'][team_side]['formation'] = team_lineup.get('formation')
                    
                    # İlk 11
                    for player in team_lineup.get('startXI', []):
                        player_info = player.get('player', {})
                        match_info['lineups'][team_side]['starting_xi'].append({
                            'id': player_info.get('id'),
                            'name': player_info.get('name'),
                            'number': player.get('number'),
                            'pos': player.get('pos'),
                            'grid': player.get('grid')
                        })
                    
                    # Yedekler
                    for player in team_lineup.get('substitutes', []):
                        player_info = player.get('player', {})
                        match_info['lineups'][team_side]['substitutes'].append({
                            'id': player_info.get('id'),
                            'name': player_info.get('name'),
                            'number': player.get('number'),
                            'pos': player.get('pos'),
                            'grid': player.get('grid')
                        })
            
            # İstatistikleri getir
            stats_endpoint = f"/fixtures/statistics?fixture={match_id}"
            stats_response = self._make_request(stats_endpoint)
            if stats_response and 'response' in stats_response:
                for team_stats in stats_response['response']:
                    team_side = 'home' if team_stats.get('team', {}).get('id') == match_info['teams']['home']['id'] else 'away'
                    match_info['statistics'][team_side] = team_stats.get('statistics', [])
            
            # Oyuncu istatistiklerini getir
            players_endpoint = f"/fixtures/players?fixture={match_id}"
            players_response = self._make_request(players_endpoint)
            if players_response and 'response' in players_response:
                for team_players in players_response['response']:
                    team_side = 'home' if team_players.get('team', {}).get('id') == match_info['teams']['home']['id'] else 'away'
                    match_info['players'][team_side] = team_players.get('players', [])
            
            return {
                'status': 'success',
                'data': match_info
            }
            
        except Exception as e:
            current_app.logger.error(f'Maç detayları çekilirken hata (Maç ID: {match_id}): {str(e)}')
            return {
                'status': 'error',
                'message': 'Maç detayları çekilirken bir hata oluştu',
                'error': str(e)
            }
