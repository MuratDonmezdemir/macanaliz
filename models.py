from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin

# User Authentication Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    profile_image_url = db.Column(db.String, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # User preferences
    favorite_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    prediction_count = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime)

    # Relationships
    predictions = relationship('UserPrediction', back_populates='user')
    favorite_team = relationship('Team', foreign_keys=[favorite_team_id])

class OAuth(OAuthConsumerMixin, db.Model):
    __tablename__ = 'oauth'
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    browser_session_key = db.Column(db.String, nullable=False)
    user = relationship(User)

    __table_args__ = (UniqueConstraint(
        'user_id',
        'browser_session_key', 
        'provider',
        name='uq_user_browser_session_key_provider',
    ),)

class UserPrediction(db.Model):
    __tablename__ = 'user_predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    prediction_id = db.Column(db.Integer, db.ForeignKey('predictions.id'), nullable=False)
    
    # User interaction data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_favorite = db.Column(db.Boolean, default=False)
    user_rating = db.Column(db.Integer)  # 1-5 stars
    notes = db.Column(db.Text)
    
    # Relationships
    user = relationship('User', back_populates='predictions')
    prediction = relationship('Prediction')

class Team(db.Model):
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    country = db.Column(db.String(50), nullable=False)
    league = db.Column(db.String(100), nullable=False)
    founded = db.Column(db.Integer)
    stadium = db.Column(db.String(100))
    
    # Team Statistics
    attack_strength = db.Column(db.Float, default=50.0)
    defense_strength = db.Column(db.Float, default=50.0)
    home_advantage = db.Column(db.Float, default=5.0)
    current_form = db.Column(db.Float, default=50.0)
    
    # Relationships
    home_matches = relationship('Match', foreign_keys='Match.home_team_id', back_populates='home_team')
    away_matches = relationship('Match', foreign_keys='Match.away_team_id', back_populates='away_team')
    players = relationship('Player', back_populates='team')
    
    def __repr__(self):
        return f'<Team {self.name}>'

class Player(db.Model):
    __tablename__ = 'players'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    
    # Player Statistics
    rating = db.Column(db.Float, default=70.0)
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    minutes_played = db.Column(db.Integer, default=0)
    is_injured = db.Column(db.Boolean, default=False)
    injury_severity = db.Column(db.Float, default=0.0)  # 0-100 scale
    
    # Relationships
    team = relationship('Team', back_populates='players')
    injuries = relationship('Injury', back_populates='player')
    
    def __repr__(self):
        return f'<Player {self.name}>'

class Match(db.Model):
    __tablename__ = 'matches'
    
    id = db.Column(db.Integer, primary_key=True)
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    
    # Match Details
    match_date = db.Column(db.DateTime, nullable=False)
    season = db.Column(db.String(20), nullable=False)
    competition = db.Column(db.String(100), nullable=False)
    
    # Results
    home_goals = db.Column(db.Integer)
    away_goals = db.Column(db.Integer)
    home_goals_first_half = db.Column(db.Integer)
    away_goals_first_half = db.Column(db.Integer)
    
    # Match Statistics
    home_shots = db.Column(db.Integer, default=0)
    away_shots = db.Column(db.Integer, default=0)
    home_shots_on_target = db.Column(db.Integer, default=0)
    away_shots_on_target = db.Column(db.Integer, default=0)
    home_possession = db.Column(db.Float, default=50.0)
    away_possession = db.Column(db.Float, default=50.0)
    home_pass_accuracy = db.Column(db.Float, default=80.0)
    away_pass_accuracy = db.Column(db.Float, default=80.0)
    
    # Match Status
    is_played = db.Column(db.Boolean, default=False)
    
    # Relationships
    home_team = relationship('Team', foreign_keys=[home_team_id], back_populates='home_matches')
    away_team = relationship('Team', foreign_keys=[away_team_id], back_populates='away_matches')
    predictions = relationship('Prediction', back_populates='match')
    
    def __repr__(self):
        return f'<Match {self.home_team.name} vs {self.away_team.name}>'

class Injury(db.Model):
    __tablename__ = 'injuries'
    
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    injury_type = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.Float, nullable=False)  # 0-100 scale
    start_date = db.Column(db.DateTime, nullable=False)
    expected_return_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    player = relationship('Player', back_populates='injuries')
    
    def __repr__(self):
        return f'<Injury {self.player.name} - {self.injury_type}>'

class Prediction(db.Model):
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    algorithm = db.Column(db.String(50), nullable=False)  # statistical, lstm, cnn, bayesian
    
    # Predictions
    home_goals_prediction = db.Column(db.Float, nullable=False)
    away_goals_prediction = db.Column(db.Float, nullable=False)
    home_goals_first_half = db.Column(db.Float, nullable=False)
    away_goals_first_half = db.Column(db.Float, nullable=False)
    
    # Probabilities
    home_win_probability = db.Column(db.Float, nullable=False)
    draw_probability = db.Column(db.Float, nullable=False)
    away_win_probability = db.Column(db.Float, nullable=False)
    
    # Confidence and Details
    confidence_score = db.Column(db.Float, nullable=False)  # 0-100 scale
    prediction_details = db.Column(db.Text)  # JSON string with additional details
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    match = relationship('Match', back_populates='predictions')
    
    def __repr__(self):
        return f'<Prediction {self.algorithm} for Match {self.match_id}>'

class TeamStatistics(db.Model):
    __tablename__ = 'team_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    season = db.Column(db.String(20), nullable=False)
    
    # Overall Statistics
    matches_played = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    goals_for = db.Column(db.Integer, default=0)
    goals_against = db.Column(db.Integer, default=0)
    
    # Home Statistics
    home_matches = db.Column(db.Integer, default=0)
    home_wins = db.Column(db.Integer, default=0)
    home_draws = db.Column(db.Integer, default=0)
    home_losses = db.Column(db.Integer, default=0)
    home_goals_for = db.Column(db.Integer, default=0)
    home_goals_against = db.Column(db.Integer, default=0)
    
    # Away Statistics
    away_matches = db.Column(db.Integer, default=0)
    away_wins = db.Column(db.Integer, default=0)
    away_draws = db.Column(db.Integer, default=0)
    away_losses = db.Column(db.Integer, default=0)
    away_goals_for = db.Column(db.Integer, default=0)
    away_goals_against = db.Column(db.Integer, default=0)
    
    # Advanced Metrics
    average_goals_per_match = db.Column(db.Float, default=0.0)
    average_goals_conceded = db.Column(db.Float, default=0.0)
    clean_sheets = db.Column(db.Integer, default=0)
    
    # Relationships
    team = relationship('Team')
    
    def __repr__(self):
        return f'<TeamStatistics {self.team.name} - {self.season}>'
