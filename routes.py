from flask import render_template, request, jsonify, flash, redirect, url_for, session
from flask_login import current_user, login_required
from app import app, db
from models import Team, Match, Player, Prediction, TeamStatistics, Injury, User, UserPrediction
from ai_models import StatisticalPredictor, LSTMPredictor, CNNPredictor, BayesianPredictor
from database_utils import initialize_sample_data, get_team_recent_form, get_head_to_head_stats
from football_api import FootballDataAPI
from leagues_manager import LeaguesManager
from football_auth import make_football_blueprint, require_login
import json
from datetime import datetime, timedelta

# Register auth blueprint
app.register_blueprint(make_football_blueprint(), url_prefix="/auth")

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def index():
    """Main page for match prediction"""
    # Get leagues and teams
    leagues_manager = LeaguesManager()
    available_leagues = leagues_manager.get_all_leagues()
    
    # Get teams from database, grouped by league
    teams_by_league = {}
    for league in available_leagues:
        teams = Team.query.filter_by(league=league).order_by(Team.name).all()
        if teams:
            teams_by_league[league] = teams
    
    # If no teams in database, show all teams without league filtering
    if not teams_by_league:
        all_teams = Team.query.order_by(Team.name).all()
        teams_by_league = {'All Teams': all_teams}
    
    return render_template('index.html', 
                         teams_by_league=teams_by_league, 
                         available_leagues=available_leagues,
                         user=current_user)

@app.route('/predict', methods=['POST'])
@require_login
def predict_match():
    """Generate predictions for a match using all 4 algorithms"""
    try:
        home_team_id = request.form.get('home_team_id', type=int)
        away_team_id = request.form.get('away_team_id', type=int)
        
        if not home_team_id or not away_team_id:
            flash('Please select both teams', 'error')
            return redirect(url_for('index'))
        
        if home_team_id == away_team_id:
            flash('Please select different teams', 'error')
            return redirect(url_for('index'))
        
        home_team = Team.query.get_or_404(home_team_id)
        away_team = Team.query.get_or_404(away_team_id)
        
        # Create a new match for prediction
        match = Match(
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            match_date=datetime.now() + timedelta(days=1),
            season='2024-25',
            competition='Prediction',
            is_played=False
        )
        db.session.add(match)
        db.session.commit()
        
        # Initialize predictors
        statistical_predictor = StatisticalPredictor()
        lstm_predictor = LSTMPredictor()
        cnn_predictor = CNNPredictor()
        bayesian_predictor = BayesianPredictor()
        
        # Generate predictions
        predictions = {}
        
        # Statistical Prediction
        stat_pred = statistical_predictor.predict(home_team, away_team)
        stat_prediction = Prediction(
            match_id=match.id,
            algorithm='statistical',
            home_goals_prediction=stat_pred['home_goals'],
            away_goals_prediction=stat_pred['away_goals'],
            home_goals_first_half=stat_pred['home_goals_first_half'],
            away_goals_first_half=stat_pred['away_goals_first_half'],
            home_win_probability=stat_pred['home_win_prob'],
            draw_probability=stat_pred['draw_prob'],
            away_win_probability=stat_pred['away_win_prob'],
            confidence_score=stat_pred['confidence'],
            prediction_details=json.dumps(stat_pred['details'])
        )
        predictions['statistical'] = stat_prediction
        
        # LSTM Prediction
        lstm_pred = lstm_predictor.predict(home_team, away_team)
        lstm_prediction = Prediction(
            match_id=match.id,
            algorithm='lstm',
            home_goals_prediction=lstm_pred['home_goals'],
            away_goals_prediction=lstm_pred['away_goals'],
            home_goals_first_half=lstm_pred['home_goals_first_half'],
            away_goals_first_half=lstm_pred['away_goals_first_half'],
            home_win_probability=lstm_pred['home_win_prob'],
            draw_probability=lstm_pred['draw_prob'],
            away_win_probability=lstm_pred['away_win_prob'],
            confidence_score=lstm_pred['confidence'],
            prediction_details=json.dumps(lstm_pred['details'])
        )
        predictions['lstm'] = lstm_prediction
        
        # CNN Prediction
        cnn_pred = cnn_predictor.predict(home_team, away_team)
        cnn_prediction = Prediction(
            match_id=match.id,
            algorithm='cnn',
            home_goals_prediction=cnn_pred['home_goals'],
            away_goals_prediction=cnn_pred['away_goals'],
            home_goals_first_half=cnn_pred['home_goals_first_half'],
            away_goals_first_half=cnn_pred['away_goals_first_half'],
            home_win_probability=cnn_pred['home_win_prob'],
            draw_probability=cnn_pred['draw_prob'],
            away_win_probability=cnn_pred['away_win_prob'],
            confidence_score=cnn_pred['confidence'],
            prediction_details=json.dumps(cnn_pred['details'])
        )
        predictions['cnn'] = cnn_prediction
        
        # Bayesian Prediction
        bayesian_pred = bayesian_predictor.predict(home_team, away_team)
        bayesian_prediction = Prediction(
            match_id=match.id,
            algorithm='bayesian',
            home_goals_prediction=bayesian_pred['home_goals'],
            away_goals_prediction=bayesian_pred['away_goals'],
            home_goals_first_half=bayesian_pred['home_goals_first_half'],
            away_goals_first_half=bayesian_pred['away_goals_first_half'],
            home_win_probability=bayesian_pred['home_win_prob'],
            draw_probability=bayesian_pred['draw_prob'],
            away_win_probability=bayesian_pred['away_win_prob'],
            confidence_score=bayesian_pred['confidence'],
            prediction_details=json.dumps(bayesian_pred['details'])
        )
        predictions['bayesian'] = bayesian_prediction
        
        # Save all predictions
        for prediction in predictions.values():
            db.session.add(prediction)
        db.session.commit()
        
        # Get additional data for display
        home_form = get_team_recent_form(home_team_id)
        away_form = get_team_recent_form(away_team_id)
        head_to_head = get_head_to_head_stats(home_team_id, away_team_id)
        
        return render_template('prediction.html', 
                             match=match,
                             home_team=home_team,
                             away_team=away_team,
                             predictions=predictions,
                             home_form=home_form,
                             away_form=away_form,
                             head_to_head=head_to_head)
        
    except Exception as e:
        app.logger.error(f"Error in predict_match: {str(e)}")
        flash('An error occurred while generating predictions', 'error')
        return redirect(url_for('index'))

@app.route('/team/<int:team_id>')
def team_stats(team_id):
    """Display detailed team statistics"""
    team = Team.query.get_or_404(team_id)
    
    # Get team statistics
    current_season = '2024-25'
    team_stats = TeamStatistics.query.filter_by(team_id=team_id, season=current_season).first()
    
    # Get recent matches
    recent_matches = Match.query.filter(
        (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
    ).filter(Match.is_played == True).order_by(Match.match_date.desc()).limit(10).all()
    
    # Get players
    players = Player.query.filter_by(team_id=team_id).order_by(Player.rating.desc()).all()
    
    # Get injuries
    active_injuries = Injury.query.join(Player).filter(
        Player.team_id == team_id,
        Injury.is_active == True
    ).all()
    
    return render_template('team_stats.html',
                         team=team,
                         team_stats=team_stats,
                         recent_matches=recent_matches,
                         players=players,
                         active_injuries=active_injuries)

@app.route('/initialize_data')
def initialize_data():
    """Initialize sample data for testing"""
    try:
        initialize_sample_data()
        flash('Sample data initialized successfully!', 'success')
    except Exception as e:
        app.logger.error(f"Error initializing data: {str(e)}")
        flash('Error initializing data', 'error')
    
    return redirect(url_for('index'))

@app.route('/update_real_data')
def update_real_data():
    """Update data from real football API for all leagues"""
    leagues_manager = LeaguesManager()
    
    try:
        # Update all leagues
        success, count = leagues_manager.update_all_leagues()
        
        if success:
            flash(f'Successfully updated {count} teams from all global leagues!', 'success')
        else:
            flash('Failed to update from API. Please provide API key for real data.', 'warning')
            
    except Exception as e:
        flash(f'Error updating data: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/league/<league_name>')
def league_teams(league_name):
    """Display teams from a specific league"""
    teams = Team.query.filter_by(league=league_name).order_by(Team.name).all()
    
    return render_template('league_teams.html', 
                         teams=teams, 
                         league_name=league_name,
                         user=current_user)

@app.route('/leagues-info')
def leagues_info():
    """Display information about all supported leagues"""
    leagues_manager = LeaguesManager()
    league_info = leagues_manager.get_league_info()
    
    return render_template('leagues_info.html', 
                         league_info=league_info,
                         user=current_user)

@app.route('/my-predictions')
@require_login
def my_predictions():
    """Display user's prediction history"""
    user_predictions = UserPrediction.query.filter_by(user_id=current_user.id)\
                                          .join(Prediction)\
                                          .join(Match)\
                                          .order_by(UserPrediction.created_at.desc())\
                                          .limit(50).all()
    
    return render_template('my_predictions.html', 
                         predictions=user_predictions,
                         user=current_user)

@app.route('/add-match', methods=['GET', 'POST'])
@require_login
def add_match():
    """Add a real fixture match manually"""
    if request.method == 'POST':
        try:
            home_team_id = request.form.get('home_team_id', type=int)
            away_team_id = request.form.get('away_team_id', type=int)
            match_date_str = request.form.get('match_date')
            competition = request.form.get('competition', 'League Match')
            
            if not home_team_id or not away_team_id or not match_date_str:
                flash('Lütfen tüm alanları doldurun', 'error')
                return redirect(url_for('add_match'))
            
            if home_team_id == away_team_id:
                flash('Lütfen farklı takımlar seçin', 'error')
                return redirect(url_for('add_match'))
            
            # Parse match date
            match_date = datetime.strptime(match_date_str, '%Y-%m-%dT%H:%M')
            
            # Check if match already exists
            existing_match = Match.query.filter_by(
                home_team_id=home_team_id,
                away_team_id=away_team_id,
                match_date=match_date
            ).first()
            
            if existing_match:
                flash('Bu maç zaten mevcut', 'warning')
                return redirect(url_for('add_match'))
            
            # Create new match
            new_match = Match(
                home_team_id=home_team_id,
                away_team_id=away_team_id,
                match_date=match_date,
                season='2024-25',
                competition=competition,
                is_played=False
            )
            
            db.session.add(new_match)
            db.session.commit()
            
            flash(f'Maç başarıyla eklendi: {new_match.home_team.name} vs {new_match.away_team.name}', 'success')
            return redirect(url_for('fixtures'))
            
        except ValueError:
            flash('Geçersiz tarih formatı', 'error')
            return redirect(url_for('add_match'))
        except Exception as e:
            flash(f'Hata: {str(e)}', 'error')
            return redirect(url_for('add_match'))
    
    # GET request - show form
    leagues_manager = LeaguesManager()
    available_leagues = leagues_manager.get_all_leagues()
    
    teams_by_league = {}
    for league in available_leagues:
        teams = Team.query.filter_by(league=league).order_by(Team.name).all()
        if teams:
            teams_by_league[league] = teams
    
    if not teams_by_league:
        all_teams = Team.query.order_by(Team.name).all()
        teams_by_league = {'Tüm Takımlar': all_teams}
    
    return render_template('add_match.html', 
                         teams_by_league=teams_by_league,
                         user=current_user)

@app.route('/fixtures')
def fixtures():
    """Display upcoming and recent matches"""
    upcoming_matches = Match.query.filter(
        Match.is_played == False,
        Match.match_date > datetime.utcnow()
    ).order_by(Match.match_date).limit(20).all()
    
    recent_matches = Match.query.filter(
        Match.is_played == True
    ).order_by(Match.match_date.desc()).limit(10).all()
    
    return render_template('fixtures.html', 
                         upcoming_matches=upcoming_matches,
                         recent_matches=recent_matches,
                         user=current_user)

@app.route('/api_status')
def api_status():
    """Check API connection status"""
    try:
        api = FootballDataAPI()
        status_info = api.get_api_info()
        return jsonify(status_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/team/<int:team_id>/form')
def api_team_form(team_id):
    """API endpoint for team form data"""
    try:
        form_data = get_team_recent_form(team_id, limit=5)
        return jsonify(form_data)
    except Exception as e:
        app.logger.error(f"Error getting team form: {str(e)}")
        return jsonify({'error': 'Failed to get team form'}), 500

@app.route('/api/teams/<int:home_id>/<int:away_id>/h2h')
def api_head_to_head(home_id, away_id):
    """API endpoint for head-to-head statistics"""
    try:
        h2h_data = get_head_to_head_stats(home_id, away_id)
        return jsonify(h2h_data)
    except Exception as e:
        app.logger.error(f"Error getting H2H stats: {str(e)}")
        return jsonify({'error': 'Failed to get head-to-head stats'}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('base.html', error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html', error_message="Internal server error"), 500
