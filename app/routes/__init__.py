from flask import Blueprint, jsonify
from app.models import db, Country, League, Team, Match

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return jsonify({
        'message': 'Welcome to the Football Prediction API',
        'endpoints': {
            'leagues': '/api/leagues',
            'teams': '/api/teams',
            'matches': '/api/matches'
        }
    })

@main_bp.route('/api/leagues')
def get_leagues():
    leagues = League.query.all()
    return jsonify([{
        'id': league.id,
        'name': league.name,
        'country': league.country.name if league.country else None
    } for league in leagues])

@main_bp.route('/api/teams')
def get_teams():
    teams = Team.query.all()
    return jsonify([{
        'id': team.id,
        'name': team.name,
        'league': team.league.name if team.league else None,
        'country': team.country.name if team.country else None
    } for team in teams])

@main_bp.route('/api/matches')
def get_matches():
    matches = Match.query.order_by(Match.match_date.desc()).limit(10).all()
    return jsonify([{
        'id': match.id,
        'home_team': match.home_team.name,
        'away_team': match.away_team.name,
        'date': match.match_date.isoformat(),
        'score': f"{match.home_goals or 0} - {match.away_goals or 0}",
        'status': match.status
    } for match in matches])
