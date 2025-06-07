from app.models.base import BaseModel
from app import db

class TeamStatistics(BaseModel):
    """Team statistics model for tracking team performance over time."""
    __tablename__ = 'team_statistics'
    
    # Team reference
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    season = db.Column(db.String(10), nullable=False)  # e.g., "2024-2025"
    
    # General statistics
    matches_played = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    goals_for = db.Column(db.Integer, default=0)
    goals_against = db.Column(db.Integer, default=0)
    
    # Home statistics
    home_matches = db.Column(db.Integer, default=0)
    home_wins = db.Column(db.Integer, default=0)
    home_draws = db.Column(db.Integer, default=0)
    home_losses = db.Column(db.Integer, default=0)
    home_goals_for = db.Column(db.Integer, default=0)
    home_goals_against = db.Column(db.Integer, default=0)
    
    # Away statistics
    away_matches = db.Column(db.Integer, default=0)
    away_wins = db.Column(db.Integer, default=0)
    away_draws = db.Column(db.Integer, default=0)
    away_losses = db.Column(db.Integer, default=0)
    away_goals_for = db.Column(db.Integer, default=0)
    away_goals_against = db.Column(db.Integer, default=0)
    
    # Calculated statistics
    clean_sheets = db.Column(db.Integer, default=0)  # Matches without conceding
    failed_to_score = db.Column(db.Integer, default=0)  # Matches without scoring
    
    # Relationships
    team = db.relationship('Team', back_populates='statistics')
    
    # Ensure one entry per team per season
    __table_args__ = (
        db.UniqueConstraint('team_id', 'season', name='_team_season_uc'),
    )
    
    @property
    def goal_difference(self):
        return self.goals_for - self.goals_against
    
    @property
    def points(self):
        return (self.wins * 3) + (self.draws * 1)
    
    @property
    def win_percentage(self):
        if self.matches_played == 0:
            return 0.0
        return (self.wins / self.matches_played) * 100
    
    def __repr__(self):
        return f'<TeamStatistics {self.team.name} {self.season}>'
