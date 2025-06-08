from flask import Blueprint, render_template, redirect, url_for, current_app, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.services.football_data import FootballDataService

bp = Blueprint('main', __name__)

def get_popular_leagues():
    """Popüler liglerin bilgilerini döndürür"""
    return [
        {'id': 39, 'name': 'Premier League', 'country': 'England', 'logo': 'premier-league.png'},
        {'id': 140, 'name': 'La Liga', 'country': 'Spain', 'logo': 'laliga.png'},
        {'id': 135, 'name': 'Serie A', 'country': 'Italy', 'logo': 'serie-a.png'},
        {'id': 78, 'name': 'Bundesliga', 'country': 'Germany', 'logo': 'bundesliga.png'},
        {'id': 61, 'name': 'Ligue 1', 'country': 'France', 'logo': 'ligue-1.png'},
        {'id': 88, 'name': 'Primeira Liga', 'country': 'Portugal', 'logo': 'liga-portugal.png'},
        {'id': 2, 'name': 'UEFA Champions League', 'country': 'Europe', 'logo': 'champions-league.png'},
        {'id': 3, 'name': 'UEFA Europa League', 'country': 'Europe', 'logo': 'europa-league.png'},
        {'id': 1, 'name': 'World Cup', 'country': 'World', 'logo': 'world-cup.png'}
    ]

@bp.route('/')
def index():
    """Ana sayfa"""
    try:
        current_app.logger.info("=" * 50)
        current_app.logger.info("Ana sayfa isteği başladı")
        
        # FootballDataService oluştur
        try:
            current_app.logger.info("FootballDataService oluşturuluyor...")
            service = FootballDataService()
            current_app.logger.info("FootballDataService başarıyla oluşturuldu")
            
            # API anahtarını ve host'u logla (ilk birkaç karakteri güvenli bir şekilde)
            if hasattr(service, 'api_key'):
                current_app.logger.info(f"API Anahtarı: {service.api_key[:5]}...{service.api_key[-3:] if service.api_key else ''}")
            if hasattr(service, 'api_host'):
                current_app.logger.info(f"API Host: {service.api_host}")
                
        except Exception as e:
            error_msg = f"FootballDataService oluşturulamadı: {str(e)}"
            current_app.logger.error(error_msg, exc_info=True)
            return render_template('main/error.html', 
                               error='API servisine bağlanılamadı',
                               error_details=error_msg,
                               popular_leagues=[]), 500
        
        today = datetime.now().strftime('%Y-%m-%d')
        current_app.logger.info(f"Bugünün tarihi: {today}")
        
        # Bugünün maçlarını getir
        try:
            current_app.logger.info("Bugünün maçları getiriliyor...")
            matches = service.get_todays_matches()
            current_app.logger.info(f"{len(matches)} adet maç bulundu")
        except Exception as e:
            current_app.logger.error(f"Maçlar getirilirken hata: {str(e)}", exc_info=True)
            matches = []
        
        # Maçları lige göre grupla
        matches_by_league = {}
        try:
            for match in matches:
                if not isinstance(match, dict) or 'league' not in match:
                    current_app.logger.warning(f"Geçersiz maç formatı: {match}")
                    continue
                    
                league_info = match.get('league', {})
                if not isinstance(league_info, dict) or 'id' not in league_info:
                    current_app.logger.warning(f"Geçersiz lig bilgisi: {league_info}")
                    continue
                    
                league_id = league_info['id']
                if league_id not in matches_by_league:
                    matches_by_league[league_id] = {
                        'league': league_info,
                        'matches': []
                    }
                matches_by_league[league_id]['matches'].append(match)
                
            current_app.logger.info(f"{len(matches_by_league)} farklı lig için maç bulundu")
            
        except Exception as e:
            current_app.logger.error(f"Maçlar gruplanırken hata: {str(e)}", exc_info=True)
            return render_template('main/index.html', 
                               error='Maç bilgileri işlenirken bir hata oluştu',
                               debug_error=str(e),
                               popular_leagues=get_popular_leagues())
        
        # Eğer bugün maç yoksa, yarının maçlarını getir
        if not matches:
            current_app.logger.info("Bugün maç bulunamadı, yarının maçları deneniyor...")
            try:
                tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
                response = service._make_request('/fixtures', params={'date': tomorrow})
                matches = response.get('response', []) if response else []
                current_app.logger.info(f"Yarın için {len(matches)} maç bulundu")
            except Exception as e:
                current_app.logger.error(f"Yarının maçları getirilirken hata: {str(e)}", exc_info=True)
                matches = []
        
        # Popüler ligleri al
        try:
            popular_leagues = get_popular_leagues()
            current_app.logger.info(f"{len(popular_leagues)} adet popüler lig yüklendi")
        except Exception as e:
            current_app.logger.error(f"Popüler ligler yüklenirken hata: {str(e)}")
            popular_leagues = []
        
        return render_template('main/index.html', 
                             matches_by_league=matches_by_league,
                             today=today,
                             popular_leagues=popular_leagues)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        current_app.logger.error(f'Ana sayfa yüklenirken beklenmeyen hata: {str(e)}')
        current_app.logger.error(f'Hata detayları: {error_details}')
        return render_template('main/error.html', 
                             error='Bir hata oluştu',
                             error_details=str(e),
                             popular_leagues=[]), 500

@bp.route('/about')
def about():
    return render_template('main/about.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Kullanıcı kontrol paneli"""
    try:
        service = FootballDataService()
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Bugünün maçlarını getir
        matches = service.get_todays_matches()
        
        # Popüler liglerin sıralamalarını getir
        standings = {}
        for league in get_popular_leagues():
            try:
                standing = service.get_standings(league['id'])
                if standing:
                    standings[league['id']] = {
                        'league': league,
                        'standings': standing
                    }
            except Exception as e:
                current_app.logger.error(f"Sıralama getirilirken hata ({league['name']}): {str(e)}")
                continue
        
        return render_template('main/dashboard.html',
                               matches=matches,
                               standings=standings,
                               today=today,
                               popular_leagues=get_popular_leagues())
        
    except Exception as e:
        current_app.logger.error(f'Dashboard yüklenirken hata: {str(e)}')
        return render_template('main/dashboard.html', 
                             error='Veriler yüklenirken bir hata oluştu',
                             popular_leagues=get_popular_leagues())

@bp.route('/league/<int:league_id>')
def league(league_id):
    """Lig detay sayfası"""
    try:
        service = FootballDataService()
        
        # Lig bilgilerini getir
        league_info = None
        for lg in get_popular_leagues():
            if lg['id'] == league_id:
                league_info = lg
                break
        
        if not league_info:
            return render_template('errors/404.html'), 404
        
        # Puan durumu
        standings = service.get_standings(league_id)
        
        # Maçlar
        matches = service.get_matches(league_id)
        
        # Takımlar
        teams = service.get_teams(league_id)
        
        return render_template('main/league.html',
                             league=league_info,
                             standings=standings[0]['league']['standards'][0] if standings and len(standings) > 0 else None,
                             matches=matches,
                             teams=teams,
                             popular_leagues=get_popular_leagues())
        
    except Exception as e:
        current_app.logger.error(f'Lig sayfası yüklenirken hata: {str(e)}')
        return render_template('errors/500.html'), 500

@bp.route('/match/<int:match_id>')
def match(match_id):
    """Maç detay sayfası"""
    try:
        service = FootballDataService()
        
        # Maç bilgilerini getir
        match_data = service.get_match(match_id)
        
        if not match_data:
            return render_template('errors/404.html'), 404
        
        return render_template('main/match.html',
                             match=match_data,
                             popular_leagues=get_popular_leagues())
        
    except Exception as e:
        current_app.logger.error(f'Maç sayfası yüklenirken hata: {str(e)}')
        return render_template('errors/500.html'), 500

@bp.route('/team/<int:team_id>')
def team(team_id):
    """Takım detay sayfası"""
    try:
        service = FootballDataService()
        
        # Takım bilgilerini getir
        team_data = service._make_request('/teams', params={'id': team_id})
        
        if not team_data or 'response' not in team_data or not team_data['response']:
            return render_template('errors/404.html'), 404
            
        team_info = team_data['response'][0]['team']
        
        # Takımın maçlarını getir
        matches = service.get_team_matches(team_id)
        
        return render_template('main/team.html',
                             team=team_info,
                             matches=matches,
                             popular_leagues=get_popular_leagues())
        
    except Exception as e:
        current_app.logger.error(f'Takım sayfası yüklenirken hata: {str(e)}')
        return render_template('errors/500.html'), 500
