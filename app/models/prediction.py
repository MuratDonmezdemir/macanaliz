from app.models.base import BaseModel
from app import db

class Prediction(BaseModel):
    """Prediction model for match outcomes."""
    __tablename__ = 'predictions'
    
    # Match reference
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False, unique=True)
    
    # Prediction data
    home_goals = db.Column(db.Float, nullable=False, default=0.0)
    away_goals = db.Column(db.Float, nullable=False, default=0.0)
    home_win = db.Column(db.Float, nullable=False, default=0.0)  # Probability 0-1
    draw = db.Column(db.Float, nullable=False, default=0.0)       # Probability 0-1
    away_win = db.Column(db.Float, nullable=False, default=0.0)   # Probability 0-1
    
    # Additional prediction metrics
    over_2_5 = db.Column(db.Float)  # Probability of over 2.5 goals
    btts = db.Column(db.Float)      # Probability of both teams to score
    
    # Model information
    model_version = db.Column(db.String(50))
    confidence = db.Column(db.Float)  # Overall confidence of the prediction (0-1)
    
    # Relationships
    match = db.relationship('Match', back_populates='predictions')
    
    def __repr__(self):
        return f'<Prediction {self.match_id}: {self.home_win:.0%} - {self.draw:.0%} - {self.away_win:.0%}>'
