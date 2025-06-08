import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import os
from datetime import datetime
from typing import Dict, Tuple, List, Optional
import logging

# Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MatchPredictor:
    """Futbol maç tahmini için makine öğrenmesi modeli"""
    
    def __init__(self, model_type: str = 'xgb', model_dir: str = 'models'):
        """
        Args:
            model_type: Kullanılacak model türü ('rf', 'xgb', 'lgbm', 'catboost')
            model_dir: Modellerin kaydedileceği dizin
        """
        self.model_type = model_type
        self.model_dir = model_dir
        os.makedirs(self.model_dir, exist_ok=True)
        self.model = self._init_model()
        self.features = [
            'home_team_strength', 'away_team_strength',
            'home_last_5_avg_goals', 'away_last_5_avg_goals',
            'home_last_5_avg_conceded', 'away_last_5_avg_conceded',
            'home_form', 'away_form',
            'head_to_head_home_wins', 'head_to_head_draws', 'head_to_head_away_wins',
            'home_team_rank', 'away_team_rank',
            'days_since_last_match_home', 'days_since_last_match_away'
        ]
        self.targets = ['home_goals', 'away_goals']
    
    def _init_model(self):
        """Modeli başlat"""
        if self.model_type == 'rf':
            return RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        elif self.model_type == 'xgb':
            return XGBRegressor(n_estimators=200, random_state=42, n_jobs=-1)
        elif self.model_type == 'lgbm':
            return LGBMRegressor(n_estimators=200, random_state=42, n_jobs=-1)
        elif self.model_type == 'catboost':
            return CatBoostRegressor(iterations=200, random_seed=42, verbose=0)
        else:
            raise ValueError(f"Bilinmeyen model türü: {self.model_type}")
    
    def prepare_features(self, matches: List[Dict], team_stats: Dict) -> Tuple[pd.DataFrame, pd.Series]:
        """Ham maç verilerinden özellikler hazırlar"""
        X = []
        y = []
        
        for i in range(1, len(matches)):
            match = matches[i]
            prev_matches = matches[max(0, i-5):i]  # Son 5 maç
            
            # Takım güçleri
            home_team_id = match['home_team_id']
            away_team_id = match['away_team_id']
            
            # Son 5 maç istatistikleri
            home_last_5 = [m for m in prev_matches if m['home_team_id'] == home_team_id or m['away_team_id'] == home_team_id][-5:]
            away_last_5 = [m for m in prev_matches if m['home_team_id'] == away_team_id or m['away_team_id'] == away_team_id][-5:]
            
            # Özellikler
            features = {
                'home_team_strength': team_stats.get(home_team_id, {}).get('strength', 0),
                'away_team_strength': team_stats.get(away_team_id, {}).get('strength', 0),
                'home_last_5_avg_goals': self._calculate_avg_goals(home_team_id, home_last_5, is_home=True),
                'away_last_5_avg_goals': self._calculate_avg_goals(away_team_id, away_last_5, is_home=False),
                'home_last_5_avg_conceded': self._calculate_avg_conceded(home_team_id, home_last_5, is_home=True),
                'away_last_5_avg_conceded': self._calculate_avg_conceded(away_team_id, away_last_5, is_home=False),
                'home_form': self._calculate_form(home_team_id, home_last_5),
                'away_form': self._calculate_form(away_team_id, away_last_5),
                'head_to_head_home_wins': 0,  # Bu verileri head-to-head analizinden doldur
                'head_to_head_draws': 0,
                'head_to_head_away_wins': 0,
                'home_team_rank': team_stats.get(home_team_id, {}).get('rank', 20),
                'away_team_rank': team_stats.get(away_team_id, {}).get('rank', 20),
                'days_since_last_match_home': self._days_since_last_match(home_team_id, match['match_date'], prev_matches),
                'days_since_last_match_away': self._days_since_last_match(away_team_id, match['match_date'], prev_matches)
            }
            
            X.append([features[col] for col in self.features])
            y.append([match['home_goals'], match['away_goals']])
        
        return pd.DataFrame(X, columns=self.features), np.array(y)
    
    def _calculate_avg_goals(self, team_id: int, matches: List[Dict], is_home: bool) -> float:
        """Takımın ortalama gol sayısını hesaplar"""
        if not matches:
            return 1.5  # Varsayılan değer
            
        total_goals = 0
        for match in matches:
            if match['home_team_id'] == team_id:
                total_goals += match['home_goals']
            else:
                total_goals += match['away_goals']
                
        return total_goals / len(matches)
    
    def _calculate_avg_conceded(self, team_id: int, matches: List[Dict], is_home: bool) -> float:
        """Takımın ortalama yediği gol sayısını hesaplar"""
        if not matches:
            return 1.0  # Varsayılan değer
            
        total_conceded = 0
        for match in matches:
            if match['home_team_id'] == team_id:
                total_conceded += match['away_goals']
            else:
                total_conceded += match['home_goals']
                
        return total_conceded / len(matches)
    
    def _calculate_form(self, team_id: int, matches: List[Dict]) -> float:
        """Takımın formunu hesaplar (1-5 arası değer)"""
        if not matches:
            return 2.5  # Nötr form
            
        form = 0
        for match in matches[-5:]:  # Son 5 maç
            if match['home_team_id'] == team_id:
                if match['home_goals'] > match['away_goals']:
                    form += 1
                elif match['home_goals'] == match['away_goals']:
                    form += 0.5
            else:
                if match['away_goals'] > match['home_goals']:
                    form += 1
                elif match['away_goals'] == match['home_goals']:
                    form += 0.5
                    
        return min(5, form)  # Maksimum 5 puan
    
    def _days_since_last_match(self, team_id: int, current_date: str, prev_matches: List[Dict]) -> int:
        """Son maçtan bu yana geçen gün sayısını hesaplar"""
        if not prev_matches:
            return 7  # Varsayılan değer
            
        last_match = None
        for match in reversed(prev_matches):
            if match['home_team_id'] == team_id or match['away_team_id'] == team_id:
                last_match = match
                break
                
        if not last_match:
            return 14  # Eğer önceki maç yoksa
            
        last_date = datetime.strptime(last_match['match_date'], '%Y-%m-%d')
        current_date = datetime.strptime(current_date, '%Y-%m-%d')
        return (current_date - last_date).days
    
    def train(self, X: pd.DataFrame, y: np.ndarray, test_size: float = 0.2):
        """Modeli eğitir"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Modeli eğit
        self.model.fit(X_train, y_train)
        
        # Test seti üzerinde değerlendir
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        logger.info(f"Eğitim skoru: {train_score:.4f}")
        logger.info(f"Test skoru: {test_score:.4f}")
        
        return X_test, y_test
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Tahmin yapar"""
        return self.model.predict(X)
    
    def save_model(self, filename: str = None):
        """Modeli kaydeder"""
        if filename is None:
            filename = f"match_predictor_{self.model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.joblib"
        
        model_path = os.path.join(self.model_dir, filename)
        joblib.dump(self.model, model_path)
        logger.info(f"Model kaydedildi: {model_path}")
        return model_path
    
    def load_model(self, model_path: str):
        """Kaydedilmiş modeli yükler"""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model dosyası bulunamadı: {model_path}")
            
        self.model = joblib.load(model_path)
        logger.info(f"Model yüklendi: {model_path}")
        return self
