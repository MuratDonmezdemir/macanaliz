from ..extensions import db
from .base import BaseModel
from .enums import PredictionOutcome

class Prediction(BaseModel):
    """Maç tahminlerini temsil eden model."""
    __tablename__ = 'predictions'
    
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    predicted_outcome = db.Column(db.Enum(PredictionOutcome), nullable=False)
    home_goals_predicted = db.Column(db.Integer)
    away_goals_predicted = db.Column(db.Integer)
    confidence = db.Column(db.Float)  # 0-1 arası güven skoru
    
    # Tahminin doğruluğu (maçtan sonra doldurulacak)
    is_correct = db.Column(db.Boolean)
    
    def __repr__(self):
        return f'<Prediction {self.match_id} - {self.predicted_outcome}>'
