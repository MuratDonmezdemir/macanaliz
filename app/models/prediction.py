from datetime import datetime

from sqlalchemy import ForeignKey

from .base import BaseModel
from app.extensions import db

class Prediction(BaseModel):
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    home_goals = db.Column(db.Integer, nullable=False)
    away_goals = db.Column(db.Integer, nullable=False)
    is_correct = db.Column(db.Boolean, default=None, nullable=True)
    points_earned = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # İlişkiler
    match = db.relationship(
        'Match',
        back_populates='predictions',
        foreign_keys='Prediction.match_id'
    )
    user = db.relationship(
        'User',
        back_populates='predictions',
        foreign_keys='Prediction.user_id'
    )
    
    def calculate_points(self, actual_home_goals, actual_away_goals):
        """Tahmin puanını hesaplar"""
        if actual_home_goals is None or actual_away_goals is None:
            return 0
            
        # Sonuç doğru mu? (Kazanan veya beraberlik)
        predicted_result = self._get_result(self.home_goals, self.away_goals)
        actual_result = self._get_result(actual_home_goals, actual_away_goals)
        
        # Skor tam olarak tutuyor mu?
        if self.home_goals == actual_home_goals and self.away_goals == actual_away_goals:
            return 5  # Tam isabet
        
        # Sonuç doğru mu? (Kazanan veya beraberlik)
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
