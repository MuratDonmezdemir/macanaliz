from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required
from datetime import datetime, timedelta
from app import db
from app.models import Match, Team, League
from prediction_engine import MatchPredictor
import logging

# Blueprint oluştur
api_bp = Blueprint('api', __name__)

logger = logging.getLogger(__name__)

# Tahmin motorunu başlat
try:
    predictor = MatchPredictor(db.session)
    logger.info("Tahmin motoru başarıyla başlatıldı")
except Exception as e:
    logger.error(f"Tahmin motoru başlatılırken hata: {str(e)}")
    predictor = None

@api_bp.route('/predict/match/<int:match_id>', methods=['GET'])
def get_match_prediction(match_id):
    """
    Belirli bir maç için detaylı tahminleri getirir
    
    Parametreler:
        match_id (int): Maç ID'si
    """
    try:
        if not predictor:
            return jsonify({
                'success': False,
                'message': 'Tahmin motoru şu anda kullanılamıyor'
            }), 503
            
        match = Match.query.get_or_404(match_id)
        
        if not match.home_team_id or not match.away_team_id:
            return jsonify({
                'success': False,
                'message': 'Maç için takım bilgileri eksik'
            }), 400
        
        # Tahminleri al
        prediction = predictor.predict_match(
            home_team_id=match.home_team_id,
            away_team_id=match.away_team_id,
            match_date=match.match_date
        )
        
        if 'error' in prediction:
            return jsonify({
                'success': False,
                'message': prediction.get('error', 'Tahmin yapılamadı'),
                'details': prediction.get('details')
            }), 500
            
        # Maç bilgilerini ekle
        response = {
            'success': True,
            'match': {
                'id': match.id,
                'home_team': match.home_team.name if match.home_team else 'Bilinmiyor',
                'away_team': match.away_team.name if match.away_team else 'Bilinmiyor',
                'match_date': match.match_date.isoformat() if match.match_date else None,
                'league': match.league.name if hasattr(match, 'league') and match.league else None,
                'status': match.status
            },
            'prediction': {
                'match_prediction': {
                    'home_win': f"{prediction['match_prediction']['home_win_prob']*100:.1f}%",
                    'draw': f"{prediction['match_prediction']['draw_prob']*100:.1f}%",
                    'away_win': f"{prediction['match_prediction']['away_win_prob']*100:.1f}%"
                },
                'expected_goals': {
                    'home': prediction['expected_goals']['home'],
                    'away': prediction['expected_goals']['away']
                },
                'high_scoring_prob': f"{prediction['high_scoring_prob']*100:.1f}%"
            },
            'team_stats': {
                'home': {
                    'form': prediction['home_team_form'].get('form', []),
                    'avg_goals_for': prediction['home_team_form'].get('avg_goals_for', 0),
                    'avg_goals_against': prediction['home_team_form'].get('avg_goals_against', 0),
                    'clean_sheets': prediction['home_team_form'].get('clean_sheets', 0),
                    'failed_to_score': prediction['home_team_form'].get('failed_to_score', 0)
                },
                'away': {
                    'form': prediction['away_team_form'].get('form', []),
                    'avg_goals_for': prediction['away_team_form'].get('avg_goals_for', 0),
                    'avg_goals_against': prediction['away_team_form'].get('avg_goals_against', 0),
                    'clean_sheets': prediction['away_team_form'].get('clean_sheets', 0),
                    'failed_to_score': prediction['away_team_form'].get('failed_to_score', 0)
                }
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Maç tahmini alınırken hata: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Beklenmeyen bir hata oluştu',
            'details': str(e)
        }), 500

@api_bp.route('/predict/high-scoring', methods=['GET'])
def get_high_scoring_matches():
    """
    Yüksek skorlu olması muhtemel maçları getirir (6+ gol)
    
    Parametreler:
        days (int): Kaç gün ileriyi kontrol edecek (varsayılan: 7, maksimum: 30)
        min_prob (float): Minimum yüksek skor olasılığı (0-1 arası, varsayılan: 0.3 - %30)
    """
    try:
        if not predictor:
            return jsonify({
                'success': False,
                'message': 'Tahmin motoru şu anda kullanılamıyor'
            }), 503
        
        # Parametreleri al
        days_ahead = min(int(request.args.get('days', 7)), 30)  # Maksimum 30 gün
        min_prob = float(request.args.get('min_prob', 0.3))
        
        # Tarih aralığını belirle
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=days_ahead)
        
        # Planlanmış maçları getir
        matches = Match.query.filter(
            Match.match_date.between(start_date, end_date),
            Match.status == 'SCHEDULED',
            Match.home_team_id.isnot(None),
            Match.away_team_id.isnot(None)
        ).all()
        
        if not matches:
            return jsonify({
                'success': True,
                'message': 'Belirtilen tarih aralığında maç bulunamadı',
                'matches': []
            })
        
        high_scoring_matches = []
        
        for match in matches:
            try:
                # Her maç için tahmin yap
                prediction = predictor.predict_match(
                    home_team_id=match.home_team_id,
                    away_team_id=match.away_team_id,
                    match_date=match.match_date
                )
                
                if 'error' in prediction:
                    continue
                    
                high_scoring_prob = prediction.get('high_scoring_prob', 0)
                
                # Yüksek skor olasılığı eşiği kontrolü
                if high_scoring_prob >= min_prob:
                    high_scoring_matches.append({
                        'match_id': match.id,
                        'home_team': match.home_team.name if match.home_team else 'Bilinmiyor',
                        'away_team': match.away_team.name if match.away_team else 'Bilinmiyor',
                        'match_date': match.match_date.isoformat() if match.match_date else None,
                        'league': match.league.name if hasattr(match, 'league') and match.league else None,
                        'high_scoring_prob': f"{high_scoring_prob*100:.1f}%",
                        'expected_goals': prediction['expected_goals'],
                        'match_prediction': {
                            'home_win': f"{prediction['match_prediction']['home_win_prob']*100:.1f}%",
                            'draw': f"{prediction['match_prediction']['draw_prob']*100:.1f}%",
                            'away_win': f"{prediction['match_prediction']['away_win_prob']*100:.1f}%"
                        }
                    })
                    
            except Exception as e:
                logger.error(f"{match.id} ID'li maç için tahmin yapılırken hata: {str(e)}")
                continue
        
        # Yüksek skor olasılığına göre sırala (yüksekten düşüğe)
        high_scoring_matches.sort(key=lambda x: float(x['high_scoring_prob'].replace('%', '')), reverse=True)
        
        return jsonify({
            'success': True,
            'count': len(high_scoring_matches),
            'min_probability': f"{min_prob*100:.0f}%",
            'days_ahead': days_ahead,
            'matches': high_scoring_matches
        })
        
    except Exception as e:
        logger.error(f"Yüksek skorlu maçlar alınırken hata: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Beklenmeyen bir hata oluştu',
            'details': str(e)
        }), 500

@api_bp.route('/predict/draws', methods=['GET'])
def get_high_draw_matches():
    """
    Berabere bitme ihtimali yüksek maçları getirir
    
    Parametreler:
        days (int): Kaç gün ileriyi kontrol edecek (varsayılan: 7, maksimum: 30)
        min_prob (float): Minimum beraberlik olasılığı (0-1 arası, varsayılan: 0.35 - %35)
    """
    try:
        if not predictor:
            return jsonify({
                'success': False,
                'message': 'Tahmin motoru şu anda kullanılamıyor'
            }), 503
        
        # Parametreleri al
        days_ahead = min(int(request.args.get('days', 7)), 30)  # Maksimum 30 gün
        min_draw_prob = float(request.args.get('min_prob', 0.35))
        
        # Tarih aralığını belirle
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=days_ahead)
        
        # Planlanmış maçları getir
        matches = Match.query.filter(
            Match.match_date.between(start_date, end_date),
            Match.status == 'SCHEDULED',
            Match.home_team_id.isnot(None),
            Match.away_team_id.isnot(None)
        ).all()
        
        if not matches:
            return jsonify({
                'success': True,
                'message': 'Belirtilen tarih aralığında maç bulunamadı',
                'matches': []
            })
        
        draw_matches = []
        
        for match in matches:
            try:
                # Her maç için tahmin yap
                prediction = predictor.predict_match(
                    home_team_id=match.home_team_id,
                    away_team_id=match.away_team_id,
                    match_date=match.match_date
                )
                
                if 'error' in prediction:
                    continue
                    
                draw_prob = prediction.get('match_prediction', {}).get('draw_prob', 0)
                
                # Beraberlik olasılığı eşiği kontrolü
                if draw_prob >= min_draw_prob:
                    draw_matches.append({
                        'match_id': match.id,
                        'home_team': match.home_team.name if match.home_team else 'Bilinmiyor',
                        'away_team': match.away_team.name if match.away_team else 'Bilinmiyor',
                        'match_date': match.match_date.isoformat() if match.match_date else None,
                        'league': match.league.name if hasattr(match, 'league') and match.league else None,
                        'draw_probability': f"{draw_prob*100:.1f}%",
                        'home_win_prob': f"{prediction['match_prediction']['home_win_prob']*100:.1f}%",
                        'away_win_prob': f"{prediction['match_prediction']['away_win_prob']*100:.1f}%",
                        'expected_goals': prediction['expected_goals']
                    })
                    
            except Exception as e:
                logger.error(f"{match.id} ID'li maç için tahmin yapılırken hata: {str(e)}")
                continue
        
        # Beraberlik olasılığına göre sırala (yüksekten düşüğe)
        draw_matches.sort(key=lambda x: float(x['draw_probability'].replace('%', '')), reverse=True)
        
        return jsonify({
            'success': True,
            'count': len(draw_matches),
            'min_draw_probability': f"{min_draw_prob*100:.0f}%",
            'days_ahead': days_ahead,
            'matches': draw_matches
        })
        
    except Exception as e:
        logger.error(f"Berabere maçlar alınırken hata: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Beklenmeyen bir hata oluştu',
            'details': str(e)
        }), 500
