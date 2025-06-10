from datetime import datetime
from typing import Optional, Dict, Any, List
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Column, Integer, Float, String, DateTime, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict

# Initialize SQLAlchemy
db = SQLAlchemy()

from .base import BaseModel
from app.extensions import db

class Prediction(BaseModel):
    """Maç tahminlerini yöneten model.
    
    Attributes:
        match_id: Tahmin yapılan maçın ID'si
        model_version: Kullanılan modelin versiyonu
        home_goals: Ev sahibi takımın gol tahmini
        away_goals: Deplasman takımının gol tahmini
        home_win_prob: Ev sahibi takımın kazanma olasılığı
        draw_prob: Beraberlik olasılığı
        away_win_prob: Deplasman takımının kazanma olasılığı
        over_2_5_prob: 2.5 üstü gol olasılığı
        btts_prob: İki takımın da gol atma olasılığı
        confidence: Modelin tahmindeki güven düzeyi (0-1 arası)
    """
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Temel bilgiler
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False, index=True)
    model_version = db.Column(db.String(50), nullable=False, default='1.0.0')
    
    # Skor tahminleri
    home_goals = db.Column(db.Float, nullable=False)
    away_goals = db.Column(db.Float, nullable=False)
    
    # Sonuç olasılıkları
    home_win_prob = db.Column(db.Float, nullable=False)
    draw_prob = db.Column(db.Float, nullable=False)
    away_win_prob = db.Column(db.Float, nullable=False)
    
    # Özel bahis olasılıkları
    over_2_5_prob = db.Column(db.Float, nullable=True)
    btts_prob = db.Column(db.Float, nullable=True)  # Both Teams To Score
    
    # İlk yarı tahminleri
    home_ht_goals = db.Column(db.Float, nullable=True)
    away_ht_goals = db.Column(db.Float, nullable=True)
    
    # Model güven metrikleri
    confidence = db.Column(db.Float, nullable=True)  # 0-1 arası güven skoru
    features_used = db.Column(JSON, nullable=True)  # Kullanılan özellikler
    
    # Zaman damgaları
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, nullable=False)
    
    # İlişkiler
    match = db.relationship('Match', back_populates='predictions')
    
    def __init__(self, **kwargs):
        super(Prediction, self).__init__(**kwargs)
        # Olasılıkların toplamının 1'e eşit olduğundan emin ol
        total = self.home_win_prob + self.draw_prob + self.away_win_prob
        if abs(total - 1.0) > 0.01:  # Küçük yuvarlama hatalarına izin ver
            self.home_win_prob /= total
            self.draw_prob /= total
            self.away_win_prob /= total
    
    def to_dict(self) -> Dict[str, Any]:
        """Nesneyi sözlük olarak döndürür"""
        return {
            'id': self.id,
            'match_id': self.match_id,
            'model_version': self.model_version,
            'home_goals': round(self.home_goals, 2),
            'away_goals': round(self.away_goals, 2),
            'home_win_prob': round(self.home_win_prob, 3),
            'draw_prob': round(self.draw_prob, 3),
            'away_win_prob': round(self.away_win_prob, 3),
            'over_2_5_prob': round(self.over_2_5_prob, 3) if self.over_2_5_prob else None,
            'btts_prob': round(self.btts_prob, 3) if self.btts_prob else None,
            'confidence': round(self.confidence, 3) if self.confidence else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @property
    def predicted_result(self) -> str:
        """Tahmin edilen maç sonucunu döndürür"""
        if self.home_win_prob > self.away_win_prob and self.home_win_prob > self.draw_prob:
            return '1'  # Ev sahibi kazanır
        elif self.away_win_prob > self.home_win_prob and self.away_win_prob > self.draw_prob:
            return '2'  # Deplasman kazanır
        else:
            return 'X'  # Beraberlik
    
    def get_recommended_bets(self, min_confidence: float = 0.6) -> List[Dict[str, Any]]:
        """Önerilen bahisleri döndürür"""
        if not self.confidence or self.confidence < min_confidence:
            return []
            
        bets = []
        
        # 1X2 Bahisleri
        if self.home_win_prob >= 0.5:
            bets.append({
                'type': '1X2',
                'selection': '1',
                'probability': self.home_win_prob,
                'odds': round(1 / self.home_win_prob, 2)
            })
        elif self.away_win_prob >= 0.5:
            bets.append({
                'type': '1X2',
                'selection': '2',
                'probability': self.away_win_prob,
                'odds': round(1 / self.away_win_prob, 2)
            })
            
        # Over/Under 2.5
        if self.over_2_5_prob:
            if self.over_2_5_prob >= 0.6:
                bets.append({
                    'type': 'Over/Under',
                    'selection': 'Over 2.5',
                    'probability': self.over_2_5_prob,
                    'odds': round(1 / self.over_2_5_prob, 2)
                })
            elif self.over_2_5_prob <= 0.4:
                bets.append({
                    'type': 'Over/Under',
                    'selection': 'Under 2.5',
                    'probability': 1 - self.over_2_5_prob,
                    'odds': round(1 / (1 - self.over_2_5_prob), 2)
                })
                
        # Both Teams To Score
        if self.btts_prob:
            if self.btts_prob >= 0.6:
                bets.append({
                    'type': 'BTTS',
                    'selection': 'Yes',
                    'probability': self.btts_prob,
                    'odds': round(1 / self.btts_prob, 2)
                })
            elif self.btts_prob <= 0.4:
                bets.append({
                    'type': 'BTTS',
                    'selection': 'No',
                    'probability': 1 - self.btts_prob,
                    'odds': round(1 / (1 - self.btts_prob), 2)
                })
                
        return sorted(bets, key=lambda x: x['probability'], reverse=True)
    
    def calculate_accuracy(self, actual_home_goals: int, actual_away_goals: int) -> Dict[str, float]:
        """Tahminin doğruluğunu hesaplar"""
        if actual_home_goals is None or actual_away_goals is None:
            return {}
            
        result = {}
        
        # 1X2 doğruluğu
        actual_result = self._get_result(actual_home_goals, actual_away_goals)
        predicted_result = self._get_result(round(self.home_goals), round(self.away_goals))
        result['1x2_correct'] = 1 if actual_result == predicted_result else 0
        
        # Gol farkı doğruluğu
        actual_diff = actual_home_goals - actual_away_goals
        predicted_diff = round(self.home_goals) - round(self.away_goals)
        result['exact_score'] = 1 if (actual_home_goals == round(self.home_goals) and 
                                     actual_away_goals == round(self.away_goals)) else 0
        result['correct_difference'] = 1 if actual_diff * predicted_diff > 0 else 0
        
        # Gol sayısı doğruluğu
        result['home_goals_correct'] = 1 if actual_home_goals == round(self.home_goals) else 0
        result['away_goals_correct'] = 1 if actual_away_goals == round(self.away_goals) else 0
        
        # Tam isabet kontrolü
        if (result['home_goals_correct'] == 1 and result['away_goals_correct'] == 1):
            return 5  # Tam isabet
        
        # Sonuç doğru mu? (Kazanan veya beraberlik)
        predicted_result = self._get_result(round(self.home_goals), round(self.away_goals))
        actual_result = self._get_result(actual_home_goals, actual_away_goals)
        
        if predicted_result == actual_result:
            return 3  # Sonuç doğru
            
        # Gol farkı doğru mu?
        predicted_diff = self.home_goals - self.away_goals
        actual_diff = actual_home_goals - actual_away_goals
        if predicted_diff == actual_diff:
            return 2  # Gol farkı doğru
            
        # Gol sayısı (ev sahibi veya deplasman) doğru mu?
        if self.home_goals == actual_home_goals or self.away_goals == actual_away_goals:
            return 1  # Gol sayısı doğru
            
        return 0  # Hiçbiri
    
    def _get_result(self, home_goals, away_goals):
        """Maç sonucunu belirler (H: Ev kazandı, D: Beraberlik, M: Deplasman kazandı)"""
        if home_goals > away_goals:
            return 'H'
        elif home_goals < away_goals:
            return 'M'
        else:
            return 'D'
    
    def update_accuracy(self, actual_home_goals, actual_away_goals):
        """Tahminin doğruluğunu günceller"""
        if actual_home_goals is None or actual_away_goals is None:
            return
            
        self.points_earned = self.calculate_points(actual_home_goals, actual_away_goals)
        self.is_correct = (self.points_earned > 0)
        db.session.commit()
    
    def __repr__(self):
        return f'<Prediction {self.user_id} - {self.match_id}: {self.home_goals}-{self.away_goals}>'
