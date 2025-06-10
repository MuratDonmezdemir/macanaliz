from datetime import datetime
from .base import BaseModel
from app.extensions import db

class Standing(BaseModel):
    """Puan durumu modeli"""
    __tablename__ = 'standings'
    __table_args__ = {'extend_existing': True}  # Mevcut tabloyu genişlet
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('seasons.id'), nullable=False)
    played = db.Column(db.Integer, default=0)
    won = db.Column(db.Integer, default=0)
    drawn = db.Column(db.Integer, default=0)
    lost = db.Column(db.Integer, default=0)
    goals_for = db.Column(db.Integer, default=0)
    goals_against = db.Column(db.Integer, default=0)
    goal_difference = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)
    position = db.Column(db.Integer)
    form = db.Column(db.String(10))  # Son 5 maç formu (Örn: "WWDLD")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    team = db.relationship('Team', back_populates='standings')
    season = db.relationship('Season', back_populates='standings')
    
    def __repr__(self):
        return f'<Standing {self.team.name} - {self.season.name}>'
    
    def to_dict(self):
        """Puan durumu bilgilerini sözlük olarak döndürür"""
        return {
            'id': self.id,
            'team_id': self.team_id,
            'team_name': self.team.name,
            'team_logo': self.team.logo,
            'season_id': self.season_id,
            'season_name': self.season.name,
            'played': self.played,
            'won': self.won,
            'drawn': self.drawn,
            'lost': self.lost,
            'goals_for': self.goals_for,
            'goals_against': self.goals_against,
            'goal_difference': self.goal_difference,
            'points': self.points,
            'position': self.position,
            'form': self.form
        }
