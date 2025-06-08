from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.athlete import Athlete
from app.models.race import Race, RaceResult
from app.models.weather import WeatherData
from app.models.location import Location

bp = Blueprint('api', __name__)

@bp.route('/races', methods=['GET'])
@login_required
def get_races():
    races = Race.query.all()
    return jsonify([{
        'id': race.id,
        'name': race.name,
        'start_date': race.start_date.isoformat(),
        'end_date': race.end_date.isoformat() if race.end_date else None,
        'status': race.status,
        'race_type': race.race_type
    } for race in races])

@bp.route('/athlete/profile', methods=['GET'])
@login_required
def get_athlete_profile():
    athlete = Athlete.query.filter_by(user_id=current_user.id).first()
    if not athlete:
        return jsonify({'error': 'Athlete profile not found'}), 404
        
    return jsonify({
        'id': athlete.id,
        'first_name': athlete.first_name,
        'last_name': athlete.last_name,
        'experience_level': athlete.experience_level,
        'weight': athlete.weight,
        'height': athlete.height,
        'dominant_side': athlete.dominant_side
    })

@bp.route('/weather/<int:location_id>', methods=['GET'])
@login_required
def get_weather(location_id):
    weather = WeatherData.query.filter_by(location_id=location_id)\
        .order_by(WeatherData.timestamp.desc()).first()
    
    if not weather:
        return jsonify({'error': 'Weather data not found'}), 404
        
    return jsonify({
        'temperature': weather.temperature,
        'wind_speed': weather.wind_speed,
        'wind_direction': weather.wind_direction,
        'wind_gust': weather.wind_gust,
        'wave_height': weather.wave_height,
        'timestamp': weather.timestamp.isoformat()
    })
