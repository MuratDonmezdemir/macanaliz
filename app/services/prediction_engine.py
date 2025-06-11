"""
Tahmin Motoru Modülü

Bu modül, futbol maçları için makine öğrenmesi tabanlı tahminler yapmak üzere tasarlanmıştır.
Temel olarak maç sonucu, gol sayısı ve her iki takımın da gol atıp atmayacağı gibi
çeşitli tahminleri yapabilir.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Union, Any, Tuple

import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, classification_report, confusion_matrix
)
import xgboost as xgb

# Loglama yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PredictionEngine:
    """
    Futbol maçları için tahmin motoru sınıfı.
    
    Bu sınıf, çeşitli makine öğrenmesi modellerini kullanarak
    futbol maçları için tahminler yapmayı sağlar.
    """
    
    def __init__(self, model_dir: str = 'data/models'):
        """Tahmin motorunu başlatır.
        
        Args:
            model_dir (str, optional): Modellerin kaydedileceği/okunacağı dizin. 
                                    Varsayılan: 'data/models'
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Modelleri saklamak için sözlük
        self.models = {
            'result': None,        # Maç sonucu (1-X-2)
            'over_under': None,    # Üst/Alt gol tahmini
            'btts': None,          # Her iki takım da gol atar mı?
            'correct_score': None,  # Kesin skor tahmini
            'corners': None,       # Köşe vuruşu tahmini
            'goals': None          # Gol sayısı tahmini
        }
        
        # Model metriklerini saklamak için sözlük
        self.model_metrics = {}
        
        # Her model için özellik sıralaması
        self.feature_orders = {
            'result': [
                'home_form', 'home_goals_scored_avg', 'home_goals_conceded_avg',
                'home_win_rate', 'home_draw_rate', 'home_loss_rate',
                'away_form', 'away_goals_scored_avg', 'away_goals_conceded_avg',
                'away_win_rate', 'away_draw_rate', 'away_loss_rate',
                'form_difference', 'goal_difference', 'attack_strength', 'defense_strength'
            ],
            'over_under': [
                'home_goals_scored_avg', 'home_goals_conceded_avg',
                'away_goals_scored_avg', 'away_goals_conceded_avg',
                'goal_difference', 'attack_strength', 'defense_strength',
                'match_importance', 'temperature', 'humidity'
            ],
            'btts': [
                'home_goals_scored_avg', 'home_goals_conceded_avg', 'home_clean_sheets',
                'away_goals_scored_avg', 'away_goals_conceded_avg', 'away_clean_sheets',
                'attack_strength', 'defense_strength', 'btts_last_5_home', 'btts_last_5_away'
            ]
        }
        
        # Kategorik özellikler için etiket kodlayıcılar
        self.label_encoders = {}
        
        # Kayıtlı modelleri ve metrikleri yükle
        self.load_models()
        self.load_metrics()
    
    def load_models(self) -> None:
        """Diskten tüm kayıtlı modelleri yükler."""
        for model_type in self.models.keys():
            model_path = self.model_dir / f"{model_type}_model.joblib"
            if model_path.exists():
                try:
                    self.models[model_type] = joblib.load(model_path)
                    logger.info(f"{model_type} modeli başarıyla yüklendi: {model_path}")
                except Exception as e:
                    logger.error(f"{model_type} modeli yüklenirken hata oluştu: {e}")
    
    def save_models(self) -> None:
        """Tüm modelleri diske kaydeder."""
        for model_type, model in self.models.items():
            if model is not None:
                try:
                    model_path = self.model_dir / f"{model_type}_model.joblib"
                    joblib.dump(model, model_path)
                    logger.info(f"{model_type} modeli başarıyla kaydedildi: {model_path}")
                except Exception as e:
                    logger.error(f"{model_type} modeli kaydedilirken hata oluştu: {e}")
    
    def load_metrics(self) -> None:
        """Model metriklerini diskten yükler."""
        metrics_path = self.model_dir / "model_metrics.json"
        if metrics_path.exists():
            try:
                with open(metrics_path, 'r', encoding='utf-8') as f:
                    self.model_metrics = json.load(f)
                logger.info(f"Model metrikleri başarıyla yüklendi: {metrics_path}")
            except Exception as e:
                logger.error(f"Model metrikleri yüklenirken hata oluştu: {e}")
    
    def save_metrics(self) -> None:
        """Model metriklerini diske kaydeder."""
        metrics_path = self.model_dir / "model_metrics.json"
        try:
            with open(metrics_path, 'w', encoding='utf-8') as f:
                json.dump(self.model_metrics, f, indent=2, ensure_ascii=False)
            logger.info(f"Model metrikleri başarıyla kaydedildi: {metrics_path}")
        except Exception as e:
            logger.error(f"Model metrikleri kaydedilirken hata oluştu: {e}")