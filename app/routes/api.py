"""
API Rotaları Modülü

Bu modül, uygulamanın tüm API endpoint'lerini içerir.
Futbol verileri, maç istatistikleri ve tahminlerle ilgili endpoint'ler burada tanımlanır.
"""
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
import json

# Modelleri içe aktar
from app.models.match import Match, Prediction
from app.models.team import Team
from app.models.league import League
from app.models.user import User

# Servisler
from app.services.football_data import FootballDataService
from app import db, cache

# Blueprint oluşturma
api_bp = Blueprint('api', __name__)

# Servis örneği oluşturma
football_service = FootballDataService()

# Hata yönetimi için özel istisna sınıfı
class APIError(Exception):
    """API hatalarını yönetmek için özel istisna sınıfı"""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or {})
        rv['message'] = self.message
        rv['status'] = 'error'
        return rv

def json_response(f):
    """JSON yanıtları için dekoratör"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            if isinstance(result, tuple):
                data, status_code = result
            else:
                data, status_code = result, 200
                
            response = {
                'status': 'success',
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            }
            return jsonify(response), status_code
        except APIError as e:
            return jsonify(e.to_dict()), e.status_code
        except Exception as e:
            current_app.logger.error(f'API Hatası: {str(e)}', exc_info=True)
            return jsonify({
                'status': 'error',
                'message': 'Beklenmeyen bir hata oluştu',
                'error': str(e)
            }), 500
    return decorated_function

# Hata işleyici
@api_bp.errorhandler(APIError)
def handle_api_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# API Rotaları
@api_bp.route('/ligler', methods=['GET'])
@json_response
def get_ligler():
    """Tüm ligleri getirir"""
    cache_key = 'all_leagues'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return cached_data, 200
    
    ligler = League.query.all()
    result = [{
        'id': lig.id,
        'name': lig.name,
        'country': lig.country,
        'logo': lig.logo_url,
        'season': lig.season
    } for lig in ligler]
    
    cache.set(cache_key, result, timeout=3600)  # 1 saat önbellek
    return result, 200

@api_bp.route('/takim/<int:team_id>', methods=['GET'])
@json_response
def get_takim(team_id):
    """Belirli bir takımın detaylarını getirir"""
    cache_key = f'team_{team_id}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return cached_data, 200
    
    takim = Team.query.get_or_404(team_id)
    result = {
        'id': takim.id,
        'name': takim.name,
        'short_name': takim.short_name,
        'logo': takim.logo_url,
        'founded': takim.founded,
        'stadium': takim.stadium.name if takim.stadium else None,
        'league': takim.league.name if takim.league else None
    }
    
    cache.set(cache_key, result, timeout=1800)  # 30 dakika önbellek
    return result, 200

@api_bp.route('/maclar', methods=['GET'])
@json_response
def get_maclar():
    """Filtrelenmiş maç listesini getirir"""
    # Sorgu parametreleri
    league_id = request.args.get('league_id', type=int)
    team_id = request.args.get('team_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    status = request.args.get('status')
    
    # Sorgu oluştur
    query = Match.query
    
    if league_id:
        query = query.filter(Match.league_id == league_id)
    if team_id:
        query = query.filter((Match.home_team_id == team_id) | (Match.away_team_id == team_id))
    if start_date:
        query = query.filter(Match.match_date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Match.match_date <= datetime.fromisoformat(end_date))
    if status:
        query = query.filter(Match.status == status)
    
    # Sıralama ve limit
    matches = query.order_by(Match.match_date.desc()).limit(100).all()
    
    # Sonuçları formatla
    result = []
    for match in matches:
        result.append({
            'id': match.id,
            'date': match.match_date.isoformat(),
            'status': match.status,
            'league': match.league.name if match.league else None,
            'home_team': match.home_team.name if match.home_team else None,
            'away_team': match.away_team.name if match.away_team else None,
            'home_goals': match.home_goals,
            'away_goals': match.away_goals,
            'stadium': match.venue.name if match.venue else None
        })
    
    return result, 200

@api_bp.route('/puan-durumu/<int:league_id>', methods=['GET'])
@json_response
def get_puan_durumu(league_id):
    """Ligin puan durumunu getirir"""
    cache_key = f'standings_{league_id}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return cached_data, 200
    
    # Lig bilgisini al
    league = League.query.get_or_404(league_id)
    
    # Takımları ve maç sonuçlarını al
    teams = Team.query.filter_by(league_id=league_id).all()
    
    # Puan durumu hesaplama
    standings = []
    for team in teams:
        # Burada gerçek puan durumu hesaplamaları yapılacak
        standings.append({
            'position': 0,  # Hesaplanacak
            'team': team.name,
            'played': 0,    # Hesaplanacak
            'won': 0,       # Hesaplanacak
            'drawn': 0,     # Hesaplanacak
            'lost': 0,      # Hesaplanacak
            'goals_for': 0, # Hesaplanacak
            'goals_against': 0, # Hesaplanacak
            'goal_difference': 0, # Hesaplanacak
            'points': 0     # Hesaplanacak
        })
    
    # Örnek veri - gerçek uygulamada veritabanından hesaplanmalı
    result = {
        'league': {
            'id': league.id,
            'name': league.name,
            'country': league.country,
            'season': league.season
        },
        'standings': standings
    }
    
    cache.set(cache_key, result, timeout=3600)  # 1 saat önbellek
    return result, 200

@api_bp.route('/tahmin-yap', methods=['POST'])
@login_required
@json_response
def tahmin_yap():
    """Maç tahmini yapar"""
    if not request.is_json:
        raise APIError('JSON verisi bekleniyor', 400)
    
    data = request.get_json()
    required_fields = ['match_id', 'prediction', 'confidence']
    
    # Gerekli alanları kontrol et
    for field in required_fields:
        if field not in data:
            raise APIError(f'Eksik alan: {field}', 400)
    
    # Maçı bul
    match = Match.query.get_or_404(data['match_id'])
    
    # Tahmini kaydet
    tahmin = Prediction(
        user_id=current_user.id,
        match_id=match.id,
        prediction=data['prediction'],
        confidence=data['confidence'],
        is_correct=None  # Maç sonucu belli olunca güncellenecek
    )
    
    db.session.add(tahmin)
    db.session.commit()
    
    return {
        'id': tahmin.id,
        'match_id': tahmin.match_id,
        'prediction': tahmin.prediction,
        'confidence': tahmin.confidence,
        'created_at': tahmin.created_at.isoformat()
    }, 201

# Kullanıcı istatistikleri
@api_bp.route('/kullanici/istatistikler', methods=['GET'])
@login_required
@json_response
def kullanici_istatistikleri():
    """Kullanıcının tahmin istatistiklerini getirir"""
    # Toplam tahmin sayısı
    total_predictions = Prediction.query.filter_by(user_id=current_user.id).count()
    
    # Doğru tahmin sayısı
    correct_predictions = Prediction.query.filter_by(
        user_id=current_user.id,
        is_correct=True
    ).count()
    
    # Başarı oranı (en az 1 tahmin yapılmışsa)
    success_rate = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0
    
    return {
        'total_predictions': total_predictions,
        'correct_predictions': correct_predictions,
        'success_rate': round(success_rate, 2)
    }, 200