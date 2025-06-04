import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from joblib import load, dump
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os

class MatchPredictor:
    def __init__(self, db_session):
        self.db = db_session
        self.model = None
        self.model_path = 'models/match_predictor.joblib'
        self._initialize_model()

    def _initialize_model(self):
        """Initialize or load the prediction model"""
        if os.path.exists(self.model_path):
            self.model = load(self.model_path)
        else:
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            os.makedirs('models', exist_ok=True)

    def save_model(self):
        """Save the trained model to disk"""
        if self.model:
            dump(self.model, self.model_path)

    def get_team_form(self, team_id, match_date, matches_back=5):
        """Get team's form (last n matches) before the given date"""
        matches = self.db.session.query(Match).filter(
            ((Match.home_team_id == team_id) | (Match.away_team_id == team_id)),
            Match.match_date < match_date,
            Match.status == 'Finished'
        ).order_by(Match.match_date.desc()).limit(matches_back).all()

        form = []
        for match in matches:
            if match.home_team_id == team_id:
                if match.home_goals > match.away_goals:
                    form.append('W')
                elif match.home_goals == match.away_goals:
                    form.append('D')
                else:
                    form.append('L')
            else:
                if match.away_goals > match.home_goals:
                    form.append('W')
                elif match.away_goals == match.home_goals:
                    form.append('D')
                else:
                    form.append('L')
        
        # Pad with None if not enough matches
        while len(form) < matches_back:
            form.append(None)
            
        return form[:matches_back]

    def prepare_match_data(self, home_team_id, away_team_id, match_date):
        """Prepare feature vector for prediction"""
        home_form = self.get_team_form(home_team_id, match_date)
        away_form = self.get_team_form(away_team_id, match_date)
        
        # Convert form to features (count of W/D/L in last 5 matches)
        def form_to_features(form):
            return [
                form.count('W'),
                form.count('D'),
                form.count('L'),
                len([x for x in form if x is not None])  # Number of matches available
            ]
        
        home_features = form_to_features(home_form)
        away_features = form_to_features(away_form)
        
        # Combine features
        features = home_features + away_features
        
        return np.array(features).reshape(1, -1)

    def predict_match(self, home_team_id, away_team_id, match_date=None):
        """Predict match outcome"""
        if match_date is None:
            match_date = datetime.now()
            
        # Prepare features
        X = self.prepare_match_data(home_team_id, away_team_id, match_date)
        
        # Make prediction
        if self.model:
            proba = self.model.predict_proba(X)[0]
            prediction = self.model.predict(X)[0]
            
            return {
                'home_win_prob': float(proba[0]),
                'draw_prob': float(proba[1]),
                'away_win_prob': float(proba[2]),
                'prediction': ['Home Win', 'Draw', 'Away Win'][prediction]
            }
        return None

    def train_model(self, matches):
        """Train the prediction model on historical matches"""
        X = []
        y = []
        
        for match in matches:
            if match.status != 'Finished' or match.home_goals is None or match.away_goals is None:
                continue
                
            # Prepare features
            try:
                features = self.prepare_match_data(
                    match.home_team_id, 
                    match.away_team_id,
                    match.match_date
                )
                
                # Determine outcome (0: home win, 1: draw, 2: away win)
                if match.home_goals > match.away_goals:
                    outcome = 0
                elif match.home_goals == match.away_goals:
                    outcome = 1
                else:
                    outcome = 2
                
                X.append(features[0])  # Flatten the features
                y.append(outcome)
                
            except Exception as e:
                print(f"Error processing match {match.id}: {e}")
        
        if not X:
            print("No valid match data for training")
            return
        
        # Train the model
        X = np.array(X)
        y = np.array(y)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Model trained with accuracy: {accuracy:.2f}")
        
        # Save the trained model
        self.save_model()
        
        return accuracy
