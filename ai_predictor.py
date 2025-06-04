import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from joblib import dump, load
import os
from sqlalchemy import func, and_, or_
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

class AIPredictor:
    """Temel AI tahmin sınıfı"""
    
    def __init__(self, db_session, model_dir='ai_models'):
        self.db = db_session
        self.model_dir = model_dir
        self.model = None
        self.scaler = StandardScaler()
        self.features = [
            'home_team_strength', 'away_team_strength',
            'home_form', 'away_form',
            'home_goals_avg', 'away_goals_avg',
            'home_conceded_avg', 'away_conceded_avg'
        ]
        self._initialize_model()
    
    def _initialize_model(self):
        """Modeli yükler veya yeni oluşturur"""
        os.makedirs(self.model_dir, exist_ok=True)
        model_path = os.path.join(self.model_dir, 'match_predictor.joblib')
        
        if os.path.exists(model_path):
            self.model = load(model_path)
        else:
            self.model = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                max_depth=5
            )
    
    def get_team_form(self, team_id, match_date, is_home=True, matches=5):
        """Takımın son maç formunu hesaplar"""
        from models import Match
        
        query = self.db.session.query(Match).filter(
            or_(
                and_(Match.home_team_id == team_id, Match.status == 'Finished'),
                and_(Match.away_team_id == team_id, Match.status == 'Finished')
            ),
            Match.match_date < match_date
        ).order_by(Match.match_date.desc()).limit(matches)
        
        points = 0
        total_matches = 0
        
        for match in query:
            is_home_team = match.home_team_id == team_id
            home_goals = match.home_goals or 0
            away_goals = match.away_goals or 0
            
            if is_home_team:
                if home_goals > away_goals:
                    points += 3
                elif home_goals == away_goals:
                    points += 1
            else:
                if away_goals > home_goals:
                    points += 3
                elif away_goals == home_goals:
                    points += 1
            
            total_matches += 1
        
        return points / (total_matches * 3) if total_matches > 0 else 0.5
    
    def get_team_stats(self, team_id, match_date, is_home=True, matches=10):
        """Takım istatistiklerini hesaplar"""
        from models import Match
        
        if is_home:
            query = self.db.session.query(Match).filter(
                Match.home_team_id == team_id,
                Match.status == 'Finished',
                Match.match_date < match_date
            ).order_by(Match.match_date.desc()).limit(matches)
            
            goals_for = [m.home_goals or 0 for m in query if m.home_goals is not None]
            goals_against = [m.away_goals or 0 for m in query if m.away_goals is not None]
        else:
            query = self.db.session.query(Match).filter(
                Match.away_team_id == team_id,
                Match.status == 'Finished',
                Match.match_date < match_date
            ).order_by(Match.match_date.desc()).limit(matches)
            
            goals_for = [m.away_goals or 0 for m in query if m.away_goals is not None]
            goals_against = [m.home_goals or 0 for m in query if m.home_goals is not None]
        
        goals_avg = sum(goals_for) / len(goals_for) if goals_for else 1.5
        conceded_avg = sum(goals_against) / len(goals_against) if goals_against else 1.5
        
        return {
            'goals_avg': goals_avg,
            'conceded_avg': conceded_avg
        }
    
    def prepare_features(self, home_team_id, away_team_id, match_date):
        """Model için özellik vektörünü hazırlar"""
        home_form = self.get_team_form(home_team_id, match_date, is_home=True)
        away_form = self.get_team_form(away_team_id, match_date, is_home=False)
        
        home_stats = self.get_team_stats(home_team_id, match_date, is_home=True)
        away_stats = self.get_team_stats(away_team_id, match_date, is_home=False)
        
        features = {
            'home_team_strength': 1.0,  # Daha sonra güncellenecek
            'away_team_strength': 1.0,
            'home_form': home_form,
            'away_form': away_form,
            'home_goals_avg': home_stats['goals_avg'],
            'away_goals_avg': away_stats['goals_avg'],
            'home_conceded_avg': home_stats['conceded_avg'],
            'away_conceded_avg': away_stats['conceded_avg']
        }
        
        return pd.DataFrame([features])
    
    def train(self, matches):
        """Modeli eğitir"""
        X, y = [], []
        
        for match in matches:
            if match.status != 'Finished' or match.home_goals is None or match.away_goals is None:
                continue
                
            features = self.prepare_features(
                match.home_team_id,
                match.away_team_id,
                match.match_date
            )
            
            # Sonucu belirle (1: Ev sahibi kazandı, 0: Berabere, -1: Deplasman kazandı)
            if match.home_goals > match.away_goals:
                result = 1
            elif match.home_goals == match.away_goals:
                result = 0
            else:
                result = -1
            
            X.append(features.values[0])
            y.append(result)
        
        if not X:
            return 0.0
        
        X = np.array(X)
        y = np.array(y)
        
        # Veriyi ölçeklendir
        X_scaled = self.scaler.fit_transform(X)
        
        # Eğitim ve test setlerini ayır
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Modeli eğit
        self.model.fit(X_train, y_train)
        
        # Modeli kaydet
        model_path = os.path.join(self.model_dir, 'match_predictor.joblib')
        dump(self.model, model_path)
        
        # Doğruluk skorunu döndür
        return self.model.score(X_test, y_test)
    
    def predict(self, home_team_id, away_team_id, match_date):
        """Maç sonucunu tahmin eder"""
        features = self.prepare_features(home_team_id, away_team_id, match_date)
        
        if features.empty:
            return {
                'home_win': 0.33,
                'draw': 0.34,
                'away_win': 0.33
            }
        
        # Özellikleri ölçeklendir
        X = self.scaler.transform(features)
        
        # Tahmin olasılıklarını al
        probas = self.model.predict_proba(X)[0]
        
        # Sınıf sıralamasını kontrol et
        if hasattr(self.model, 'classes_'):
            classes = self.model.classes_
            if -1 in classes:  # away_win
                away_win_idx = list(classes).index(-1)
                draw_idx = list(classes).index(0)
                home_win_idx = list(classes).index(1)
                
                home_win = probas[home_win_idx]
                draw = probas[draw_idx]
                away_win = probas[away_win_idx]
            else:  # Sıralama farklı olabilir
                home_win, draw, away_win = probas
        else:
            home_win, draw, away_win = probas
        
        return {
            'home_win': float(home_win),
            'draw': float(draw),
            'away_win': float(away_win)
        }
    
    def predict_goals(self, home_team_id, away_team_id, match_date, max_goals=5):
        """Gol sayılarını tahmin eder (Poisson Dağılımı kullanarak)"""
        home_stats = self.get_team_stats(home_team_id, match_date, is_home=True)
        away_stats = self.get_team_stats(away_team_id, match_date, is_home=False)
        
        # Gol ortalamalarını hesapla
        home_attack = home_stats['goals_avg']
        home_defense = home_stats['conceded_avg']
        away_attack = away_stats['goals_avg']
        away_defense = away_stats['conceded_avg']
        
        # Gol beklentisi
        home_goals_exp = (home_attack + away_defense) / 2
        away_goals_exp = (away_attack + home_defense) / 2
        
        # Poisson dağılımına göre olasılıkları hesapla
        home_probs = {}
        away_probs = {}
        
        for goals in range(max_goals + 1):
            home_probs[goals] = poisson.pmf(goals, home_goals_exp)
            away_probs[goals] = poisson.pmf(goals, away_goals_exp)
        
        # En olası skoru bul
        max_prob = -1
        most_likely_score = "0-0"
        
        for h_goals in home_probs:
            for a_goals in away_probs:
                prob = home_probs[h_goals] * away_probs[a_goals]
                if prob > max_prob:
                    max_prob = prob
                    most_likely_score = f"{h_goals}-{a_goals}"
        
        return {
            'home_goals_exp': home_goals_exp,
            'away_goals_exp': away_goals_exp,
            'home_probs': home_probs,
            'away_probs': away_probs,
            'most_likely_score': most_likely_score,
            'probability': max_prob
        }
