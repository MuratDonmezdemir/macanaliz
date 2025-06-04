from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from models import db, Team, Match, Prediction
from ai_predictor import AIPredictor
from datetime import datetime, timedelta
import os
from sqlalchemy import or_

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///football.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with app
db.init_app(app)

# Initialize AI predictor
predictor = AIPredictor(db.session)

# Create database tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    """Main page with upcoming matches and predictions"""
    # Get upcoming matches (next 7 days)
    today = datetime.now()
    next_week = today + timedelta(days=7)
    
    upcoming_matches = Match.query.filter(
        Match.match_date.between(today, next_week),
        or_(Match.status == 'Scheduled', Match.status == 'Live')
    ).order_by(Match.match_date.asc()).all()
    
    matches_with_predictions = []
    for match in upcoming_matches:
        # Get match prediction
        prediction = predictor.predict(
            match.home_team_id,
            match.away_team_id,
            match.match_date
        )
        
        # Get goal prediction
        goals_prediction = predictor.predict_goals(
            match.home_team_id,
            match.away_team_id,
            match.match_date
        )
        
        matches_with_predictions.append({
            'match': match,
            'prediction': prediction,
            'goals_prediction': goals_prediction
        })
    
    return render_template('index.html', 
                         matches=matches_with_predictions,
                         today=today)

@app.route('/teams')
def teams():
    """Get all teams"""
    teams = Team.query.all()
    return {'teams': [team.name for team in teams]}

@app.route('/api/predict/<int:match_id>', methods=['GET'])
def api_predict_match(match_id):
    """API endpoint for match prediction"""
    match = Match.query.get_or_404(match_id)
    
    # Get match prediction
    prediction = predictor.predict(
        match.home_team_id,
        match.away_team_id,
        match.match_date
    )
    
    # Get goal prediction
    goals_prediction = predictor.predict_goals(
        match.home_team_id,
        match.away_team_id,
        match.match_date
    )
    
    return jsonify({
        'match_id': match_id,
        'home_team': match.home_team.name,
        'away_team': match.away_team.name,
        'match_date': match.match_date.isoformat(),
        'competition': match.competition,
        'prediction': prediction,
        'goals_prediction': goals_prediction
    })

@app.route('/api/train', methods=['POST'])
def train_model():
    """API endpoint to train the prediction model"""
    try:
        # Get training parameters from request
        data = request.get_json() or {}
        days_back = int(data.get('days_back', 365 * 2))  # Default: 2 years
        
        # Get matches for training
        training_date = datetime.now() - timedelta(days=days_back)
        matches = Match.query.filter(
            Match.match_date >= training_date,
            Match.status == 'Finished',
            Match.home_goals.isnot(None),
            Match.away_goals.isnot(None)
        ).all()
        
        if not matches:
            return jsonify({
                'status': 'error',
                'message': 'No training data available'
            }), 400
        
        # Train the model
        accuracy = predictor.train(matches)
        
        return jsonify({
            'status': 'success',
            'message': 'Model trained successfully',
            'matches_used': len(matches),
            'accuracy': accuracy
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/teams/<int:team_id>/stats')
def team_stats(team_id):
    """Get team statistics"""
    team = Team.query.get_or_404(team_id)
    
    # Get team form
    home_form = predictor.get_team_form(team_id, datetime.now(), is_home=True)
    away_form = predictor.get_team_form(team_id, datetime.now(), is_home=False)
    
    # Get team stats
    home_stats = predictor.get_team_stats(team_id, datetime.now(), is_home=True)
    away_stats = predictor.get_team_stats(team_id, datetime.now(), is_home=False)
    
    return jsonify({
        'team_id': team.id,
        'team_name': team.name,
        'home_form': home_form,
        'away_form': away_form,
        'home_stats': home_stats,
        'away_stats': away_stats
    })

@app.route('/dashboard')
def dashboard():
    """Admin dashboard for model management"""
    # Get model info
    model_info = {
        'full_time': {
            'version': '1.0',
            'last_trained': 'N/A',
            'accuracy': 'N/A'
        },
        'goals': {
            'version': '1.0',
            'last_trained': 'N/A',
            'accuracy': 'N/A'
        }
    }
    
    # Get recent predictions
    recent_predictions = Prediction.query.order_by(
        Prediction.created_at.desc()
    ).limit(10).all()
    
    # Get upcoming matches
    upcoming_matches = Match.query.filter(
        Match.match_date >= datetime.now(),
        or_(Match.status == 'Scheduled', Match.status == 'Live')
    ).order_by(Match.match_date.asc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         model_info=model_info,
                         recent_predictions=recent_predictions,
                         upcoming_matches=upcoming_matches)

if __name__ == '__main__':
    print("Starting Football Analysis App...")
    print("Visit http://127.0.0.1:8000 in your browser")
    app.run(host='0.0.0.0', port=8000, debug=True)
