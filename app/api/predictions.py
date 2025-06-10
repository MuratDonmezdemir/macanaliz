"""
Futbol maç tahminleri için API endpoint'leri
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest, HTTPException, NotFound
from sqlalchemy.orm import Session

from app import db
from app.models import Match, Team, League
from .. import prediction_engine

# Blueprint tanımı
bp = Blueprint('predictions', __name__)

# Varsayılan tahmin parametreleri
DEFAULT_MATCHES_BACK = 7
DEFAULT_MIN_DRAW_PROB = 0.35
DEFAULT_MIN_HIGH_SCORING_PROB = 0.3

# Hata yönetimi için yardımcı fonksiyon
def handle_error(e: Exception, status_code: int = 500) -> tuple:
    """Hata yanıtlarını standartlaştırır"""
    error_message = str(e)
    if hasattr(e, 'description'):
        error_message = e.description
    return jsonify({
        'success': False,
        'error': error_message,
        'code': getattr(e, 'code', status_code),
        'timestamp': datetime.utcnow().isoformat()
    }), status_code

@bp.route('/match/<int:match_id>', methods=['GET'])
def predict_match(match_id: int) -> tuple:
    """
    Belirli bir maç için tahmin yapar
    
    Parametreler:
        match_id: Tahmin yapılacak maçın ID'si
        
    Dönüş:
        JSON formatında tahmin sonuçları
    """
    try:
        # Maç bilgilerini veritabanından al
        match = db.session.query(Match).get(match_id)
        if not match:
            return handle_error(HTTPException('Maç bulunamadı'), 404)
            
        # Tahmin motorunu başlat
        predictor = MatchPredictor(db.session)
        
        # Tahmini yap
        prediction = predictor.predict_match(
            home_team_id=match.home_team_id,
            away_team_id=match.away_team_id,
            match_date=match.match_date
        )
        
        # Yanıtı hazırla
        response = {
            'success': True,
            'match': {
                'id': match.id,
                'home_team': match.home_team.name,
                'away_team': match.away_team.name,
                'match_date': match.match_date.isoformat(),
                'league': {
                    'id': match.league.id,
                    'name': match.league.name
                } if match.league else None
            },
            'prediction': prediction,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        return handle_error(e)


@bp.route('/high-draw-probability', methods=['GET'])
def get_high_draw_probability_matches() -> tuple:
    """
    Yüksek beraberlik ihtimali olan maçları listeler
    
    Query Parametreleri:
        min_prob: Minimum beraberlik olasılığı (varsayılan: 0.35)
        league_id: Filtreleme için lig ID'si (isteğe bağlı)
        days_ahead: Kaç gün ilerisindeki maçlar kontrol edilecek (varsayılan: 7)
    
    Dönüş:
        JSON formatında yüksek beraberlik ihtimali olan maçlar
    """
    try:
        # Parametreleri al
        min_prob = float(request.args.get('min_prob', DEFAULT_MIN_DRAW_PROB))
        league_id = request.args.get('league_id', type=int)
        days_ahead = int(request.args.get('days_ahead', 7))
        
        # Tarih aralığını belirle
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=days_ahead)
        
        # İlgili maçları veritabanından al
        query = db.session.query(Match).filter(
            Match.match_date.between(start_date, end_date)
        )
        
        if league_id:
            query = query.filter(Match.league_id == league_id)
            
        matches = query.all()
        
        if not matches:
            return jsonify({
                'success': True,
                'matches': [],
                'message': 'Belirtilen kriterlere uygun maç bulunamadı.'
            })
        
        # Tahmin motorunu başlat
        predictor = prediction_engine.MatchPredictor(db.session, league_id=league_id)
        
        # Yüksek beraberlik ihtimali olan maçları bul
        high_draw_matches = predictor.find_high_draw_probability_matches(
            matches=matches,
            min_draw_prob=min_prob
        )
        
        # Yanıtı hazırla
        response = {
            'success': True,
            'count': len(high_draw_matches),
            'min_draw_probability': min_prob,
            'matches': [{
                'match_id': match.id,
                'home_team': match.home_team.name,
                'away_team': match.away_team.name,
                'match_date': match.match_date.isoformat(),
                'league': {
                    'id': match.league.id,
                    'name': match.league.name
                } if match.league else None,
                'prediction': predictor.predict_match(
                    home_team_id=match.home_team_id,
                    away_team_id=match.away_team_id,
                    match_date=match.match_date
                )
            } for match in high_draw_matches],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        return handle_error(e)


@bp.route('/high-scoring', methods=['GET'])
def get_high_scoring_matches() -> tuple:
    """
    Yüksek gol beklenen (5+ gol) maçları listeler
    
    Query Parametreleri:
        min_prob: Minimum 5+ gol olasılığı (varsayılan: 0.3)
        league_id: Filtreleme için lig ID'si (isteğe bağlı)
        days_ahead: Kaç gün ilerisindeki maçlar kontrol edilecek (varsayılan: 7)
    
    Dönüş:
        JSON formatında yüksek gol beklenen maçlar
    """
    try:
        # Parametreleri al
        min_prob = float(request.args.get('min_prob', DEFAULT_MIN_HIGH_SCORING_PROB))
        league_id = request.args.get('league_id', type=int)
        days_ahead = int(request.args.get('days_ahead', 7))
        
        # Tarih aralığını belirle
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=days_ahead)
        
        # İlgili maçları veritabanından al
        query = db.session.query(Match).filter(
            Match.match_date.between(start_date, end_date)
        )
        
        if league_id:
            query = query.filter(Match.league_id == league_id)
            
        matches = query.all()
        
        if not matches:
            return jsonify({
                'success': True,
                'matches': [],
                'message': 'Belirtilen kriterlere uygun maç bulunamadı.'
            })
        
        # Tahmin motorunu başlat
        predictor = prediction_engine.MatchPredictor(db.session, league_id=league_id)
        
        # Yüksek gol beklenen maçları bul
        high_scoring_matches = []
        for match in matches:
            try:
                prob = predictor.calculate_high_scoring_probability(
                    home_team_id=match.home_team_id,
                    away_team_id=match.away_team_id,
                    match_date=match.match_date
                )
                
                if prob >= min_prob:
                    high_scoring_matches.append({
                        'match': match,
                        'high_scoring_probability': prob
                    })
            except Exception as e:
                # Hata durumunda bu maçı atla
                continue
        
        # Sırala (yüksek olasılıktan düşüğe)
        high_scoring_matches.sort(key=lambda x: x['high_scoring_probability'], reverse=True)
        
        # Yanıtı hazırla
        response = {
            'success': True,
            'count': len(high_scoring_matches),
            'min_high_scoring_probability': min_prob,
            'matches': [{
                'match_id': item['match'].id,
                'home_team': item['match'].home_team.name,
                'away_team': item['match'].away_team.name,
                'match_date': item['match'].match_date.isoformat(),
                'league': {
                    'id': item['match'].league.id,
                    'name': item['match'].league.name
                } if item['match'].league else None,
                'high_scoring_probability': item['high_scoring_probability'],
                'prediction': predictor.predict_match(
                    home_team_id=item['match'].home_team_id,
                    away_team_id=item['match'].away_team_id,
                    match_date=item['match'].match_date
                )
            } for item in high_scoring_matches],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        return handle_error(e)
