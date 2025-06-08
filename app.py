import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from sqlalchemy import or_

# Initialize Flask app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
    f'sqlite:///{os.path.join(basedir, "app.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with app
db = SQLAlchemy(app)

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
    from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
from dotenv import load_dotenv

# Uygulama ve veritabanı başlatma
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# Yapılandırma
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gizli-anahtar-buraya')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
    f'sqlite:///{os.path.join(basedir, "app.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Modeller
class Country(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(3), unique=True, nullable=False)
    flag = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# API Rotaları
@app.route('/')
def index():
    return jsonify({"message": "Football Match Prediction API"})

@app.route('/teams')
def teams():
    """Tüm takımları getir"""
    teams = Team.query.all()
    return jsonify([{"id": team.id, "name": team.name} for team in teams])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Veritabanı tablolarını oluştur
    app.run(debug=True)from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
from dotenv import load_dotenv

# Uygulama ve veritabanı başlatma
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# Yapılandırma
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gizli-anahtar-buraya')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
    f'sqlite:///{os.path.join(basedir, "app.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Modeller
class Country(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(3), unique=True, nullable=False)
    flag = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# API Rotaları
@app.route('/')
def index():
    return jsonify({"message": "Football Match Prediction API"})

@app.route('/teams')
def teams():
    """Tüm takımları getir"""
    teams = Team.query.all()
    return jsonify([{"id": team.id, "name": team.name} for team in teams])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Veritabanı tablolarını oluştur
    app.run(debug=True)git add .
git commit -m "Yapılan değişikliklerin açıklaması"
git push# Initialize Flask app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
    f'sqlite:///{os.path.join(basedir, "app.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with app
db = SQLAlchemy(app)

# Initialize AI predictor
predictor = AIPredictor(db.session)

# Create database tables
with app.app_context():
    db.create_all()# Klasörleri oluştur
mkdir -p app/models app/api app/services
# Boş dosyaları oluştur
# Ana sayfayı test et
curl http://127.0.0.1:5000/

# Takımları listele (şu an boş olacak)
curl http://127.0.0.1:5000/teamsfrom flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
from dotenv import load_dotenv

# Uygulama ve veritabanı başlatma
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# Yapılandırma
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gizli-anahtar-buraya')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
    f'sqlite:///{os.path.join(basedir, "app.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Modeller
class Country(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(3), unique=True, nullable=False)
    flag = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# API Rotaları
@app.route('/')
def index():
    return jsonify({"message": "Football Match Prediction API"})

@app.route('/teams')
def teams():
    """Tüm takımları getir"""
    teams = Team.query.all()
    return jsonify([{"id": team.id, "name": team.name} for team in teams])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Veritabanı tablolarını oluştur
    app.run(debug=True)@app.route('/api/teams', methods=['GET'])
def teams():
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
                         from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Country(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(3), unique=True, nullable=False)
    flag = db.Column(db.String(255))

    # İlişkiler
    leagues = db.relationship('League', backref='country', lazy=True)
    teams = db.relationship('Team', backref='country', lazy=True)

class League(db.Model):
    __tablename__ = 'leagues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    level = db.Column(db.Integer)
    logo = db.Column(db.String(255))
    current_season = db.Column(db.String(10))

    # İlişkiler
    teams = db.relationship('Team', backref='league', lazy=True)
    matches = db.relationship('Match', backref='league', lazy=True)

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    founded = db.Column(db.Integer)
    stadium = db.Column(db.String(100))
    logo = db.Column(db.String(255))
    attack_rating = db.Column(db.Float, default=50.0)
    defense_rating = db.Column(db.Float, default=50.0)
    home_advantage = db.Column(db.Float, default=1.1)
    current_form = db.Column(db.Float, default=0.0)

    # İlişkiler
    home_matches = db.relationship('Match', foreign_keys='Match.home_team_id', backref='home_team', lazy=True)
    away_matches = db.relationship('Match', foreign_keys='Match.away_team_id', backref='away_team', lazy=True)
import os
from app import create_app, db
from app.models import Country, League, Team, Match

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Country': Country,
        'League': League,
        'Team': Team,
        'Match': Match
    }

if __name__ == '__main__':
    app.run(debug=True)import os
from app import create_app, db
from app.models import Country, League, Team, Match

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Country': Country,
        'League': League,
        'Team': Team,
        'Match': Match
    }

if __name__ == '__main__':
    app.run(debug=True)from flask import jsonify, request
from app import db
from app.models import Team, Match, League
from app.services import PredictionService
from . import bp

@bp.route('/teams', methods=['GET'])
def get_teams():
    teams = Team.query.all()
    return jsonify([{
        'id': team.id,
        'name': team.name,
        'league_id': team.league_id
    } for team in teams])

@bp.route('/matches', methods=['GET'])
def get_matches():
    league_id = request.args.get('league_id', type=int)
    status = request.args.get('status', 'Scheduled')

    query = Match.query
    if league_id:
        query = query.filter_by(league_id=league_id)
    if status:
        query = query.filter_by(status=status)

    matches = query.order_by(Match.match_date).limit(100).all()
    return jsonify([match.to_dict() for match in matches])

@bp.route('/predict/<int:match_id>', methods=['GET'])
def predict_match(match_id):
    match = Match.query.get_or_404(match_id)
    prediction_service = PredictionService()

    # Örnek özellik vektörü (gerçek uygulamada DataService'den alınacak)
    features = [
        match.home_team.attack_rating,
        match.home_team.defense_rating,
        match.away_team.attack_rating,
        match.away_team.defense_rating,
        match.home_team.home_advantage,
        match.home_team.current_form,
        match.away_team.current_form
    ]

    prediction = prediction_service.predict(features)

    # Tahminleri kaydet
    match.prediction_home_win = prediction['home_win']
    match.prediction_draw = prediction['draw']
    match.prediction_away_win = prediction['away_win']
    db.session.commit()

    return jsonify({
        'match_id': match.id,
        'home_team': match.home_team.name,
        'away_team': match.away_team.name,
        'predictions': prediction
    })from flask import jsonify, request
from app import db
from app.models import Team, Match, League
from app.services import PredictionService
from . import bp

@bp.route('/teams', methods=['GET'])
def get_teams():
    teams = Team.query.all()
    return jsonify([{
        'id': team.id,
        'name': team.name,
        'league_id': team.league_id
    } for team in teams])

@bp.route('/matches', methods=['GET'])
def get_matches():
    league_id = request.args.get('league_id', type=int)
    status = request.args.get('status', 'Scheduled')

    query = Match.query
    if league_id:
        query = query.filter_by(league_id=league_id)
    if status:
        query = query.filter_by(status=status)

    matches = query.order_by(Match.match_date).limit(100).all()
    return jsonify([match.to_dict() for match in matches])

@bp.route('/predict/<int:match_id>', methods=['GET'])
def predict_match(match_id):
    match = Match.query.get_or_404(match_id)
    prediction_service = PredictionService()

    # Örnek özellik vektörü (gerçek uygulamada DataService'den alınacak)
    features = [
        match.home_team.attack_rating,
        match.home_team.defense_rating,
        match.away_team.attack_rating,
        match.away_team.defense_rating,
        match.home_team.home_advantage,
        match.home_team.current_form,
        match.away_team.current_form
    ]

    prediction = prediction_service.predict(features)

    # Tahminleri kaydet
    match.prediction_home_win = prediction['home_win']
    match.prediction_draw = prediction['draw']
    match.prediction_away_win = prediction['away_win']
    db.session.commit()

    return jsonify({
        'match_id': match.id,
        'home_team': match.home_team.name,
        'away_team': match.away_team.name,
        'predictions': prediction
    })from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import routesfrom flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import routesimport numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
from joblib import dump, load
import os
from app import app
from .data_service import DataService

class PredictionService:
    def __init__(self):
        self.model_path = os.path.join(app.config['MODEL_PATH'], 'xgb_model.joblib')
        self.scaler_path = os.path.join(app.config['MODEL_PATH'], 'scaler.joblib')
        self.model = None
        self.scaler = None
        self.load_model()

    def load_model(self):
        """Modeli yükler veya yeni bir model oluşturur"""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = load(self.model_path)
            self.scaler = load(self.scaler_path)
        else:
            self.model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
            self.scaler = StandardScaler()

    def train(self, X, y):
        """Modeli eğitir"""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)

        # Modeli kaydet
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        dump(self.model, self.model_path)
        dump(self.scaler, self.scaler_path)

    def predict(self, features):
        """Tahmin yapar"""
        if not self.model or not self.scaler:
            raise Exception("Model yüklenemedi veya oluşturulamadı")

        features_scaled = self.scaler.transform([features])
        prediction = self.model.predict_proba(features_scaled)[0]

        return {
            'home_win': float(prediction[0]),
            'draw': float(prediction[1]),
            'away_win': float(prediction[2])
        }import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
from joblib import dump, load
import os
from app import app
from .data_service import DataService

class PredictionService:
    def __init__(self):
        self.model_path = os.path.join(app.config['MODEL_PATH'], 'xgb_model.joblib')
        self.scaler_path = os.path.join(app.config['MODEL_PATH'], 'scaler.joblib')
        self.model = None
        self.scaler = None
        self.load_model()

    def load_model(self):
        """Modeli yükler veya yeni bir model oluşturur"""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = load(self.model_path)
            self.scaler = load(self.scaler_path)
        else:
            self.model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
            self.scaler = StandardScaler()

    def train(self, X, y):
        """Modeli eğitir"""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)

        # Modeli kaydet
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        dump(self.model, self.model_path)
        dump(self.scaler, self.scaler_path)

    def predict(self, features):
        """Tahmin yapar"""
        if not self.model or not self.scaler:
            raise Exception("Model yüklenemedi veya oluşturulamadı")

        features_scaled = self.scaler.transform([features])
        prediction = self.model.predict_proba(features_scaled)[0]

        return {
            'home_win': float(prediction[0]),
            'draw': float(prediction[1]),
            'away_win': float(prediction[2])
        }from datetime import datetime, timedelta
from app import db
from app.models import Match, Team

class DataService:
    @staticmethod
    def get_team_recent_matches(team_id, limit=5, before_date=None):
        """Takımın son maçlarını getirir"""
        if before_date is None:
            before_date = datetime.utcnow()

        return Match.query.filter(
            ((Match.home_team_id == team_id) | (Match.away_team_id == team_id)) &
            (Match.status == 'Finished') &
            (Match.match_date < before_date)
        ).order_by(Match.match_date.desc()).limit(limit).all()

    @staticmethod
    def calculate_team_form(matches, team_id):
        """Takımın son 5 maçındaki formunu hesaplar (puan ortalaması)"""
        if not matches:
            return 0.0

        total_points = 0
        for match in matches:
            if match.home_team_id == team_id:
                if match.home_goals > match.away_goals:
                    total_points += 3
                elif match.home_goals == match.away_goals:
                    total_points += 1
            else:
                if match.away_goals > match.home_goals:
                    total_points += 3
                elif match.away_goals == match.home_goals:
                    total_points += 1

        return total_points / (len(matches) * 3)  # 0-1 arasında normalize edilmiş değerfrom datetime import datetime, timedelta
from app import db
from app.models import Match, Team

class DataService:
    @staticmethod
    def get_team_recent_matches(team_id, limit=5, before_date=None):
        """Takımın son maçlarını getirir"""
        if before_date is None:
            before_date = datetime.utcnow()

        return Match.query.filter(
            ((Match.home_team_id == team_id) | (Match.away_team_id == team_id)) &
            (Match.status == 'Finished') &
            (Match.match_date < before_date)
        ).order_by(Match.match_date.desc()).limit(limit).all()

    @staticmethod
    def calculate_team_form(matches, team_id):
        """Takımın son 5 maçındaki formunu hesaplar (puan ortalaması)"""
        if not matches:
            return 0.0

        total_points = 0
        for match in matches:
            if match.home_team_id == team_id:
                if match.home_goals > match.away_goals:
                    total_points += 3
                elif match.home_goals == match.away_goals:
                    total_points += 1
            else:
                if match.away_goals > match.home_goals:
                    total_points += 3
                elif match.away_goals == match.home_goals:
                    total_points += 1

        return total_points / (len(matches) * 3)  # 0-1 arasında normalize edilmiş değerfrom datetime import datetime, timedelta
from app import db
from app.models import Match, Team

class DataService:
    @staticmethod
    def get_team_recent_matches(team_id, limit=5, before_date=None):
        """Takımın son maçlarını getirir"""
        if before_date is None:
            before_date = datetime.utcnow()

        return Match.query.filter(
            ((Match.home_team_id == team_id) | (Match.away_team_id == team_id)) &
            (Match.status == 'Finished') &
            (Match.match_date < before_date)
        ).order_by(Match.match_date.desc()).limit(limit).all()

    @staticmethod
    def calculate_team_form(matches, team_id):
        """Takımın son 5 maçındaki formunu hesaplar (puan ortalaması)"""
        if not matches:
            return 0.0

        total_points = 0
        for match in matches:
            if match.home_team_id == team_id:
                if match.home_goals > match.away_goals:
                    total_points += 3
                elif match.home_goals == match.away_goals:
                    total_points += 1
            else:
                if match.away_goals > match.home_goals:
                    total_points += 3
                elif match.away_goals == match.home_goals:
                    total_points += 1

        return total_points / (len(matches) * 3)  # 0-1 arasında normalize edilmiş değerfrom datetime import datetime, timedelta
from app import db
from app.models import Match, Team

class DataService:
    @staticmethod
    def get_team_recent_matches(team_id, limit=5, before_date=None):
        """Takımın son maçlarını getirir"""
        if before_date is None:
            before_date = datetime.utcnow()

        return Match.query.filter(
            ((Match.home_team_id == team_id) | (Match.away_team_id == team_id)) &
            (Match.status == 'Finished') &
            (Match.match_date < before_date)
        ).order_by(Match.match_date.desc()).limit(limit).all()

    @staticmethod
    def calculate_team_form(matches, team_id):
        """Takımın son 5 maçındaki formunu hesaplar (puan ortalaması)"""
        if not matches:
            return 0.0

        total_points = 0
        for match in matches:
            if match.home_team_id == team_id:
                if match.home_goals > match.away_goals:
                    total_points += 3
                elif match.home_goals == match.away_goals:
                    total_points += 1
            else:
                if match.away_goals > match.home_goals:
                    total_points += 3
                elif match.away_goals == match.home_goals:
                    total_points += 1

        return total_points / (len(matches) * 3)  # 0-1 arasında normalize edilmiş değerfrom .data_service import DataService
from .prediction_service import PredictionService

__all__ = ['DataService', 'PredictionService']from .data_service import DataService
from .prediction_service import PredictionService

__all__ = ['DataService', 'PredictionService']from datetime import datetime
from .base_model import BaseModel
from app import db

class Match(BaseModel):
    __tablename__ = 'matches'

    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    match_date = db.Column(db.DateTime, nullable=False, index=True)
    season = db.Column(db.String(10))
    matchday = db.Column(db.Integer)
    status = db.Column(db.String(20))  # Scheduled, Finished, Postponed, etc.

    # Maç istatistikleri
    home_goals = db.Column(db.Integer)
    away_goals = db.Column(db.Integer)
    home_ht_goals = db.Column(db.Integer)
    away_ht_goals = db.Column(db.Integer)
    home_shots = db.Column(db.Integer)
    away_shots = db.Column(db.Integer)
    home_shots_on_target = db.Column(db.Integer)
    away_shots_on_target = db.Column(db.Integer)
    home_possession = db.Column(db.Float)
    away_possession = db.Column(db.Float)

    # Tahminler
    prediction_home_win = db.Column(db.Float)
    prediction_draw = db.Column(db.Float)
    prediction_away_win = db.Column(db.Float)
    prediction_goals_over_2_5 = db.Column(db.Float)
    prediction_btts = db.Column(db.Float)  # Both Teams To Score

    def __repr__(self):
        return f'<Match {self.home_team.name} vs {self.away_team.name} - {self.match_date}>'

    def to_dict(self):
        return {
            'id': self.id,
            'home_team': self.home_team.name,
            'away_team': self.away_team.name,
            'match_date': self.match_date.isoformat(),
            'home_goals': self.home_goals,
            'away_goals': self.away_goals,
            'status': self.status
        }from datetime import datetime
from .base_model import BaseModel
from app import db

class Match(BaseModel):
    __tablename__ = 'matches'

    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    match_date = db.Column(db.DateTime, nullable=False, index=True)
    season = db.Column(db.String(10))
    matchday = db.Column(db.Integer)
    status = db.Column(db.String(20))  # Scheduled, Finished, Postponed, etc.

    # Maç istatistikleri
    home_goals = db.Column(db.Integer)
    away_goals = db.Column(db.Integer)
    home_ht_goals = db.Column(db.Integer)
    away_ht_goals = db.Column(db.Integer)
    home_shots = db.Column(db.Integer)
    away_shots = db.Column(db.Integer)
    home_shots_on_target = db.Column(db.Integer)
    away_shots_on_target = db.Column(db.Integer)
    home_possession = db.Column(db.Float)
    away_possession = db.Column(db.Float)

    # Tahminler
    prediction_home_win = db.Column(db.Float)
    prediction_draw = db.Column(db.Float)
    prediction_away_win = db.Column(db.Float)
    prediction_goals_over_2_5 = db.Column(db.Float)
    prediction_btts = db.Column(db.Float)  # Both Teams To Score

    def __repr__(self):
        return f'<Match {self.home_team.name} vs {self.away_team.name} - {self.match_date}>'

    def to_dict(self):
        return {
            'id': self.id,
            'home_team': self.home_team.name,
            'away_team': self.away_team.name,
            'match_date': self.match_date.isoformat(),
            'home_goals': self.home_goals,
            'away_goals': self.away_goals,
            'status': self.status
        }from .base_model import BaseModel
from app import db

class Team(BaseModel):
    __tablename__ = 'teams'

    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    founded = db.Column(db.Integer)
    stadium = db.Column(db.String(100))
    logo = db.Column(db.String(255))
    attack_rating = db.Column(db.Float, default=50.0)
    defense_rating = db.Column(db.Float, default=50.0)
    home_advantage = db.Column(db.Float, default=1.1)
    current_form = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f'<Team {self.name}>'from .base_model import BaseModel
from app import db

class Team(BaseModel):
    __tablename__ = 'teams'

    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    founded = db.Column(db.Integer)
    stadium = db.Column(db.String(100))
    logo = db.Column(db.String(255))
    attack_rating = db.Column(db.Float, default=50.0)
    defense_rating = db.Column(db.Float, default=50.0)
    home_advantage = db.Column(db.Float, default=1.1)
    current_form = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f'<Team {self.name}>'from .base_model import BaseModel
from .country import Country
from .league import League
from .team import Team
from .match import Match

__all__ = ['BaseModel', 'Country', 'League', 'Team', 'Match']from .base_model import BaseModel
from .country import Country
from .league import League
from .team import Team
from .match import Match

__all__ = ['BaseModel', 'Country', 'League', 'Team', 'Match']import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gizli-anahtar-buraya'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FOOTBALL_DATA_API_KEY = os.environ.get('FOOTBALL_DATA_API_KEY', '')import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gizli-anahtar-buraya'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FOOTBALL_DATA_API_KEY = os.environ.get('FOOTBALL_DATA_API_KEY', '')import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
from joblib import dump, load
import os
from app import app
from .data_service import DataService

class PredictionService:
    def __init__(self):
        self.model_path = os.path.join(app.config['MODEL_PATH'], 'xgb_model.joblib')
        self.scaler_path = os.path.join(app.config['MODEL_PATH'], 'scaler.joblib')
        self.model = None
        self.scaler = None
        self.load_model()

    def load_model(self):
        """Modeli yükler veya yeni bir model oluşturur"""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = load(self.model_path)
            self.scaler = load(self.scaler_path)
        else:
            self.model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
            self.scaler = StandardScaler()

    def train(self, X, y):
        """Modeli eğitir"""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)

        # Modeli kaydet
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        dump(self.model, self.model_path)
        dump(self.scaler, self.scaler_path)

    def predict(self, features):
        """Tahmin yapar"""
        if not self.model or not self.scaler:
            raise Exception("Model yüklenemedi veya oluşturulamadı")

        features_scaled = self.scaler.transform([features])
        prediction = self.model.predict_proba(features_scaled)[0]

        return {
            'home_win': float(prediction[0]),
            'draw': float(prediction[1]),
            'away_win': float(prediction[2])
        }import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
from joblib import dump, load
import os
from app import app
from .data_service import DataService

class PredictionService:
    def __init__(self):
        self.model_path = os.path.join(app.config['MODEL_PATH'], 'xgb_model.joblib')
        self.scaler_path = os.path.join(app.config['MODEL_PATH'], 'scaler.joblib')
        self.model = None
        self.scaler = None
        self.load_model()

    def load_model(self):
        """Modeli yükler veya yeni bir model oluşturur"""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = load(self.model_path)
            self.scaler = load(self.scaler_path)
        else:
            self.model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
            self.scaler = StandardScaler()

    def train(self, X, y):
        """Modeli eğitir"""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)

        # Modeli kaydet
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        dump(self.model, self.model_path)
        dump(self.scaler, self.scaler_path)

    def predict(self, features):
        """Tahmin yapar"""
        if not self.model or not self.scaler:
            raise Exception("Model yüklenemedi veya oluşturulamadı")

        features_scaled = self.scaler.transform([features])
        prediction = self.model.predict_proba(features_scaled)[0]

        return {
            'home_win': float(prediction[0]),
            'draw': float(prediction[1]),
            'away_win': float(prediction[2])
        }import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
from joblib import dump, load
import os
from app import app
from .data_service import DataService

class PredictionService:
    def __init__(self):
        self.model_path = os.path.join(app.config['MODEL_PATH'], 'xgb_model.joblib')
        self.scaler_path = os.path.join(app.config['MODEL_PATH'], 'scaler.joblib')
        self.model = None
        self.scaler = None
        self.load_model()

    def load_model(self):
        """Modeli yükler veya yeni bir model oluşturur"""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = load(self.model_path)
            self.scaler = load(self.scaler_path)
        else:
            self.model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
            self.scaler = StandardScaler()

    def train(self, X, y):
        """Modeli eğitir"""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)

        # Modeli kaydet
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        dump(self.model, self.model_path)
        dump(self.scaler, self.scaler_path)

    def predict(self, features):
        """Tahmin yapar"""
        if not self.model or not self.scaler:
            raise Exception("Model yüklenemedi veya oluşturulamadı")

        features_scaled = self.scaler.transform([features])
        prediction = self.model.predict_proba(features_scaled)[0]

        return {
            'home_win': float(prediction[0]),
            'draw': float(prediction[1]),
            'away_win': float(prediction[2])
        }from datetime import datetime, timedelta
from app import db
from app.models import Match, Team

class DataService:
    @staticmethod
    def get_team_recent_matches(team_id, limit=5, before_date=None):
        """Takımın son maçlarını getirir"""
        if before_date is None:
            before_date = datetime.utcnow()

        return Match.query.filter(
            ((Match.home_team_id == team_id) | (Match.away_team_id == team_id)) &
            (Match.status == 'Finished') &
            (Match.match_date < before_date)
        ).order_by(Match.match_date.desc()).limit(limit).all()

    @staticmethod
    def calculate_team_form(matches, team_id):
        """Takımın son 5 maçındaki formunu hesaplar (puan ortalaması)"""
        if not matches:
            return 0.0

        total_points = 0
        for match in matches:
            if match.home_team_id == team_id:
                if match.home_goals > match.away_goals:
                    total_points += 3
                elif match.home_goals == match.away_goals:
                    total_points += 1
            else:
                if match.away_goals > match.home_goals:
                    total_points += 3
                elif match.away_goals == match.home_goals:
                    total_points += 1

        return total_points / (len(matches) * 3)  # 0-1 arasında normalize edilmiş değerfrom datetime import datetime
from .base_model import BaseModel
from app import db

class Match(BaseModel):
    __tablename__ = 'matches'

    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    match_date = db.Column(db.DateTime, nullable=False, index=True)
    season = db.Column(db.String(10))
    matchday = db.Column(db.Integer)
    status = db.Column(db.String(20))  # Scheduled, Finished, Postponed, etc.

    # Maç istatistikleri
    home_goals = db.Column(db.Integer)
    away_goals = db.Column(db.Integer)
    home_ht_goals = db.Column(db.Integer)
    away_ht_goals = db.Column(db.Integer)
    home_shots = db.Column(db.Integer)
    away_shots = db.Column(db.Integer)
    home_shots_on_target = db.Column(db.Integer)
    away_shots_on_target = db.Column(db.Integer)
    home_possession = db.Column(db.Float)
    away_possession = db.Column(db.Float)

    # Tahminler
    prediction_home_win = db.Column(db.Float)
    prediction_draw = db.Column(db.Float)
    prediction_away_win = db.Column(db.Float)
    prediction_goals_over_2_5 = db.Column(db.Float)
    prediction_btts = db.Column(db.Float)  # Both Teams To Score

    def __repr__(self):
        return f'<Match {self.home_team.name} vs {self.away_team.name} - {self.match_date}>'

    def to_dict(self):
        return {
            'id': self.id,
            'home_team': self.home_team.name,
            'away_team': self.away_team.name,
            'match_date': self.match_date.isoformat(),
            'home_goals': self.home_goals,
            'away_goals': self.away_goals,
            'status': self.status
        }from .base_model import BaseModel
from app import db

class Team(BaseModel):
    __tablename__ = 'teams'

    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    founded = db.Column(db.Integer)
    stadium = db.Column(db.String(100))
    logo = db.Column(db.String(255))
    attack_rating = db.Column(db.Float, default=50.0)
    defense_rating = db.Column(db.Float, default=50.0)
    home_advantage = db.Column(db.Float, default=1.1)
    current_form = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f'<Team {self.name}>'from .base_model import BaseModel
from .country import Country
from .league import League
from .team import Team
from .match import Match

__all__ = ['BaseModel', 'Country', 'League', 'Team', 'Match']from .base_model import BaseModel
from .country import Country
from .league import League
from .team import Team
from .match import Match

__all__ = ['BaseModel', 'Country', 'League', 'Team', 'Match']from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

from app import modelsfrom flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

from app import modelsimport os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gizli-anahtar-buraya'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FOOTBALL_DATA_API_KEY = os.environ.get('FOOTBALL_DATA_API_KEY', '')import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gizli-anahtar-buraya'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FOOTBALL_DATA_API_KEY = os.environ.get('FOOTBALL_DATA_API_KEY', '')flask==2.0.1
flask-sqlalchemy==2.5.1
flask-migrate==3.1.0
python-dotenv==0.19.0
pandas==1.3.3
numpy==1.21.2
scikit-learn==0.24.2
xgboost==1.4.2
tensorflow==2.6.0
gunicorn==20.1.0# config.py
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gizli-anahtar-buraya'
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "app.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FOOTBALL_DATA_API_KEY = os.environ.get('FOOTBALL_DATA_API_KEY', '')# config.py
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gizli-anahtar-buraya'
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "app.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FOOTBALL_DATA_API_KEY = os.environ.get('FOOTBALL_DATA_API_KEY', '')# Gerekli klasör yapısını oluştur
mkdir -p app/models app/api app/services
New-Item -ItemType File -Path "app/__init__.py", "app/models/__init__.py", "app/api/__init__.py", "app/services/__init__.py", "config.py", "run.py", ".env"# Gerekli klasör yapısını oluştur
mkdir -p app/models app/api app/services
New-Item -ItemType File -Path "app/__init__.py", "app/models/__init__.py", "app/api/__init__.py", "app/services/__init__.py", "config.py", "run.py", ".env"# run.py
from app import create_app, db
from app.models import Country, League, Team, Match

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Country': Country,
        'League': League,
        'Team': Team,
        'Match': Match
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)# run.py
from app import create_app, db
from app.models import Country, League, Team, Match

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Country': Country,
        'League': League,
        'Team': Team,
        'Match': Match
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)# run.py
from app import create_app, db
from app.models import Country, League, Team, Match

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Country': Country,
        'League': League,
        'Team': Team,
        'Match': Match
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)# run.py
from app import create_app, db
from app.models import Country, League, Team, Match

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Country': Country,
        'League': League,
        'Team': Team,
        'Match': Match
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)flask shell
>>> from app import db
>>> from app.models import Country
>>> country = Country(name='Türkiye', code='TUR')
>>> db.session.add(country)
>>> db.session.commit()
>>> Country.query.all()flask db init
flask db migrate -m "Initial migration"
flask db upgradeflask db init
flask db migrate -m "Initial migration"
flask db upgradepython -m venv venv
.\venv\Scripts\activatepython -m venv venv
.\venv\Scripts\activateimport os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gizli-anahtar-buraya'
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "app.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FOOTBALL_DATA_API_KEY = os.environ.get('FOOTBALL_DATA_API_KEY', '')
    MODEL_PATH = os.path.join(basedir, 'app/models/saved_models')
    os.makedirs(MODEL_PATH, exist_ok=True)import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gizli-anahtar-buraya'
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "app.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FOOTBALL_DATA_API_KEY = os.environ.get('FOOTBALL_DATA_API_KEY', '')
    MODEL_PATH = os.path.join(basedir, 'app/models/saved_models')
    os.makedirs(MODEL_PATH, exist_ok=True)from app import create_app, db
from app.models import Country, League, Team, Match

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Country': Country,
        'League': League,
        'Team': Team,
        'Match': Match
    }

if __name__ == '__main__':
    app.run(debug=True)from app import create_app, db
from app.models import Country, League, Team, Match

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Country': Country,
        'League': League,
        'Team': Team,
        'Match': Match
    }

if __name__ == '__main__':
    app.run(debug=True)from app import create_app, db
from app.models import Country, League, Team, Match

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Country': Country,
        'League': League,
        'Team': Team,
        'Match': Match
    }

if __name__ == '__main__':
    app.run(debug=True)from app import create_app, db
from app.models import Country, League, Team, Match

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Country': Country,
        'League': League,
        'Team': Team,
        'Match': Match
    }

if __name__ == '__main__':
    app.run(debug=True)from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from config import Config

# Uygulama ve veritabanı başlatma
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    # Uygulama örneğini oluştur
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Uzantıları başlat
    db.init_app(app)
    migrate.init_app(app, db)

    # Blueprint'leri kaydet
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

from app import models  # noqafrom flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from config import Config

# Uygulama ve veritabanı başlatma
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    # Uygulama örneğini oluştur
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Uzantıları başlat
    db.init_app(app)
    migrate.init_app(app, db)

    # Blueprint'leri kaydet
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

from app import models  # noqamacanaliz/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py
│   │   ├── country.py
│   │   ├── league.py
│   │   ├── team.py
│   │   └── match.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_service.py
│   │   └── prediction_service.py
│   └── api/
│       ├── __init__.py
│       └── routes.py
├── .env
├── config.py
├── requirements.txt
└── run.pymacanaliz/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py
│   │   ├── country.py
│   │   ├── league.py
│   │   ├── team.py
│   │   └── match.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_service.py
│   │   └── prediction_service.py
│   └── api/
│       ├── __init__.py
│       └── routes.py
├── .env
├── config.py
├── requirements.txt
└── run.pySECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///app.db
FOOTBALL_DATA_API_KEY=your-api-keySECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///app.db
FOOTBALL_DATA_API_KEY=your-api-keySECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///app.db
FOOTBALL_DATA_API_KEY=your-api-keySECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///app.db
FOOTBALL_DATA_API_KEY=your-api-keySECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///app.db
FOOTBALL_DATA_API_KEY=your-api-keySECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///app.db
FOOTBALL_DATA_API_KEY=your-api-keymacanaliz/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── services/
│   └── api/
└── .envmacanaliz/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── services/
│   └── api/
└── .envmacanaliz/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── services/
│   └── api/
└── .envmacanaliz/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── services/
│   └── api/
└── .envmacanaliz/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── services/
│   └── api/
└── .envmacanaliz/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── services/
│   └── api/
└── .env
requests==2.26.0flask==2.0.1
flask-sqlalchemy==2.5.1
flask-migrate==3.1.0
python-dotenv==0.19.0
pandas==1.3.3
numpy==1.21.2
scikit-learn==0.24.2
xgboost==1.4.2
tensorflow==2.6.0
gunicorn==20.1.0
requests==2.26.0macanaliz/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py
│   │   ├── country.py
│   │   ├── league.py
│   │   ├── team.py
│   │   └── match.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_service.py
│   │   └── prediction_service.py
│   └── api/
│       ├── __init__.py
│       ├── routes.py
│       └── schemas.py
├── config.py
├── requirements.txt
└── run.pymacanaliz/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py
│   │   ├── country.py
│   │   ├── league.py
│   │   ├── team.py
│   │   └── match.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_service.py
│   │   └── prediction_service.py
│   └── api/
│       ├── __init__.py
│       ├── routes.py
│       └── schemas.py
├── config.py
├── requirements.txt
└── run.pyimport os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gizli-anahtar-buraya'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FOOTBALL_DATA_API_KEY = os.environ.get('FOOTBALL_DATA_API_KEY', '')import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

# Uygulama ve veritabanı başlatma
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    # Uygulama örneğini oluştur
    app = Flask(__name__)

    # Yapılandırmayı yükle
    load_dotenv()
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gizli-anahtar-buraya')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'sqlite:///app.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['FOOTBALL_DATA_API_KEY'] = os.environ.get('FOOTBALL_DATA_API_KEY', '')

    # Uzantıları başlat
    db.init_app(app)
    migrate.init_app(app, db)

    # Blueprint'leri kaydet
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Shell context ekle
    @app.shell_context_processor
    def make_shell_context():
        from app.models import Country, League, Team, Match
        return {
            'db': db,
            'Country': Country,
            'League': League,
            'Team': Team,
            'Match': Match
        }

    return app

# Uygulamayı oluştur
app = create_app()

# Ana uygulama çalıştırıldığında
if __name__ == '__main__':
    app.run(debug=True)from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

# Uygulama ve veritabanı başlatma
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    # Uygulama örneğini oluştur
    app = Flask(__name__)

    # Yapılandırmayı yükle
    load_dotenv()
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gizli-anahtar-buraya')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'sqlite:///app.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['FOOTBALL_DATA_API_KEY'] = os.environ.get('FOOTBALL_DATA_API_KEY', '')

    # Uzantıları başlat
    db.init_app(app)
    migrate.init_app(app, db)

    # Blueprint'leri kaydet
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Shell context ekle
    @app.shell_context_processor
    def make_shell_context():
        from app.models import Country, League, Team, Match
        return {
            'db': db,
            'Country': Country,
            'League': League,
            'Team': Team,
            'Match': Match
        }

    return app

# Uygulamayı oluştur
app = create_app()

# Ana uygulama çalıştırıldığında
if __name__ == '__main__':
    app.run(debug=True)flask db init
flask db migrate -m "Initial migration"
flask db upgradeflask db init
flask db migrate -m "Initial migration"
flask db upgradeflask db init
flask db migrate -m "Initial migration"
flask db upgradeflask db init
flask db migrate -m "Initial migration"
flask db upgradepython -m venv venv
.\venv\Scripts\activatepython -m venv venv
.\venv\Scripts\activate# Uygulama Ayarları
SECRET_KEY=your-secret-key-here
DEBUG=True

# Veritabanı Ayarları
DATABASE_URL=sqlite:///app.db

# API Anahtarları
FOOTBALL_DATA_API_KEY=your-api-key-here# Uygulama Ayarları
SECRET_KEY=your-secret-key-here
DEBUG=True

# Veritabanı Ayarları
DATABASE_URL=sqlite:///app.db

# API Anahtarları
FOOTBALL_DATA_API_KEY=your-api-key-herefrom app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)from flask import jsonify, request
from app import db
from app.models import Team, Match, League
from app.services import DataService
from . import bp

@bp.route('/teams', methods=['GET'])
def get_teams():
    teams = Team.query.all()
    return jsonify([{
        'id': team.id,
        'name': team.name,
        'league_id': team.league_id
    } for team in teams])

@bp.route('/matches', methods=['GET'])
def get_matches():
    league_id = request.args.get('league_id', type=int)
    status = request.args.get('status', 'Scheduled')

    query = Match.query
    if league_id:
        query = query.filter_by(league_id=league_id)
    if status:
        query = query.filter_by(status=status)

    matches = query.order_by(Match.match_date).limit(100).all()
    return jsonify([match.to_dict() for match in matches])from flask import jsonify, request
from app import db
from app.models import Team, Match, League
from app.services import DataService
from . import bp

@bp.route('/teams', methods=['GET'])
def get_teams():
    teams = Team.query.all()
    return jsonify([{
        'id': team.id,
        'name': team.name,
        'league_id': team.league_id
    } for team in teams])

@bp.route('/matches', methods=['GET'])
def get_matches():
    league_id = request.args.get('league_id', type=int)
    status = request.args.get('status', 'Scheduled')

    query = Match.query
    if league_id:
        query = query.filter_by(league_id=league_id)
    if status:
        query = query.filter_by(status=status)

    matches = query.order_by(Match.match_date).limit(100).all()
    return jsonify([match.to_dict() for match in matches])from .base_model import BaseModel
from app import db

class Team(BaseModel):
    __tablename__ = 'teams'

    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    founded = db.Column(db.Integer)
    stadium = db.Column(db.String(100))
    logo = db.Column(db.String(255))
    attack_rating = db.Column(db.Float, default=50.0)
    defense_rating = db.Column(db.Float, default=50.0)
    home_advantage = db.Column(db.Float, default=1.1)
    current_form = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f'<Team {self.name}>'from .base_model import BaseModel
from app import db

class Team(BaseModel):
    __tablename__ = 'teams'

    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    founded = db.Column(db.Integer)
    stadium = db.Column(db.String(100))
    logo = db.Column(db.String(255))
    attack_rating = db.Column(db.Float, default=50.0)
    defense_rating = db.Column(db.Float, default=50.0)
    home_advantage = db.Column(db.Float, default=1.1)
    current_form = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f'<Team {self.name}>'from .base_model import BaseModel
from app import db

class Team(BaseModel):
    __tablename__ = 'teams'

    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    founded = db.Column(db.Integer)
    stadium = db.Column(db.String(100))
    logo = db.Column(db.String(255))
    attack_rating = db.Column(db.Float, default=50.0)
    defense_rating = db.Column(db.Float, default=50.0)
    home_advantage = db.Column(db.Float, default=1.1)
    current_form = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f'<Team {self.name}>'import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Uygulama ayarları
    SECRET_KEY = os.environ.get('SECRET_KEY', 'gizli-anahtar-buraya')
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'

    # Veritabanı ayarları
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "app.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # API ayarları
    FOOTBALL_DATA_API_KEY = os.environ.get('FOOTBALL_DATA_API_KEY', '')

    # Model yolları
    MODEL_PATH = os.path.join(basedir, 'app/models/saved_models')
    os.makedirs(MODEL_PATH, exist_ok=True)import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Uygulama ayarları
    SECRET_KEY = os.environ.get('SECRET_KEY', 'gizli-anahtar-buraya')
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'

    # Veritabanı ayarları
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "app.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # API ayarları
    FOOTBALL_DATA_API_KEY = os.environ.get('FOOTBALL_DATA_API_KEY', '')

    # Model yolları
    MODEL_PATH = os.path.join(basedir, 'app/models/saved_models')
    os.makedirs(MODEL_PATH, exist_ok=True)import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Uygulama ayarları
    SECRET_KEY = os.environ.get('SECRET_KEY', 'gizli-anahtar-buraya')
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'

    # Veritabanı ayarları
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "app.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # API ayarları
    FOOTBALL_DATA_API_KEY = os.environ.get('FOOTBALL_DATA_API_KEY', '')

    # Model yolları
    MODEL_PATH = os.path.join(basedir, 'app/models/saved_models')
    os.makedirs(MODEL_PATH, exist_ok=True)Flask==2.0.1
Flask-SQLAlchemy==2.5.1
Flask-Migrate==3.1.0
python-dotenv==0.19.0
pandas==1.3.3
numpy==1.21.2
scikit-learn==0.24.2
xgboost==1.4.2
requests==2.26.0
gunicorn==20.1.0Flask==2.0.1
Flask-SQLAlchemy==2.5.1
Flask-Migrate==3.1.0
python-dotenv==0.19.0
pandas==1.3.3
numpy==1.21.2
scikit-learn==0.24.2
xgboost==1.4.2
requests==2.26.0
gunicorn==20.1.0Flask==2.0.1
Flask-SQLAlchemy==2.5.1
Flask-Migrate==3.1.0
python-dotenv==0.19.0
pandas==1.3.3
numpy==1.21.2
scikit-learn==0.24.2
xgboost==1.4.2
requests==2.26.0
gunicorn==20.1.0

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gizli-anahtar-buraya'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FOOTBALL_DATA_API_KEY = os.environ.get('FOOTBALL_DATA_API_KEY', '')import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gizli-anahtar-buraya'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FOOTBALL_DATA_API_KEY = os.environ.get('FOOTBALL_DATA_API_KEY', '')macanaliz/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py
│   │   ├── country.py
│   │   ├── league.py
│   │   ├── team.py
│   │   └── match.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_service.py
│   │   └── prediction_service.py
│   └── api/
│       ├── __init__.py
│       ├── routes.py
│       └── schemas.py
├── config.py
├── requirements.txt
└── run.pyfrom flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Country(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(3), unique=True, nullable=False)
    flag = db.Column(db.String(255))
    leagues = db.relationship('League', backref='country', lazy=True)
    teams = db.relationship('Team', backref='country', lazy=True)

class League(db.Model):
    __tablename__ = 'leagues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    level = db.Column(db.Integer)
    logo = db.Column(db.String(255))
    current_season = db.Column(db.String(10))
    teams = db.relationship('Team', backref='league', lazy=True)
    matches = db.relationship('Match', backref='league', lazy=True)

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    founded = db.Column(db.Integer)
    stadium = db.Column(db.String(100))
    logo = db.Column(db.String(255))
    attack_rating = db.Column(db.Float, default=50.0)
    defense_rating = db.Column(db.Float, default=50.0)
    home_advantage = db.Column(db.Float, default=1.1)
    current_form = db.Column(db.Float, default=0.0)
    home_matches = db.relationship('Match', foreign_keys='Match.home_team_id',
                                 backref='home_team', lazy=True)
    away_matches = db.relationship('Match', foreign_keys='Match.away_team_id',
                                 backref='away_team', lazy=True)

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    match_date = db.Column(db.DateTime, nullable=False, index=True)
    season = db.Column(db.String(10))
    matchday = db.Column(db.Integer)
    status = db.Column(db.String(20))  # Scheduled, Finished, Postponed, etc.

    # Maç istatistikleri
    home_goals = db.Column(db.Integer)
    away_goals = db.Column(db.Integer)
    home_ht_goals = db.Column(db.Integer)
    away_ht_goals = db.Column(db.Integer)
    home_shots = db.Column(db.Integer)
    away_shots = db.Column(db.Integer)
    home_shots_on_target = db.Column(db.Integer)
    away_shots_on_target = db.Column(db.Integer)
    home_possession = db.Column(db.Float)
    away_possession = db.Column(db.Float)

    # Tahminler
    prediction_home_win = db.Column(db.Float)
    prediction_draw = db.Column(db.Float)
    prediction_away_win = db.Column(db.Float)
    prediction_goals_over_2_5 = db.Column(db.Float)
    prediction_btts = db.Column(db.Float)  # Both Teams To Score

    def to_dict(self):
        return {
            'id': self.id,
            'home_team': self.home_team.name,
            'away_team': self.away_team.name,
            'match_date': self.match_date.isoformat(),
            'home_goals': self.home_goals,
            'away_goals': self.away_goals,
            'status': self.status
        }from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Country(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(3), unique=True, nullable=False)
    flag = db.Column(db.String(255))
    leagues = db.relationship('League', backref='country', lazy=True)
    teams = db.relationship('Team', backref='country', lazy=True)

class League(db.Model):
    __tablename__ = 'leagues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    level = db.Column(db.Integer)
    logo = db.Column(db.String(255))
    current_season = db.Column(db.String(10))
    teams = db.relationship('Team', backref='league', lazy=True)
    matches = db.relationship('Match', backref='league', lazy=True)

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    founded = db.Column(db.Integer)
    stadium = db.Column(db.String(100))
    logo = db.Column(db.String(255))
    attack_rating = db.Column(db.Float, default=50.0)
    defense_rating = db.Column(db.Float, default=50.0)
    home_advantage = db.Column(db.Float, default=1.1)
    current_form = db.Column(db.Float, default=0.0)
    home_matches = db.relationship('Match', foreign_keys='Match.home_team_id',
                                 backref='home_team', lazy=True)
    away_matches = db.relationship('Match', foreign_keys='Match.away_team_id',
                                 backref='away_team', lazy=True)

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    match_date = db.Column(db.DateTime, nullable=False, index=True)
    season = db.Column(db.String(10))
    matchday = db.Column(db.Integer)
    status = db.Column(db.String(20))  # Scheduled, Finished, Postponed, etc.

    # Maç istatistikleri
    home_goals = db.Column(db.Integer)
    away_goals = db.Column(db.Integer)
    home_ht_goals = db.Column(db.Integer)
    away_ht_goals = db.Column(db.Integer)
    home_shots = db.Column(db.Integer)
    away_shots = db.Column(db.Integer)
    home_shots_on_target = db.Column(db.Integer)
    away_shots_on_target = db.Column(db.Integer)
    home_possession = db.Column(db.Float)
    away_possession = db.Column(db.Float)

    # Tahminler
    prediction_home_win = db.Column(db.Float)
    prediction_draw = db.Column(db.Float)
    prediction_away_win = db.Column(db.Float)
    prediction_goals_over_2_5 = db.Column(db.Float)
    prediction_btts = db.Column(db.Float)  # Both Teams To Score

    def to_dict(self):
        return {
            'id': self.id,
            'home_team': self.home_team.name,
            'away_team': self.away_team.name,
            'match_date': self.match_date.isoformat(),
            'home_goals': self.home_goals,
            'away_goals': self.away_goals,
            'status': self.status
        }import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Uygulama ayarları
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gizli-anahtar-buraya'
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'

    # Veritabanı ayarları
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Model yolları
    MODEL_PATH = os.path.join(basedir, 'app/models/saved_models')
    os.makedirs(MODEL_PATH, exist_ok=True)

    # API ayarları
    FOOTBALL_DATA_API_KEY = os.environ.get('FOOTBALL_DATA_API_KEY', '')
    FOOTBALL_DATA_API_URL = 'https://api.football-data.org/v4/'import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Uygulama ayarları
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gizli-anahtar-buraya'
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'

    # Veritabanı ayarları
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Model yolları
    MODEL_PATH = os.path.join(basedir, 'app/models/saved_models')
    os.makedirs(MODEL_PATH, exist_ok=True)

    # API ayarları
    FOOTBALL_DATA_API_KEY = os.environ.get('FOOTBALL_DATA_API_KEY', '')
    FOOTBALL_DATA_API_URL = 'https://api.football-data.org/v4/'Flask==2.3.3
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
python-dotenv==1.0.0
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
xgboost==1.7.6
tensorflow==2.13.0
joblib==1.3.2
requests==2.31.0
gunicorn==21.2.0Flask==2.3.3
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
python-dotenv==1.0.0
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
xgboost==1.7.6
tensorflow==2.13.0
joblib==1.3.2
requests==2.31.0
gunicorn==21.2.0macanaliz/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py
│   │   ├── xgboost_model.py
│   │   └── lstm_model.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_service.py
│   │   └── prediction_service.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   └── static/
│       ├── css/
│       └── js/
├── config.py
├── requirements.txt
└── run.pymacanaliz/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py
│   │   ├── xgboost_model.py
│   │   └── lstm_model.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_service.py
│   │   └── prediction_service.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   └── static/
│       ├── css/
│       └── js/
├── config.py
├── requirements.txt
└── run.pymacanaliz/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py
│   │   ├── xgboost_model.py
│   │   └── lstm_model.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_service.py
│   │   └── prediction_service.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   └── static/
│       ├── css/
│       └── js/
├── config.py
├── requirements.txt
└── run.pyimport os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Uygulama ayarları
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gizli-anahtar-buraya'
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'

    # Veritabanı ayarları
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Model yolları
    MODEL_PATHimport os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Uygulama ayarları
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gizli-anahtar-buraya'
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'

    # Veritabanı ayarları
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Model yolları
    MODEL_PATHFlask==2.3.3
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
python-dotenv==1.0.0
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
xgboost==1.7.6
tensorflow==2.13.0
joblib==1.3.2
requests==2.31.0
gunicorn==21.2.0import joblib
import numpy as np
from datetime import datetime
from models import db, Match, Team
from models.prediction_models.xgboost_model import XGBoostPredictor
from models.prediction_models.lstm_model import LSTMPredictor
from services.data_service import DataService

class PredictionService:
    def __init__(self):
        self.data_service = DataService()
        self.xgb_predictor = XGBoostPredictor()
        self.lstm_predictor = LSTMPredictor()

    def predict_match(self, home_team_id, away_team_id, match_date=None):
        """Maç için tahmin yapar"""
        if match_date is None:
            match_date = datetime.utcnow()

        # Maç özelliklerini hazırla
        features = self.data_service.prepare_match_features(
            home_team_id, away_team_id, match_date
        )

        # XGBoost ile sonuç tahmini
        xgb_result = self.xgb_predictor.predict(features)

        # LSTM ile gol sayısı tahmini
        home_team_matches = self.data_service.get_team_recent_matches(home_team_id, 10, match_date)
        away_team_matches = self.data_service.get_team_recent_matches(away_team_id, 10, match_date)

        # Gol verilerini hazırla
        home_goals = [m.home_goals if m.home_team_id == home_team_id else m.away_goals
                     for m in home_team_matches]
        away_goals = [m.away_goals if m.away_team_id == away_team_id else m.home_goals
                     for m in away_team_matches]

        # Eğer yeterli veri yoksa varsayılan değerler kullan
        if len(home_goals) < 5 or len(away_goals) < 5:
            predicted_home_goals = sum(home_goals) / len(home_goals) if home_goals else 1.5
            predicted_away_goals = sum(away_goals) / len(away_goals) if away_goals else 1.2
        else:
            # LSTM ile gol tahmini yap
            predicted_home_goals = self.lstm_predictor.predict(np.array(home_goals[:5]))
            predicted_away_goals = self.lstm_predictor.predict(np.array(away_goals[:5]))

        # Tahmin sonuçlarını birleştir
        result = {
            'match_prediction': {
                'home_win_prob': xgb_result['probabilities']['home_win'],
                'draw_prob': xgb_result['probabilities']['draw'],
                'away_win_prob': xgb_result['probabilities']['away_win'],
                'predicted_winner': 'home' if xgb_result['prediction'] == 2 else
                                  'away' if xgb_result['prediction'] == 0 else 'draw'
            },
            'score_prediction': {
                'home_goals': round(float(predicted_home_goals), 1),
                'away_goals': round(float(predicted_away_goals), 1)
            },
            'additional_stats': {
                'over_2_5': (predicted_home_goals + predicted_away_goals) > 2.5,
                'btts': predicted_home_goals > 0.5 and predicted_away_goals > 0.5
            }
        }

        return result

    def train_models(self, matches_df):
        """Modelleri veri kümesi üzerinde eğitir"""
        # XGBoost için veri hazırlama
        X = []
        y = []

        for _, match in matches_df.iterrows():
            features = self.data_service.prepare_match_features(
                match['home_team_id'],
                match['away_team_id'],
                match['match_date']
            )

            # Sonuç etiketi (0: deplasman galibiyeti, 1: beraberlik, 2: iç saha galibiyeti)
            if match['home_goals'] > match['away_goals']:
                result = 2
            elif match['home_goals'] < match['away_goals']:
                result = 0
            else:
                result = 1

            X.append(list(features.values()))
            y.append(result)

        # XGBoost modelini eğit
        self.xgb_predictor.train(np.array(X), np.array(y))

        # LSTM için gol verilerini hazırla
        home_goals = matches_df['home_goals'].values.reshape(-1, 1)
        away_goals = matches_df['away_goals'].values.reshape(-1, 1)

        # LSTM modellerini eğit
        X_train_h, X_test_h, y_train_h, y_test_h = self.lstm_predictor.prepare_data(
            pd.DataFrame(home_goals, columns=['total_goals'])
        )
        self.lstm_predictor.train(X_train_h, y_train_h)

        print("Modeller başarıyla eğitildi!")import joblib
import numpy as np
from datetime import datetime
from models import db, Match, Team
from models.prediction_models.xgboost_model import XGBoostPredictor
from models.prediction_models.lstm_model import LSTMPredictor
from services.data_service import DataService

class PredictionService:
    def __init__(self):
        self.data_service = DataService()
        self.xgb_predictor = XGBoostPredictor()
        self.lstm_predictor = LSTMPredictor()

    def predict_match(self, home_team_id, away_team_id, match_date=None):
        """Maç için tahmin yapar"""
        if match_date is None:
            match_date = datetime.utcnow()

        # Maç özelliklerini hazırla
        features = self.data_service.prepare_match_features(
            home_team_id, away_team_id, match_date
        )

        # XGBoost ile sonuç tahmini
        xgb_result = self.xgb_predictor.predict(features)

        # LSTM ile gol sayısı tahmini
        home_team_matches = self.data_service.get_team_recent_matches(home_team_id, 10, match_date)
        away_team_matches = self.data_service.get_team_recent_matches(away_team_id, 10, match_date)

        # Gol verilerini hazırla
        home_goals = [m.home_goals if m.home_team_id == home_team_id else m.away_goals
                     for m in home_team_matches]
        away_goals = [m.away_goals if m.away_team_id == away_team_id else m.home_goals
                     for m in away_team_matches]

        # Eğer yeterli veri yoksa varsayılan değerler kullan
        if len(home_goals) < 5 or len(away_goals) < 5:
            predicted_home_goals = sum(home_goals) / len(home_goals) if home_goals else 1.5
            predicted_away_goals = sum(away_goals) / len(away_goals) if away_goals else 1.2
        else:
            # LSTM ile gol tahmini yap
            predicted_home_goals = self.lstm_predictor.predict(np.array(home_goals[:5]))
            predicted_away_goals = self.lstm_predictor.predict(np.array(away_goals[:5]))

        # Tahmin sonuçlarını birleştir
        result = {
            'match_prediction': {
                'home_win_prob': xgb_result['probabilities']['home_win'],
                'draw_prob': xgb_result['probabilities']['draw'],
                'away_win_prob': xgb_result['probabilities']['away_win'],
                'predicted_winner': 'home' if xgb_result['prediction'] == 2 else
                                  'away' if xgb_result['prediction'] == 0 else 'draw'
            },
            'score_prediction': {
                'home_goals': round(float(predicted_home_goals), 1),
                'away_goals': round(float(predicted_away_goals), 1)
            },
            'additional_stats': {
                'over_2_5': (predicted_home_goals + predicted_away_goals) > 2.5,
                'btts': predicted_home_goals > 0.5 and predicted_away_goals > 0.5
            }
        }

        return result

    def train_models(self, matches_df):
        """Modelleri veri kümesi üzerinde eğitir"""
        # XGBoost için veri hazırlama
        X = []
        y = []

        for _, match in matches_df.iterrows():
            features = self.data_service.prepare_match_features(
                match['home_team_id'],
                match['away_team_id'],
                match['match_date']
            )

            # Sonuç etiketi (0: deplasman galibiyeti, 1: beraberlik, 2: iç saha galibiyeti)
            if match['home_goals'] > match['away_goals']:
                result = 2
            elif match['home_goals'] < match['away_goals']:
                result = 0
            else:
                result = 1

            X.append(list(features.values()))
            y.append(result)

        # XGBoost modelini eğit
        self.xgb_predictor.train(np.array(X), np.array(y))

        # LSTM için gol verilerini hazırla
        home_goals = matches_df['home_goals'].values.reshape(-1, 1)
        away_goals = matches_df['away_goals'].values.reshape(-1, 1)

        # LSTM modellerini eğit
        X_train_h, X_test_h, y_train_h, y_test_h = self.lstm_predictor.prepare_data(
            pd.DataFrame(home_goals, columns=['total_goals'])
        )
        self.lstm_predictor.train(X_train_h, y_train_h)

        print("Modeller başarıyla eğitildi!")import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

class LSTMPredictor:
    def __init__(self, model_path=None, sequence_length=5):
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.sequence_length = sequence_length
        self.model_path = model_path or os.path.join('models', 'prediction_models', 'lstm_model.h5')
        self.scaler_path = os.path.join('models', 'prediction_models', 'lstm_scaler.pkl')

        # Model ve scaler'ı yükle (eğer varsa)
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = load_model(self.model_path)
            self.scaler = joblib.load(self.scaler_path)

    def create_sequences(self, data, seq_length):
        """Zaman serisi verisini LSTM için uygun formata dönüştürür"""
        X, y = [], []
        for i in range(len(data) - seq_length):
            X.append(data[i:(i + seq_length)])
            y.append(data[i + seq_length])
        return np.array(X), np.array(y)

    def prepare_data(self, df, target_column='total_goals', test_size=0.2):
        """Veriyi hazırlar ve ölçeklendirir"""
        # Hedef değişkeni seç
        data = df[target_column].values.reshape(-1, 1)

        # Ölçeklendir
        scaled_data = self.scaler.fit_transform(data)

        # Zaman serisi verisini oluştur
        X, y = self.create_sequences(scaled_data, self.sequence_length)

        # Eğitim ve test setlerine ayır
        train_size = int(len(X) * (1 - test_size))
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]

        return X_train, X_test, y_train, y_test

    def build_model(self, input_shape):
        """LSTM modelini oluşturur"""
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25, activation='relu'),
            Dense(1)
        ])

        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )

        return model

    def train(self, X, y, epochs=50, batch_size=32, validation_split=0.1):
        """Modeli eğitir"""
        self.model = self.build_model((X.shape[1], X.shape[2]))

        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=1
        )

        # Modeli kaydet
        self.save_model()

        return history

    def predict(self, sequence):
        """Tahmin yapar"""
        if self.model is None:
            raise ValueError("Model henüz eğitilmemiş veya yüklenmemiş!")

        # Girişi ölçeklendir
        scaled_sequence = self.scaler.transform(sequence.reshape(-1, 1))

        # Tahmin yap
        scaled_prediction = self.model.predict(scaled_sequence.reshape(1, -1, 1))

        # Ölçeklendirmeyi geri al
        prediction = self.scaler.inverse_transform(scaled_prediction)

        return prediction[0][0]

    def save_model(self):
        """Modeli ve scaler'ı kaydeder"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        self.model.save(self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        print(f"Model ve scaler kaydedildi: {self.model_path}")import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

class LSTMPredictor:
    def __init__(self, model_path=None, sequence_length=5):
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.sequence_length = sequence_length
        self.model_path = model_path or os.path.join('models', 'prediction_models', 'lstm_model.h5')
        self.scaler_path = os.path.join('models', 'prediction_models', 'lstm_scaler.pkl')

        # Model ve scaler'ı yükle (eğer varsa)
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = load_model(self.model_path)
            self.scaler = joblib.load(self.scaler_path)

    def create_sequences(self, data, seq_length):
        """Zaman serisi verisini LSTM için uygun formata dönüştürür"""
        X, y = [], []
        for i in range(len(data) - seq_length):
            X.append(data[i:(i + seq_length)])
            y.append(data[i + seq_length])
        return np.array(X), np.array(y)

    def prepare_data(self, df, target_column='total_goals', test_size=0.2):
        """Veriyi hazırlar ve ölçeklendirir"""
        # Hedef değişkeni seç
        data = df[target_column].values.reshape(-1, 1)

        # Ölçeklendir
        scaled_data = self.scaler.fit_transform(data)

        # Zaman serisi verisini oluştur
        X, y = self.create_sequences(scaled_data, self.sequence_length)

        # Eğitim ve test setlerine ayır
        train_size = int(len(X) * (1 - test_size))
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]

        return X_train, X_test, y_train, y_test

    def build_model(self, input_shape):
        """LSTM modelini oluşturur"""
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25, activation='relu'),
            Dense(1)
        ])

        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )

        return model

    def train(self, X, y, epochs=50, batch_size=32, validation_split=0.1):
        """Modeli eğitir"""
        self.model = self.build_model((X.shape[1], X.shape[2]))

        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=1
        )

        # Modeli kaydet
        self.save_model()

        return history

    def predict(self, sequence):
        """Tahmin yapar"""
        if self.model is None:
            raise ValueError("Model henüz eğitilmemiş veya yüklenmemiş!")

        # Girişi ölçeklendir
        scaled_sequence = self.scaler.transform(sequence.reshape(-1, 1))

        # Tahmin yap
        scaled_prediction = self.model.predict(scaled_sequence.reshape(1, -1, 1))

        # Ölçeklendirmeyi geri al
        prediction = self.scaler.inverse_transform(scaled_prediction)

        return prediction[0][0]

    def save_model(self):
        """Modeli ve scaler'ı kaydeder"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        self.model.save(self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        print(f"Model ve scaler kaydedildi: {self.model_path}")import os
import joblib
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

class XGBoostPredictor:
    def __init__(self, model_path=None):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = model_path or os.path.join('models', 'prediction_models', 'xgboost_model.pkl')
        self.scaler_path = os.path.join('models', 'prediction_models', 'xgboost_scaler.pkl')

        # Model ve scaler'ı yükle (eğer varsa)
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)

    def prepare_features(self, df):
        """Veri çerçevesini modele uygun hale getirir"""
        # Gerekli özellikler
        features = [
            'home_avg_goals', 'home_avg_conceded', 'home_form',
            'away_avg_goals', 'away_avg_conceded', 'away_form',
            'h2h_avg_goals'
        ]

        # Eksik değerleri doldur
        df = df[features].fillna(0)

        # Ölçeklendirme
        if hasattr(self, 'fitted_'):
            X = self.scaler.transform(df)
        else:
            X = self.scaler.fit_transform(df)
            self.fitted_ = True

        return X

    def train(self, X, y, test_size=0.2, random_state=42):
        """Modeli eğitir"""
        # Veriyi eğitim ve test setlerine ayır
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        # Özellikleri hazırla
        X_train = self.prepare_features(pd.DataFrame(X_train))
        X_test = self.prepare_features(pd.DataFrame(X_test))

        # Modeli oluştur ve eğit
        self.model = XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )

        self.model.fit(X_train, y_train)

        # Test seti üzerinde değerlendir
        y_pred = self.model.predict(X_test)

        print("Model Eğitimi Tamamlandı")
        print(f"Doğruluk: {accuracy_score(y_test, y_pred):.2f}")
        print("\nSınıflandırma Raporu:")
        print(classification_report(y_test, y_pred))

        # Modeli kaydet
        self.save_model()

        return self

    def predict(self, X):
        """Tahmin yapar"""
        if self.model is None:
            raise ValueError("Model henüz eğitilmemiş veya yüklenmemiş!")

        # Özellikleri hazırla
        X_prepared = self.prepare_features(pd.DataFrame([X]))

        # Tahmin yap
        pred_proba = self.model.predict_proba(X_prepared)[0]
        prediction = self.model.predict(X_prepared)[0]

        return {
            'prediction': int(prediction),
            'probabilities': {
                'home_win': float(pred_proba[2]),
                'draw': float(pred_proba[1]),
                'away_win': float(pred_proba[0])
            }
        }

    def save_model(self):
        """Modeli ve scaler'ı kaydeder"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        print(f"Model ve scaler kaydedildi: {self.model_path}")<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Futbol Tahmin Sistemi</title>
    <link href="[https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"](https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css") rel="stylesheet">
    <link rel="stylesheet" href="[https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css">](https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css">)
    <style>
        .match-card {
            transition: transform 0.2s;
            margin-bottom: 1rem;
        }
        .match-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .probability-bar {
            height: 20px;
            border-radius: 10px;
            margin: 5px 0;
            overflow: hidden;
        }
        .progress {
            height: 100%;
        }
        .team-logo {
            width: 30px;
            height: 30px;
            object-fit: contain;
            margin-right: 10px;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
        <div class="container">
            <a class="navbar-brand" href="/">Futbol Tahmin Sistemi</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link active" href="/">Ana Sayfa</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#" id="trainModels">Modelleri Eğit</a>
                    </li>
                </ul>
                <div class="d-flex">
                    <select class="form-select me-2" id="leagueSelect">
                        <option value="">Tüm Ligler</option>
                    </select>
                    <input type="date" class="form-control me-2" id="dateFilter">
                    <button class="btn btn-light" id="filterBtn">Filtrele</button>
                </div>
            </div>
        </div>
    </nav>

    <div class="container">
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Maç Arama</h5>
                    </div>
                    <div class="card-body">
                        <div class="row g-3">
                            <div class="col-md-5">
                                <select class="form-select" id="homeTeamSelect">
                                    <option value="">Ev Sahibi Takım Seçin</option>
                                </select>
                            </div>
                            <div class="col-md-2 text-center align-self-center">
                                <span class="fs-4">vs</span>
                            </div>
                            <div class="col-md-5">
                                <select class="form-select" id="awayTeamSelect">
                                    <option value="">Deplasman Takımı Seçin</option>
                                </select>
                            </div>
                            <div class="col-12 text-center">
                                <button class="btn btn-primary" id="predictBtn">Tahmin Yap</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-12">
                <h4 class="mb-3">Önümüzdeki Maçlar</h4>
                <div id="loading" class="loading">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Yükleniyor...</span>
                    </div>
                    <p class="mt-2">Yükleniyor...</p>
                </div>
                <div id="matchesContainer" class="row">
                    <!-- Maç kartları buraya eklenecek -->
                </div>
            </div>
        </div>
    </div>

    <!-- Tahmin Modalı -->
    <div class="modal fade" id="predictionModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Maç Tahmini</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="predictionContent">
                    <!-- Tahmin içeriği buraya eklenecek -->
                </div>
            </div>
        </div>
    </div>

    <script src="[https://cdn.jsdelivr.net/npm/bootstrap@5.1.3](https://cdn.jsdelivr.net/npm/bootstrap@5.1.3)<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Futbol Tahmin Sistemi</title>
    <link href="[https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"](https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css") rel="stylesheet">
    <link rel="stylesheet" href="[https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css">](https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css">)
    <style>
        .match-card {
            transition: transform 0.2s;
            margin-bottom: 1rem;
        }
        .match-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .probability-bar {
            height: 20px;
            border-radius: 10px;
            margin: 5px 0;
            overflow: hidden;
        }
        .progress {
            height: 100%;
        }
        .team-logo {
            width: 30px;
            height: 30px;
            object-fit: contain;
            margin-right: 10px;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
        <div class="container">
            <a class="navbar-brand" href="/">Futbol Tahmin Sistemi</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link active" href="/">Ana Sayfa</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#" id="trainModels">Modelleri Eğit</a>
                    </li>
                </ul>
                <div class="d-flex">
                    <select class="form-select me-2" id="leagueSelect">
                        <option value="">Tüm Ligler</option>
                    </select>
                    <input type="date" class="form-control me-2" id="dateFilter">
                    <button class="btn btn-light" id="filterBtn">Filtrele</button>
                </div>
            </div>
        </div>
    </nav>

    <div class="container">
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Maç Arama</h5>
                    </div>
                    <div class="card-body">
                        <div class="row g-3">
                            <div class="col-md-5">
                                <select class="form-select" id="homeTeamSelect">
                                    <option value="">Ev Sahibi Takım Seçin</option>
                                </select>
                            </div>
                            <div class="col-md-2 text-center align-self-center">
                                <span class="fs-4">vs</span>
                            </div>
                            <div class="col-md-5">
                                <select class="form-select" id="awayTeamSelect">
                                    <option value="">Deplasman Takımı Seçin</option>
                                </select>
                            </div>
                            <div class="col-12 text-center">
                                <button class="btn btn-primary" id="predictBtn">Tahmin Yap</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-12">
                <h4 class="mb-3">Önümüzdeki Maçlar</h4>
                <div id="loading" class="loading">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Yükleniyor...</span>
                    </div>
                    <p class="mt-2">Yükleniyor...</p>
                </div>
                <div id="matchesContainer" class="row">
                    <!-- Maç kartları buraya eklenecek -->
                </div>
            </div>
        </div>
    </div>

    <!-- Tahmin Modalı -->
    <div class="modal fade" id="predictionModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Maç Tahmini</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="predictionContent">
                    <!-- Tahmin içeriği buraya eklenecek -->
                </div>
            </div>
        </div>
    </div>

    <script src="[https://cdn.jsdelivr.net/npm/bootstrap@5.1.3](https://cdn.jsdelivr.net/npm/bootstrap@5.1.3)<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Futbol Tahmin Sistemi</title>
    <link href="[https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"](https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css") rel="stylesheet">
    <link rel="stylesheet" href="[https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css">](https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css">)
    <style>
        .match-card {
            transition: transform 0.2s;
            margin-bottom: 1rem;
        }
        .match-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .probability-bar {
            height: 20px;
            border-radius: 10px;
            margin: 5px 0;
            overflow: hidden;
        }
        .progress {
            height: 100%;
        }
        .team-logo {
            width: 30px;
            height: 30px;
            object-fit: contain;
            margin-right: 10px;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
        <div class="container">
            <a class="navbar-brand" href="/">Futbol Tahmin Sistemi</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link active" href="/">Ana Sayfa</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#" id="trainModels">Modelleri Eğit</a>
                    </li>
                </ul>
                <div class="d-flex">
                    <select class="form-select me-2" id="leagueSelect">
                        <option value="">Tüm Ligler</option>
                    </select>
                    <input type="date" class="form-control me-2" id="dateFilter">
                    <button class="btn btn-light" id="filterBtn">Filtrele</button>
                </div>
            </div>
        </div>
    </nav>

    <div class="container">
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Maç Arama</h5>
                    </div>
                    <div class="card-body">
                        <div class="row g-3">
                            <div class="col-md-5">
                                <select class="form-select" id="homeTeamSelect">
                                    <option value="">Ev Sahibi Takım Seçin</option>
                                </select>
                            </div>
                            <div class="col-md-2 text-center align-self-center">
                                <span class="fs-4">vs</span>
                            </div>
                            <div class="col-md-5">
                                <select class="form-select" id="awayTeamSelect">
                                    <option value="">Deplasman Takımı Seçin</option>
                                </select>
                            </div>
                            <div class="col-12 text-center">
                                <button class="btn btn-primary" id="predictBtn">Tahmin Yap</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-12">
                <h4 class="mb-3">Önümüzdeki Maçlar</h4>
                <div id="loading" class="loading">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Yükleniyor...</span>
                    </div>
                    <p class="mt-2">Yükleniyor...</p>
                </div>
                <div id="matchesContainer" class="row">
                    <!-- Maç kartları buraya eklenecek -->
                </div>
            </div>
        </div>
    </div>

    <!-- Tahmin Modalı -->
    <div class="modal fade" id="predictionModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Maç Tahmini</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="predictionContent">
                    <!-- Tahmin içeriği buraya eklenecek -->
                </div>
            </div>
        </div>
    </div>

    <script src="[https://cdn.jsdelivr.net/npm/bootstrap@5.1.3](https://cdn.jsdelivr.net/npm/bootstrap@5.1.3)# ... mevcut importlar ...
from services.prediction_service import PredictionService

# ... mevcut kodlar ...

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    # Tahmin servisini başlat
    prediction_service = PredictionService()

    # ... mevcut route'lar ...

    # Tahmin endpoint'i
    @app.route('/api/predict', methods=['POST'])
    def predict_match():
        data = request.get_json()

        try:
            home_team_id = data['home_team_id']
            away_team_id = data['away_team_id']
            match_date = datetime.fromisoformat(data.get('match_date', datetime.utcnow().isoformat()))

            prediction = prediction_service.predict_match(home_team_id, away_team_id, match_date)

            return jsonify({
                'success': True,
                'prediction': prediction
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400

    # Model eğitme endpoint'i (sadece yönetici için)
    @app.route('/api/train', methods=['POST'])
    def train_models():
        try:
            # Tüm tamamlanmış maçları al
            matches = Match.query.filter_by(status='Finished').all()

            if not matches:
                return jsonify({
                    'success': False,
                    'error': 'Eğitim verisi bulunamadı'
                }), 400

            results = prediction_service.train_models(matches)

            return jsonify({
                'success': True,
                'results': results
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    return app# ... mevcut importlar ...
from services.prediction_service import PredictionService

# ... mevcut kodlar ...

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    # Tahmin servisini başlat
    prediction_service = PredictionService()

    # ... mevcut route'lar ...

    # Tahmin endpoint'i
    @app.route('/api/predict', methods=['POST'])
    def predict_match():
        data = request.get_json()

        try:
            home_team_id = data['home_team_id']
            away_team_id = data['away_team_id']
            match_date = datetime.fromisoformat(data.get('match_date', datetime.utcnow().isoformat()))

            prediction = prediction_service.predict_match(home_team_id, away_team_id, match_date)

            return jsonify({
                'success': True,
                'prediction': prediction
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400

    # Model eğitme endpoint'i (sadece yönetici için)
    @app.route('/api/train', methods=['POST'])
    def train_models():
        try:
            # Tüm tamamlanmış maçları al
            matches = Match.query.filter_by(status='Finished').all()

            if not matches:
                return jsonify({
                    'success': False,
                    'error': 'Eğitim verisi bulunamadı'
                }), 400

            results = prediction_service.train_models(matches)

            return jsonify({
                'success': True,
                'results': results
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    return appimport numpy as np
from models.prediction_models.xgboost_model import XGBoostModel
from models.prediction_models.lstm_model import LSTMModel
from services.data_service import DataService

class PredictionService:
    def __init__(self):
        self.xgb_model = XGBoostModel()
        self.lstm_model = LSTMModel()
        self.data_service = DataService()

    def prepare_training_data(self, matches):
        """Eğitim verilerini hazırlar"""
        X, y = [], []

        for match in matches:
            if match.status != 'Finished' or match.home_goals is None or match.away_goals is None:
                continue

            # Özellikleri çıkar
            features = self.data_service.prepare_match_features(
                match.home_team_id,
                match.away_team_id,
                match.match_date
            )

            # Etiketi belirle (0: beraberlik, 1: ev kazanır, 2: deplasman kazanır)
            if match.home_goals > match.away_goals:
                label = 1
            elif match.home_goals == match.away_goals:
                label = 0
            else:
                label = 2

            X.append(list(features.values()))
            y.append(label)

        return np.array(X), np.array(y)

    def train_models(self, matches):
        """Modelleri eğitir"""
        X, y = self.prepare_training_data(matches)

        if len(X) == 0:
            raise ValueError("Eğitim verisi bulunamadı!")

        # XGBoost modelini eğit
        self.xgb_model.train(X, y)

        # LSTM modeli için veriyi düzenle
        X_lstm = X.reshape((X.shape[0], 1, X.shape[1]))  # LSTM için 3 boyutlu hale getir
        self.lstm_model.train(X_lstm, y)

        return {
            'xgb_accuracy': self.xgb_model.evaluate(X, y)['accuracy'],
            'lstm_accuracy': self.lstm_model.evaluate(X_lstm, y)['accuracy']
        }

    def predict_match(self, home_team_id, away_team_id, match_date=None):
        """Maç tahmini yapar"""
        # Özellikleri hazırla
        features = self.data_service.prepare_match_features(
            home_team_id, away_team_id, match_date
        )
        X = np.array([list(features.values())])

        # Tahminleri yap
        xgb_pred = self.xgb_model.predict_proba(X)[0]
        lstm_pred = self.lstm_model.predict_proba(X.reshape(1, 1, -1))[0]

        # Ağırlıklı ortalama al
        pred_proba = (xgb_pred + lstm_pred) / 2

        return {
            'home_win': float(pred_proba[1]),
            'draw': float(pred_proba[0]),
            'away_win': float(pred_proba[2]),
            'goals_over_2_5': self._predict_over_2_5(features),
            'btts': self._predict_btts(features)
        }

    def _predict_over_2_5(self, features):
        """2.5 üstü gol tahmini"""
        # Basit bir örnek - gerçekte daha karmaşık bir model kullanılmalı
        total_avg_goals = (features['home_avg_goals'] + features['away_avg_goals'] +
                          features['home_avg_conceded'] + features['away_avg_conceded']) / 2import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from .base_model import BaseModel

class LSTMModel(BaseModel):
    """LSTM tabanlı dizi tahmin modeli"""

    def __init__(self, model_name="lstm_model", sequence_length=5, n_features=10):
        self.sequence_length = sequence_length
        self.n_features = n_features
        super().__init__(model_name)

    def build_model(self, n_units=64, dropout_rate=0.2, learning_rate=0.001):
        """Model mimarisini oluşturur"""
        model = Sequential([
            LSTM(n_units, input_shape=(self.sequence_length, self.n_features), return_sequences=True),
            Dropout(dropout_rate),
            LSTM(n_units // 2),
            Dropout(dropout_rate),
            Dense(64, activation='relu'),
            Dense(3, activation='softmax')  # 3 sınıf: beraberlik, ev sahibi kazanır, deplasman kazanır
        ])

        model.compile(
            optimizer=Adam(learning_rate=learning_rate),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        return model

    def train(self, X, y, epochs=50, batch_size=32, validation_split=0.2, **kwargs):
        """Modeli eğitir"""
        # Veriyi LSTM için uygun forma getir
        X_seq = self._create_sequences(X, self.sequence_length)
        y_seq = y[-len(X_seq):]  # İlk sequence_length elemanı atlandı

        # Etiketleri one-hot encoding'e çevir
        y_one_hot = tf.keras.utils.to_categorical(y_seq, num_classes=3)

        # Modeli oluştur veya yükle
        if self.model is None:
            self.model = self.build_model()

        # Modeli eğit
        history = self.model.fit(
            X_seq, y_one_hot,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            **kwargs
        )

        self.save_model()
        return history

    def predict(self, X):
        """Tahmin yapar"""
        if self.model is None:
            raise ValueError("Model eğitilmemiş!")

        X_seq = self._create_sequences(X, self.sequence_length)
        return np.argmax(self.model.predict(X_seq), axis=1)

    def predict_proba(self, X):
        """Olasılık skorlarıyla tahmin yapar"""
        if self.model is None:
            raise ValueError("Model eğitilmemiş!")

        X_seq = self._create_sequences(X, self.sequence_length)
        return self.model.predict(X_seq)

    def _create_sequences(self, data, sequence_length):
        """Veriden dizi örnekleri oluşturur"""
        sequences = []
        for i in range(len(data) - sequence_length + 1):
            sequences.append(data[i:(i + sequence_length)])
        return np.array(sequences)

    def save_model(self):
        """Modeli kaydeder"""
        if self.model is not None:
            self.model.save(self.model_path)

    def load_model(self):
        """Kayıtlı modeli yükler"""
        if os.path.exists(self.model_path):
            self.model = load_model(self.model_path)import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from .base_model import BaseModel

class LSTMModel(BaseModel):
    """LSTM tabanlı dizi tahmin modeli"""

    def __init__(self, model_name="lstm_model", sequence_length=5, n_features=10):
        self.sequence_length = sequence_length
        self.n_features = n_features
        super().__init__(model_name)

    def build_model(self, n_units=64, dropout_rate=0.2, learning_rate=0.001):
        """Model mimarisini oluşturur"""
        model = Sequential([
            LSTM(n_units, input_shape=(self.sequence_length, self.n_features), return_sequences=True),
            Dropout(dropout_rate),
            LSTM(n_units // 2),
            Dropout(dropout_rate),
            Dense(64, activation='relu'),
            Dense(3, activation='softmax')  # 3 sınıf: beraberlik, ev sahibi kazanır, deplasman kazanır
        ])

        model.compile(
            optimizer=Adam(learning_rate=learning_rate),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        return model

    def train(self, X, y, epochs=50, batch_size=32, validation_split=0.2, **kwargs):
        """Modeli eğitir"""
        # Veriyi LSTM için uygun forma getir
        X_seq = self._create_sequences(X, self.sequence_length)
        y_seq = y[-len(X_seq):]  # İlk sequence_length elemanı atlandı

        # Etiketleri one-hot encoding'e çevir
        y_one_hot = tf.keras.utils.to_categorical(y_seq, num_classes=3)

        # Modeli oluştur veya yükle
        if self.model is None:
            self.model = self.build_model()

        # Modeli eğit
        history = self.model.fit(
            X_seq, y_one_hot,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            **kwargs
        )

        self.save_model()
        return history

    def predict(self, X):
        """Tahmin yapar"""
        if self.model is None:
            raise ValueError("Model eğitilmemiş!")

        X_seq = self._create_sequences(X, self.sequence_length)
        return np.argmax(self.model.predict(X_seq), axis=1)

    def predict_proba(self, X):
        """Olasılık skorlarıyla tahmin yapar"""
        if self.model is None:
            raise ValueError("Model eğitilmemiş!")

        X_seq = self._create_sequences(X, self.sequence_length)
        return self.model.predict(X_seq)

    def _create_sequences(self, data, sequence_length):
        """Veriden dizi örnekleri oluşturur"""
        sequences = []
        for i in range(len(data) - sequence_length + 1):
            sequences.append(data[i:(i + sequence_length)])
        return np.array(sequences)

    def save_model(self):
        """Modeli kaydeder"""
        if self.model is not None:
            self.model.save(self.model_path)

    def load_model(self):
        """Kayıtlı modeli yükler"""
        if os.path.exists(self.model_path):
            self.model = load_model(self.model_path)import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from .base_model import BaseModel

class LSTMModel(BaseModel):
    """LSTM tabanlı dizi tahmin modeli"""

    def __init__(self, model_name="lstm_model", sequence_length=5, n_features=10):
        self.sequence_length = sequence_length
        self.n_features = n_features
        super().__init__(model_name)

    def build_model(self, n_units=64, dropout_rate=0.2, learning_rate=0.001):
        """Model mimarisini oluşturur"""
        model = Sequential([
            LSTM(n_units, input_shape=(self.sequence_length, self.n_features), return_sequences=True),
            Dropout(dropout_rate),
            LSTM(n_units // 2),
            Dropout(dropout_rate),
            Dense(64, activation='relu'),
            Dense(3, activation='softmax')  # 3 sınıf: beraberlik, ev sahibi kazanır, deplasman kazanır
        ])

        model.compile(
            optimizer=Adam(learning_rate=learning_rate),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        return model

    def train(self, X, y, epochs=50, batch_size=32, validation_split=0.2, **kwargs):
        """Modeli eğitir"""
        # Veriyi LSTM için uygun forma getir
        X_seq = self._create_sequences(X, self.sequence_length)
        y_seq = y[-len(X_seq):]  # İlk sequence_length elemanı atlandı

        # Etiketleri one-hot encoding'e çevir
        y_one_hot = tf.keras.utils.to_categorical(y_seq, num_classes=3)

        # Modeli oluştur veya yükle
        if self.model is None:
            self.model = self.build_model()

        # Modeli eğit
        history = self.model.fit(
            X_seq, y_one_hot,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            **kwargs
        )

        self.save_model()
        return history

    def predict(self, X):
        """Tahmin yapar"""
        if self.model is None:
            raise ValueError("Model eğitilmemiş!")

        X_seq = self._create_sequences(X, self.sequence_length)
        return np.argmax(self.model.predict(X_seq), axis=1)

    def predict_proba(self, X):
        """Olasılık skorlarıyla tahmin yapar"""
        if self.model is None:
            raise ValueError("Model eğitilmemiş!")

        X_seq = self._create_sequences(X, self.sequence_length)
        return self.model.predict(X_seq)

    def _create_sequences(self, data, sequence_length):
        """Veriden dizi örnekleri oluşturur"""
        sequences = []
        for i in range(len(data) - sequence_length + 1):
            sequences.append(data[i:(i + sequence_length)])
        return np.array(sequences)

    def save_model(self):
        """Modeli kaydeder"""
        if self.model is not None:
            self.model.save(self.model_path)

    def load_model(self):
        """Kayıtlı modeli yükler"""
        if os.path.exists(self.model_path):
            self.model = load_model(self.model_path)import xgboost as xgb
import numpy as np
from .base_model import BaseModel

class XGBoostModel(BaseModel):
    """XGBoost tabanlı sınıflandırma modeli"""

    def __init__(self, model_name="xgboost_model"):
        super().__init__(model_name)
        self.n_classes = 3  # 0: Beraberlik, 1: Ev Sahibi Kazanır, 2: Deplasman Kazanır

    def train(self, X, y, params=None):
        """Modeli eğitir"""
        if params is None:
            params = {
                'objective': 'multi:softprob',
                'num_class': self.n_classes,
                'max_depth': 6,
                'learning_rate': 0.1,
                'n_estimators': 100,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42
            }

        self.model = xgb.XGBClassifier(**params)
        self.model.fit(X, y)
        self.save_model()

    def predict(self, X):
        """Tahmin yapar"""
        if self.model is None:
            raise ValueError("Model eğitilmemiş!")
        return self.model.predict(X)

    def predict_proba(self, X):
        """Olasılık skorlarıyla tahmin yapar"""
        if self.model is None:
            raise ValueError("Model eğitilmemiş!")
        return self.model.predict_proba(X)import xgboost as xgb
import numpy as np
from .base_model import BaseModel

class XGBoostModel(BaseModel):
    """XGBoost tabanlı sınıflandırma modeli"""

    def __init__(self, model_name="xgboost_model"):
        super().__init__(model_name)
        self.n_classes = 3  # 0: Beraberlik, 1: Ev Sahibi Kazanır, 2: Deplasman Kazanır

    def train(self, X, y, params=None):
        """Modeli eğitir"""
        if params is None:
            params = {
                'objective': 'multi:softprob',
                'num_class': self.n_classes,
                'max_depth': 6,
                'learning_rate': 0.1,
                'n_estimators': 100,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42
            }

        self.model = xgb.XGBClassifier(**params)
        self.model.fit(X, y)
        self.save_model()

    deffrom abc import ABC, abstractmethod
import os
import joblib
import numpy as np
from config import Config

class BaseModel(ABC):
    """Tüm tahmin modelleri için temel sınıf"""

    def __init__(self, model_name):
        self.model_name = model_name
        self.model = None
        self.model_path = os.path.join(Config.MODEL_PATH, f"{model_name}.pkl")
        selfimport pandas as pd
import numpy as np
from datetime import datetime, timedelta
from models import db, Match, Team

class DataService:
    @staticmethod
    def get_team_recent_matches(team_id, limit=5, before_date=None):
        """Takımın son maçlarını getirir"""
        if before_date is None:
            before_date = datetime.utcnow()

        matches = Match.query.filter(
            ((Match.home_team_id == team_id) | (Match.away_team_id == team_id)) &
            (Match.status == 'Finished') &
            (Match.match_date < before_date)
        ).order_by(Match.match_date.desc()).limit(limit).all()

        return matches

    @staticmethod
    def prepare_match_features(home_team_id, away_team_id, match_date=None):
        """Maç için özellik vektörü oluşturur"""
        if match_date is None:
            match_date = datetime.utcnow()

        # Takımların son 5 maçını al
        home_matches = DataService.get_team_recent_matches(home_team_id, 5, match_date)
        away_matches = DataService.get_team_recent_matches(away_team_id, 5, match_date)

        # Özellik çıkarımı yap
        features = {
            # Ev sahibi takım özellikleri
            'home_avg_goals': DataService._calculate_avg_goals(home_matches, home_team_id),
            'home_avg_conceded': DataService._calculate_avg_conceded(home_matches, home_team_id),
            'home_form': DataService._calculate_form(home_matches, home_team_id),

            # Deplasman takımı özellikleri
            'away_avg_goals': DataService._calculate_avg_goals(away_matches, away_team_id),
            'away_avg_conceded': DataService._calculate_avg_conceded(away_matches, away_team_id),
            'away_form': DataService._calculate_form(away_matches, away_team_id),

            # Genel istatistikler
            'h2h_avg_goals': DataService._calculate_h2h_avg_goals(home_team_id, away_team_id, match_date),
        }

        return features

    @staticmethod
    def _calculate_avg_goals(matches, team_id):
        """Takımın attığı ortalama gol sayısını hesaplar"""
        if not matches:
            return 0.0

        total_goals = 0
        for match in matches:
            if match.home_team_id == team_id:
                total_goals += match.home_goals or 0
            else:
                total_goals += match.away_goals or 0

        return total_goals / len(matches)

    @staticmethod
    def _calculate_avg_conceded(matches, team_id):
        """Takımın yediği ortalama gol sayısını hesaplar"""
        if not matches:
            return 0.0

        total_conceded = 0
        for match in matches:
            if match.home_team_id == team_id:
                total_conceded += match.away_goals or 0
            else:
                total_conceded += match.home_goals or 0

        return total_conceded / len(matches)

    @staticmethod
    def _calculate_form(matches, team_id):
        """Takımın form puanını hesaplar (son 5 maçta alınan puanların ortalaması)"""
        if not matches:
            return 0.0

        total_points = 0
        for match in matches:
            if match.home_team_id == team_id:
                if match.home_goals > match.away_goals:
                    total_points += 3  # Galibiyet
                elif match.home_goals == match.away_goals:
                    total_points += 1  # Beraberlik
            else:
                if match.away_goals > match.home_goals:
                    total_points += 3  # Galibiyet
                elif match.away_goals == match.home_goals:
                    total_points += 1  # Beraberlik

        return total_points / len(matches)

    @staticmethod
    def _calculate_h2h_avg_goals(home_team_id, away_team_id, before_date, limit=5):
        """İki takım arasındaki son maçlardaki ortalama gol sayısı"""
        matches = Match.query.filter(
            ((Match.home_team_id == home_team_id) & (Match.away_team_id == away_team_id)) |
            ((Match.home_team_id == away_team_id) & (Match.away_team_id == home_team_id)),
            (Match.status == 'Finished'),
            (Match.match_date < before_date)
        ).order_by(Match.match_date.desc()).limit(limit).all()

        if not matches:
            return 2.5  # Varsayılan değer

        total_goals = sum((match.home_goals or 0) + (match.away_goals or 0) for match in matches)
        return total_goals / len(matches)from flask import Flask, render_template, jsonify, request
from models import db
from config import Config
from datetime import datetime
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Veritabanını başlat
    db.init_app(app)

    # Ana sayfa
    @app.route('/')
    def index():
        return render_template('index.html')

    # API endpoint'leri
    @app.route('/api/leagues', methods=['GET'])
    def get_leagues():
        from models import League
        leagues = League.query.all()
        return jsonify([{
            'id': league.id,
            'name': league.name,
            'country': league.country.name,
            'logo': league.logo
        } for league in leagues])

    # Diğer API endpoint'leri buraya eklenecek

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Gerekirse veritabanı tablolarını oluştur
        db.create_all()
    app.run(debug=True)import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class Config:
    # SQLAlchemy ayarları
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///football_predictions.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uygulama ayarları
    SECRET_KEY = os.getenv('SECRET_KEY', 'gizli-anahtar-buraya')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'

    # Football-Data.org API ayarları
    FOOTBALL_DATA_API_KEY = os.getenv('FOOTBALL_DATA_API_KEY', '')
    FOOTBALL_DATA_API_URL = 'https://api.football-data.org/v4/'

    # Model ayarları
    MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models/prediction_models/')
    os.makedirs(MODEL_PATH, exist_ok=True)from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Country(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(3), unique=True, nullable=False)
    flag = db.Column(db.String(255))

    # İlişkiler
    leagues = db.relationship('League', backref='country', lazy=True)
    teams = db.relationship('Team', backref='country', lazy=True)

class League(db.Model):
    __tablename__ = 'leagues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    level = db.Column(db.Integer)
    logo = db.Column(db.String(255))
    current_season = db.Column(db.String(10))

    # İlişkiler
    teams = db.relationship('Team', backref='league', lazy=True)
    matches = db.relationship('Match', backref='league', lazy=True)

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    founded = db.Column(db.Integer)
    stadium = db.Column(db.String(100))
    logo = db.Column(db.String(255))
    attack_rating = db.Column(db.Float, default=50.0)
    defense_rating = db.Column(db.Float, default=50.0)
    home_advantage = db.Column(db.Float, default=1.1)
    current_form = db.Column(db.Float, default=0.0)

    # İlişkiler
    home_matches = db.relationship('Match', foreign_keys='Match.home_team_id', backref='home_team', lazy=True)
    away_matches = db.relationship('Match', foreign_keys='Match.away_team_id', backref='away_team', lazy=True)

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    match_date = db.Column(db.DateTime, nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    season = db.Column(db.String(10))
    matchday = db.Column(db.Integer)
    status = db.Column(db.String(20))  # Scheduled, Finished, Postponed, etc.

    # Maç istatistikleri
    home_goals = db.Column(db.Integer)
    away_goals = db.Column(db.Integer)
    home_ht_goals = db.Column(db.Integer)
    away_ht_goals = db.Column(db.Integer)
    home_shots = db.Column(db.Integer)
    away_shots = db.Column(db.Integer)
    home_shots_on_target = db.Column(db.Integer)
    away_shots_on_target = db.Column(db.Integer)
    home_possession = db.Column(db.Float)
    away_possession = db.Column(db.Float)
    home_fouls = db.Column(db.Integer)
    away_fouls = db.Column(db.Integer)
    home_yellows = db.Column(db.Integer)
    away_yellows = db.Column(db.Integer)
    home_reds = db.Column(db.Integer)
    away_reds = db.Column(db.Integer)
    home_corners = db.Column(db.Integer)
    away_corners = db.Column(db.Integer)
    home_offsides = db.Column(db.Integer)
    away_offsides = db.Column(db.Integer)

    # Tahminler
    prediction_home_win = db.Column(db.Float)
    prediction_draw = db.Column(db.Float)
    prediction_away_win = db.Column(db.Float)
    prediction_goals_over_2_5 = db.Column(db.Float)
    prediction_btts = db.Column(db.Float)  # Both Teams To Score

    def __repr__(self):
        return f"<Match {self.home_team.name} {self.home_goals or '?'} - {self.away_goals or '?'} {self.away_team.name}>"from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Country(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(3), unique=True, nullable=False)
    flag = db.Column(db.String(255))

    # İlişkiler
    leagues = db.relationship('League', backref='country', lazy=True)
    teams = db.relationship('Team', backref='country', lazy=True)

class League(db.Model):
    __tablename__ = 'leagues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    level = db.Column(db.Integer)
    logo = db.Column(db.String(255))
    current_season = db.Column(db.String(10))

    # İlişkiler
    teams = db.relationship('Team', backref='league', lazy=True)
    matches = db.relationship('Match', backref='league', lazy=True)

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    founded = db.Column(db.Integer)
    stadium = db.Column(db.String(100))
    logo = db.Column(db.String(255))
    attack_rating = db.Column(db.Float, default=50.0)
    defense_rating = db.Column(db.Float, default=50.0)
    home_advantage = db.Column(db.Float, default=1.1)
    current_form = db.Column(db.Float, default=0.0)

    # İlişkiler
    home_matches = db.relationship('Match', foreign_keys='Match.home_team_id', backref='home_team', lazy=True)
    away_matches = db.relationship('Match', foreign_keys='Match.away_team_id', backref='away_team', lazy=True)

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    match_date = db.Column(db.DateTime, nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    season = db.Column(db.String(10))
    matchday = db.Column(db.Integer)
    status = db.Column(db.String(20))  # Scheduled, Finished, Postponed, etc.

    # Maç istatistikleri
    home_goals = db.Column(db.Integer)
    away_goals = db.Column(db.Integer)
    home_ht_goals = db.Column(db.Integer)
    away_ht_goals = db.Column(db.Integer)
    home_shots = db.Column(db.Integer)
    away_shots = db.Column(db.Integer)
    home_shots_on_target = db.Column(db.Integer)
    away_shots_on_target = db.Column(db.Integer)
    home_possession = db.Column(db.Float)
    away_possession = db.Column(db.Float)
    home_fouls = db.Column(db.Integer)
    away_fouls = db.Column(db.Integer)
    home_yellows = db.Column(db.Integer)
    away_yellows = db.Column(db.Integer)
    home_reds = db.Column(db.Integer)
    away_reds = db.Column(db.Integer)
    home_corners = db.Column(db.Integer)
    away_corners = db.Column(db.Integer)
    home_offsides = db.Column(db.Integer)
    away_offsides = db.Column(db.Integer)

    # Tahminler
    prediction_home_win = db.Column(db.Float)
    prediction_draw = db.Column(db.Float)
    prediction_away_win = db.Column(db.Float)
    prediction_goals_over_2_5 = db.Column(db.Float)
    prediction_btts = db.Column(db.Float)  # Both Teams To Score

    def __repr__(self):
        return f"<Match {self.home_team.name} {self.home_goals or '?'} - {self.away_goals or '?'} {self.away_team.name}>"import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class Config:
    # SQLAlchemy ayarları
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///football_predictions.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uygulama ayarları
    SECRET_KEY = os.getenv('SECRET_KEY', 'gizli-anahtar-buraya')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'

    # Football-Data.org API ayarları
    FOOTBALL_DATA_API_KEY = os.getenv('FOOTBALL_DATA_API_KEY', '')
    FOOTBALL_DATA_API_URL = 'https://api.football-data.org/v4/'

    # Model ayarları
    MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models/prediction_models/')
    os.makedirs(MODEL_PATH, exist_ok=True)from flask import Flask, render_template, jsonify, request
from models import db
from config import Config
from datetime import datetime
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Veritabanını başlat
    db.init_app(app)

    # Ana sayfa
    @app.route('/')
    def index():
        return render_template('index.html')

    # API endpoint'leri
    @app.route('/api/leagues', methods=['GET'])
    def get_leagues():
        from models import League
        leagues = League.query.all()
        return jsonify([{
            'id': league.id,
            'name': league.name,
            'country': league.country.name,
            'logo': league.logo
        } for league in leagues])

    # Diğer API endpoint'leri buraya eklenecek

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Gerekirse veritabanı tablolarını oluştur
        db.create_all()
    app.run(debug=True)import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from models import db, Match, Team

class DataService:
    @staticmethod
    def get_team_recent_matches(team_id, limit=5, before_date=None):
        """Takımın son maçlarını getirir"""
        if before_date is None:
            before_date = datetime.utcnow()

        matches = Match.query.filter(
            ((Match.home_team_id == team_id) | (Match.away_team_id == team_id)) &
            (Match.status == 'Finished') &
            (Match.match_date < before_date)
        ).order_by(Match.match_date.desc()).limit(limit).all()

        return matches

    @staticmethod
    def prepare_match_features(home_team_id, away_team_id, match_date=None):
        """Maç için özellik vektörü oluşturur"""
        if match_date is None:
            match_date = datetime.utcnow()

        # Takımların son 5 maçını al
        home_matches = DataService.get_team_recent_matches(home_team_id, 5, match_date)
        away_matches = DataService.get_team_recent_matches(away_team_id, 5, match_date)

        # Özellik çıkarımı yap
        features = {
            # Ev sahibi takım özellikleri
            'home_avg_goals': DataService._calculate_avg_goals(home_matches, home_team_id),
            'home_avg_conceded': DataService._calculate_avg_conceded(home_matches, home_team_id),
            'home_form': DataService._calculate_form(home_matches, home_team_id),

            # Deplasman takımı özellikleri
            'away_avg_goals': DataService._calculate_avg_goals(away_matches, away_team_id),
            'away_avg_conceded': DataService._calculate_avg_conceded(away_matches, away_team_id),
            'away_form': DataService._calculate_form(away_matches, away_team_id),

            # Genel istatistikler
            'h2h_avg_goals': DataService._calculate_h2h_avg_goals(home_team_id, away_team_id, match_date),
        }

        return features

    @staticmethod
    def _calculate_avg_goals(matches, team_id):
        """Takımın attığı ortalama gol sayısını hesaplar"""
        if not matches:
            return 0.0

        total_goals = 0
        for match in matches:
            if match.home_team_id == team_id:
                total_goals += match.home_goals or 0
            else:
                total_goals += match.away_goals or 0

        return total_goals / len(matches)

    @staticmethod
    def _calculate_avg_conceded(matches, team_id):
        """Takımın yediği ortalama gol sayısını hesaplar"""
        if not matches:
            return 0.0

        total_conceded = 0
        for match in matches:
            if match.home_team_id == team_id:
                total_conceded += match.away_goals or 0
            else:
                total_conceded += match.home_goals or 0

        return total_conceded / len(matches)

    @staticmethod
    def _calculate_form(matches, team_id):
        """Takımın form puanını hesaplar (son 5 maçta alınan puanların ortalaması)"""
        if not matches:
            return 0.0

        total_points = 0
        for match in matches:
            if match.home_team_id == team_id:
                if match.home_goals > match.away_goals:
                    total_points += 3  # Galibiyet
                elif match.home_goals == match.away_goals:
                    total_points += 1  # Beraberlik
            else:
                if match.away_goals > match.home_goals:
                    total_points += 3  # Galibiyet
                elif match.away_goals == match.home_goals:
                    total_points += 1  # Beraberlik

        return total_points / len(matches)

    @staticmethod
    def _calculate_h2h_avg_goals(home_team_id, away_team_id, before_date, limit=5):
        """İki takım arasındaki son maçlardaki ortalama gol sayısı"""
        matches = Match.query.filter(
            ((Match.home_team_id == home_team_id) & (Match.away_team_id == away_team_id)) |
            ((Match.home_team_id == away_team_id) & (Match.away_team_id == home_team_id)),
            (Match.status == 'Finished'),
            (Match.match_date < before_date)
        ).order_by(Match.match_date.desc()).limit(limit).all()

        if not matches:
            return 2.5  # Varsayılan değer

        total_goals = sum((match.home_goals or 0) + (match.away_goals or 0) for match in matches)
        return total_goals / len(matches)
class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    match_date = db.Column(db.DateTime, nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    season = db.Column(db.String(10))
    matchday = db.Column(db.Integer)
    status = db.Column(db.String(20))  # Scheduled, Finished, Postponed, etc.

    # Maç istatistikleri
    home_goals = db.Column(db.Integer)
    away_goals = db.Column(db.Integer)
    home_ht_goals = db.Column(db.Integer)
    away_ht_goals = db.Column(db.Integer)
    home_shots = db.Column(db.Integer)
    away_shots = db.Column(db.Integer)
    home_shots_on_target = db.Column(db.Integer)
    away_shots_on_target = db.Column(db.Integer)
    home_possession = db.Column(db.Float)
    away_possession = db.Column(db.Float)
    home_fouls = db.Column(db.Integer)
    away_fouls = db.Column(db.Integer)
    home_yellows = db.Column(db.Integer)
    away_yellows = db.Column(db.Integer)
    home_reds = db.Column(db.Integer)
    away_reds = db.Column(db.Integer)
    home_corners = db.Column(db.Integer)
    away_corners = db.Column(db.Integer)
    home_offsides = db.Column(db.Integer)
    away_offsides = db.Column(db.Integer)

    # Tahminler
    prediction_home_win = db.Column(db.Float)
    prediction_draw = db.Column(db.Float)
    prediction_away_win = db.Column(db.Float)
    prediction_goals_over_2_5 = db.Column(db.Float)
    prediction_btts = db.Column(db.Float)  # Both Teams To Score

    def __repr__(self):
        return f"<Match {self.home_team.name} {self.home_goals or '?'} - {self.away_goals or '?'} {self.away_team.name}>"from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Country(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(3), unique=True, nullable=False)
    flag = db.Column(db.String(255))

    # İlişkiler
    leagues = db.relationship('League', backref='country', lazy=True)
    teams = db.relationship('Team', backref='country', lazy=True)

class League(db.Model):
    __tablename__ = 'leagues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    level = db.Column(db.Integer)
    logo = db.Column(db.String(255))
    current_season = db.Column(db.String(10))

    # İlişkiler
    teams = db.relationship('Team', backref='league', lazy=True)
    matches = db.relationship('Match', backref='league', lazy=True)

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    founded = db.Column(db.Integer)
    stadium = db.Column(db.String(100))
    logo = db.Column(db.String(255))
    attack_rating = db.Column(db.Float, default=50.0)
    defense_rating = db.Column(db.Float, default=50.0)
    home_advantage = db.Column(db.Float, default=1.1)
    current_form = db.Column(db.Float, default=0.0)

    # İlişkiler
    home_matches = db.relationship('Match', foreign_keys='Match.home_team_id', backref='home_team', lazy=True)
    away_matches = db.relationship('Match', foreign_keys='Match.away_team_id', backref='away_team', lazy=True)

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    match_date = db.Column(db.DateTime, nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    season = db.Column(db.String(10))
    matchday = db.Column(db.Integer)
    status = db.Column(db.String(20))  # Scheduled, Finished, Postponed, etc.

    # Maç istatistikleri
    home_goals = db.Column(db.Integer)
    away_goals = db.Column(db.Integer)
    home_ht_goals = db.Column(db.Integer)
    away_ht_goals = db.Column(db.Integer)
    home_shots = db.Column(db.Integer)
    away_shots = db.Column(db.Integer)
    home_shots_on_target = db.Column(db.Integer)
    away_shots_on_target = db.Column(db.Integer)
    home_possession = db.Column(db.Float)
    away_possession = db.Column(db.Float)
    home_fouls = db.Column(db.Integer)
    away_fouls = db.Column(db.Integer)
    home_yellows = db.Column(db.Integer)
    away_yellows = db.Column(db.Integer)
    home_reds = db.Column(db.Integer)
    away_reds = db.Column(db.Integer)
    home_corners = db.Column(db.Integer)
    away_corners = db.Column(db.Integer)
    home_offsides = db.Column(db.Integer)
    away_offsides = db.Column(db.Integer)

    # Tahminler
    prediction_home_win = db.Column(db.Float)
    prediction_draw = db.Column(db.Float)
    prediction_away_win = db.Column(db.Float)
    prediction_goals_over_2_5 = db.Column(db.Float)
    prediction_btts = db.Column(db.Float)  # Both Teams To Score

    def __repr__(self):
        return f"<Match {self.home_team.name} {self.home_goals or '?'} - {self.away_goals or '?'} {self.away_team.name}>"from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Country(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(3), unique=True, nullable=False)
    flag = db.Column(db.String(255))

    # İlişkiler
    leagues = db.relationship('League', backref='country', lazy=True)
    teams = db.relationship('Team', backref='country', lazy=True)

class League(db.Model):
    __tablename__ = 'leagues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    level = db.Column(db.Integer)
    logo = db.Column(db.String(255))
    current_season = db.Column(db.String(10))

    # İlişkiler
    teams = db.relationship('Team', backref='league', lazy=True)
    matches = db.relationship('Match', backref='league', lazy=True)

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    founded = db.Column(db.Integer)
    stadium = db.Column(db.String(100))
    logo = db.Column(db.String(255))
    attack_rating = db.Column(db.Float, default=50.0)
    defense_rating = db.Column(db.Float, default=50.0)
    home_advantage = db.Column(db.Float, default=1.1)
    current_form = db.Column(db.Float, default=0.0)

    # İlişkiler
    home_matches = db.relationship('Match', foreign_keys='Match.home_team_id', backref='home_team', lazy=True)
    away_matches = db.relationship('Match', foreign_keys='Match.away_team_id', backref='away_team', lazy=True)

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    match_date = db.Column(db.DateTime, nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    season = db.Column(db.String(10))
    matchday = db.Column(db.Integer)
    status = db.Column(db.String(20))  # Scheduled, Finished, Postponed, etc.

    # Maç istatistikleri
    home_goals = db.Column(db.Integer)
    away_goals = db.Column(db.Integer)
    home_ht_goals = db.Column(db.Integer)
    away_ht_goals = db.Column(db.Integer)
    home_shots = db.Column(db.Integer)
    away_shots = db.Column(db.Integer)
    home_shots_on_target = db.Column(db.Integer)
    away_shots_on_target = db.Column(db.Integer)
    home_possession = db.Column(db.Float)
    away_possession = db.Column(db.Float)
    home_fouls = db.Column(db.Integer)
    away_fouls = db.Column(db.Integer)
    home_yellows = db.Column(db.Integer)
    away_yellows = db.Column(db.Integer)
    home_reds = db.Column(db.Integer)
    away_reds = db.Column(db.Integer)
    home_corners = db.Column(db.Integer)
    away_corners = db.Column(db.Integer)
    home_offsides = db.Column(db.Integer)
    away_offsides = db.Column(db.Integer)

    # Tahminler
    prediction_home_win = db.Column(db.Float)
    prediction_draw = db.Column(db.Float)
    prediction_away_win = db.Column(db.Float)
    prediction_goals_over_2_5 = db.Column(db.Float)
    prediction_btts = db.Column(db.Float)  # Both Teams To Score

    def __repr__(self):
        return f"<Match {self.home_team.name} {self.home_goals or '?'} - {self.away_goals or '?'} {self.away_team.name}>"recent_predictions=recent_predictions,
                         upcoming_matches=upcoming_matches)

if __name__ == '__main__':
    print("Starting Football Analysis App...")
    print("Visit http://127.0.0.1:8000 in your browser")
    app.run(host='0.0.0.0', port=8000, debug=True)
