from datetime import datetime
from typing import List, Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .team_statistics import TeamStatistics
from .base import BaseModel
from app.extensions import db
from sqlalchemy.orm import relationship, backref

class Team(BaseModel):
    """Futbol takımı modeli
    
    Attributes:
        name (str): Takımın tam adı
        short_name (str): Takımın kısa adı
        country (str): Ülke adı
        city (str): Şehir adı
        founded (int): Kuruluş yılı
        logo (str): Logo URL'si
        website (str): Resmi web sitesi
        colors (str): Takım renkleri (JSON formatında)
        coach (str): Teknik direktör adı
        is_national (bool): Milli takım mı?
    """
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    short_name = db.Column(db.String(20))
    country = db.Column(db.String(50))
    city = db.Column(db.String(50))
    founded = db.Column(db.Integer)
    logo = db.Column(db.String(200))
    stadium_id = db.Column(db.Integer, db.ForeignKey('stadiums.id'))
    website = db.Column(db.String(200))
    colors = db.Column(db.String(100))  # JSON formatında renkler
    coach = db.Column(db.String(100))
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'))
    
    # League ilişkisi backref ile tanımlanıyor
    is_national = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    home_matches = db.relationship(
        'Match', 
        foreign_keys='Match.home_team_id', 
        backref=db.backref('home_team', lazy='joined'), 
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    away_matches = db.relationship(
        'Match', 
        foreign_keys='Match.away_team_id', 
        backref=db.backref('away_team', lazy='joined'), 
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    players = db.relationship(
        'Player', 
        backref='team',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    statistics = db.relationship(
        'TeamStatistics', 
        backref='team_stats',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    # League ve Stadium ilişkileri backref ile tanımlanıyor
    
    def __repr__(self):
        return f'<Team {self.name}>'
    
    def to_dict(self):
        """Takım bilgilerini sözlük olarak döndürür"""
        return {
            'id': self.id,
            'name': self.name,
            'short_name': self.short_name,
            'country': self.country,
            'logo': self.logo,
            'stadium': self.stadium.name if self.stadium else None,
            'league': self.league.name if self.league else None,
            'founded': self.founded,
            'coach': self.coach
        }
    
    def get_season_statistics(self, season_id: int) -> Optional[Any]:
        """Belirtilen sezon için takım istatistiklerini getirir
        
        Args:
            season_id (int): Sezon ID'si
            
        Returns:
            Optional[TeamStatistics]: İlgili sezon istatistikleri veya None
        """
        from .team_statistics import TeamStatistics
        return self.statistics.filter_by(season_id=season_id).first()
    
    def update_statistics(self, match_result: str, is_home: bool, goals_for: int, 
                         goals_against: int, season_id: int) -> None:
        """Takım istatistiklerini günceller
        
        Args:
            match_result (str): Maç sonucu ('W'=Galibiyet, 'D'=Beraberlik, 'L'=Mağlubiyet)
            is_home (bool): İç saha maçı mı?
            goals_for (int): Atılan gol sayısı
            goals_against (int): Yenilen gol sayısı
            season_id (int): Sezon ID'si
        """
        stats = self.get_season_statistics(season_id)
        if not stats:
            from . import season
            stats = TeamStatistics(
                team_id=self.id,
                season_id=season_id
            )
            db.session.add(stats)
        
        # Temel istatistikleri güncelle
        stats.total_matches += 1
        if match_result == 'W':
            stats.wins += 1
        elif match_result == 'D':
            stats.draws += 1
        else:
            stats.losses += 1
            
        # Gol istatistikleri
        stats.goals_scored += goals_for
        stats.goals_conceded += goals_against
        
        # Temiz kale durumu
        if goals_against == 0:
            stats.clean_sheets += 1
            
        # Form durumunu güncelle
        stats.update_form(match_result)
        stats.last_updated = datetime.utcnow()
        
        db.session.commit()
    
    def get_recent_matches(self, limit: int = 5) -> List[Any]:
        """Takımın son maçlarını getirir
        
        Args:
            limit (int): Getirilecek maç sayısı
            
        Returns:
            List[Match]: Son maçların listesi
        """
        from .match import Match
        return Match.query.filter(
            (Match.home_team_id == self.id) | (Match.away_team_id == self.id)
        ).order_by(Match.match_date.desc()).limit(limit).all()
    
    def get_next_match(self):
        """Takımın bir sonraki maçını getirir"""
        return Match.query.filter(
            ((Match.home_team_id == self.id) | (Match.away_team_id == self.id)) &
            (Match.status == 'SCHEDULED')
        ).order_by(Match.match_date.asc()).first()
    
    def get_standings(self, season_id):
        """Takımın lig sıralamasındaki durumunu getirir"""
        from .standing import Standing
        return Standing.query.filter_by(
            team_id=self.id,
            season_id=season_id
        ).first()
    
    def get_statistics(self):
        """Takım istatistiklerini getirir"""
        from .match import MatchStatistics
        return MatchStatistics.query.filter_by(team_id=self.id).first()
