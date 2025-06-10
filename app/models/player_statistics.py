"""Player statistics model to track player performance metrics"""
from datetime import datetime
from typing import Dict, Any, Optional
from decimal import Decimal
from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey, String, Date, Numeric, CheckConstraint
from sqlalchemy.orm import relationship

from .base import BaseModel
from app.extensions import db


class PlayerStatistics(BaseModel):
    """Tracks player statistics for a specific season and competition"""
    __tablename__ = 'player_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Relationships
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False, index=True)
    season_id = db.Column(db.Integer, db.ForeignKey('seasons.id'), nullable=False, index=True)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), index=True)
    
    # Appearances
    appearances = db.Column(db.Integer, default=0)  # Toplam maç
    starts = db.Column(db.Integer, default=0)  # İlk 11'de başlama
    minutes_played = db.Column(db.Integer, default=0)  # Toplam dakika
    
    # Goals and assists
    goals = db.Column(db.Integer, default=0)  # Attığı goller
    assists = db.Column(db.Integer, default=0)  # Asist sayısı
    goals_conceded = db.Column(db.Integer, default=0)  # Yediği gol (kaleci/defans için)
    clean_sheets = db.Column(db.Integer, default=0)  # Kalesinde gol yemediği maç (kaleci/defans için)
    
    # Shots
    shots = db.Column(db.Integer, default=0)  # Şut
    shots_on_target = db.Column(db.Integer, default=0)  # İsabetli şut
    shot_accuracy = db.Column(db.Float)  # İsabet yüzdesi
    
    # Passing
    passes = db.Column(db.Integer, default=0)  # Toplam pas
    pass_accuracy = db.Column(db.Float)  # Pas isabet yüzdesi
    key_passes = db.Column(db.Integer, default=0)  # Kritik pas
    crosses = db.Column(db.Integer, default=0)  # Orta
    cross_accuracy = db.Column(db.Float)  # Orta isabet yüzdesi
    
    # Defensive
    tackles = db.Column(db.Integer, default=0)  # Top kapma
    interceptions = db.Column(db.Integer, default=0)  # Top kesme
    clearances = db.Column(db.Integer, default=0)  # Topu uzaklaştırma
    blocks = db.Column(db.Integer, default=0)  # Şut engelleme
    
    # Discipline
    yellow_cards = db.Column(db.Integer, default=0)  # Sarı kart
    red_cards = db.Column(db.Integer, default=0)  # Kırmızı kart
    fouls_committed = db.Column(db.Integer, default=0)  # Yapılan faul
    fouls_suffered = db.Column(db.Integer, default=0)  # Yenen faul
    offsides = db.Column(db.Integer, default=0)  # Ofsayt
    
    # Goalkeeping
    saves = db.Column(db.Integer, default=0)  # Kurtarış (kaleci)
    penalties_saved = db.Column(db.Integer, default=0)  # Penaltı kurtarışı
    punches = db.Column(db.Integer, default=0)  # Yumruklama
    high_claims = db.Column(db.Integer, default=0)  # Yüksek toplarda müdahale
    
    # Advanced metrics
    duels_won = db.Column(db.Integer, default=0)  # Kazanılan ikili mücadele
    duels_lost = db.Column(db.Integer, default=0)  # Kaybedilen ikili mücadele
    aerial_duels_won = db.Column(db.Integer, default=0)  # Havada kazanılan ikili mücadele
    dribbles_attempted = db.Column(db.Integer, default=0)  # Denenen dripling
    successful_dribbles = db.Column(db.Integer, default=0)  # Başarılı dripling
    
    # Physical
    distance_covered = db.Column(db.Float)  # Toplam koşu mesafesi (km)
    sprints = db.Column(db.Integer, default=0)  # Sürat koşusu sayısı
    
    # Ratings
    average_rating = db.Column(db.Float)  # Maç başına ortalama performans puanı
    man_of_the_match = db.Column(db.Integer, default=0)  # Maçın adamı seçilme sayısı
    
    # System fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    player = relationship('Player', back_populates='statistics')
    team = relationship('Team')
    season = relationship('Season')
    competition = relationship('Competition')
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('player_id', 'season_id', 'competition_id', name='_player_season_competition_uc'),
    )
    
    def __init__(self, **kwargs):
        super(PlayerStatistics, self).__init__(**kwargs)
        self.calculate_derived_stats()
    
    def calculate_derived_stats(self):
        """Türetilmiş istatistikleri hesapla"""
        # Şut isabet yüzdesi
        if self.shots > 0:
            self.shot_accuracy = round((self.shots_on_target / self.shots) * 100, 1)
        
        # Pas isabet yüzdesi
        if self.passes > 0:
            self.pass_accuracy = round((self.passes - self.passes * 0.1) / self.passes * 100, 1)  # Basit bir hesaplama
        
        # Orta isabet yüzdesi
        if self.crosses > 0:
            self.cross_accuracy = round((self.crosses - self.crosses * 0.3) / self.crosses * 100, 1)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert statistics to dictionary"""
        return {
            'id': self.id,
            'player_id': self.player_id,
            'team_id': self.team_id,
            'season_id': self.season_id,
            'competition_id': self.competition_id,
            'season_name': self.season.name if self.season else None,
            'competition_name': self.competition.name if self.competition else None,
            
            # Appearances
            'appearances': self.appearances,
            'starts': self.starts,
            'minutes_played': self.minutes_played,
            'minutes_per_game': round(self.minutes_played / self.appearances, 1) if self.appearances > 0 else 0,
            
            # Goals and assists
            'goals': self.goals,
            'assists': self.assists,
            'goals_conceded': self.goals_conceded,
            'clean_sheets': self.clean_sheets,
            'goals_per_game': round(self.goals / self.appearances, 2) if self.appearances > 0 else 0,
            'assists_per_game': round(self.assists / self.appearances, 2) if self.appearances > 0 else 0,
            
            # Shots
            'shots': self.shots,
            'shots_on_target': self.shots_on_target,
            'shot_accuracy': self.shot_accuracy,
            'conversion_rate': round((self.goals / self.shots) * 100, 1) if self.shots > 0 else 0,
            
            # Passing
            'passes': self.passes,
            'pass_accuracy': self.pass_accuracy,
            'key_passes': self.key_passes,
            'key_passes_per_game': round(self.key_passes / self.appearances, 1) if self.appearances > 0 else 0,
            'crosses': self.crosses,
            'cross_accuracy': self.cross_accuracy,
            
            # Defensive
            'tackles': self.tackles,
            'tackles_per_game': round(self.tackles / self.appearances, 1) if self.appearances > 0 else 0,
            'interceptions': self.interceptions,
            'clearances': self.clearances,
            'blocks': self.blocks,
            
            # Discipline
            'yellow_cards': self.yellow_cards,
            'red_cards': self.red_cards,
            'fouls_committed': self.fouls_committed,
            'fouls_suffered': self.fouls_suffered,
            'offsides': self.offsides,
            
            # Goalkeeping
            'saves': self.saves,
            'saves_per_game': round(self.saves / self.appearances, 1) if self.appearances > 0 else 0,
            'penalties_saved': self.penalties_saved,
            'punches': self.punches,
            'high_claims': self.high_claims,
            
            # Advanced metrics
            'duels_won': self.duels_won,
            'duels_lost': self.duels_lost,
            'duel_success_rate': round((self.duels_won / (self.duels_won + self.duels_lost)) * 100, 1) 
                                if (self.duels_won + self.duels_lost) > 0 else 0,
            'aerial_duels_won': self.aerial_duels_won,
            'dribbles_attempted': self.dribbles_attempted,
            'successful_dribbles': self.successful_dribbles,
            'dribble_success_rate': round((self.successful_dribbles / self.dribbles_attempted) * 100, 1) 
                                   if self.dribbles_attempted > 0 else 0,
            
            # Physical
            'distance_covered': self.distance_covered,
            'distance_per_game': round(self.distance_covered / self.appearances, 1) 
                                if self.distance_covered and self.appearances > 0 else 0,
            'sprints': self.sprints,
            
            # Ratings
            'average_rating': round(self.average_rating, 2) if self.average_rating else 0,
            'man_of_the_match': self.man_of_the_match,
            
            # System
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def update_from_match_performance(self, match_stats: Dict[str, Any]):
        """Update statistics based on match performance"""
        # Update basic stats
        self.appearances += 1
        self.minutes_played += match_stats.get('minutes_played', 0)
        
        # Update goals and assists
        self.goals += match_stats.get('goals', 0)
        self.assists += match_stats.get('assists', 0)
        
        # Update defensive stats
        self.tackles += match_stats.get('tackles', 0)
        self.interceptions += match_stats.get('interceptions', 0)
        self.clearances += match_stats.get('clearances', 0)
        self.blocks += match_stats.get('blocks', 0)
        
        # Update discipline
        self.yellow_cards += match_stats.get('yellow_cards', 0)
        self.red_cards += match_stats.get('red_cards', 0)
        self.fouls_committed += match_stats.get('fouls_committed', 0)
        self.fouls_suffered += match_stats.get('fouls_suffered', 0)
        
        # Update shots and passing
        self.shots += match_stats.get('shots', 0)
        self.shots_on_target += match_stats.get('shots_on_target', 0)
        self.passes += match_stats.get('passes', 0)
        self.key_passes += match_stats.get('key_passes', 0)
        
        # Update other metrics
        self.distance_covered = (self.distance_covered or 0) + match_stats.get('distance_covered', 0)
        self.sprints += match_stats.get('sprints', 0)
        
        # Recalculate derived stats
        self.calculate_derived_stats()
        
        # Update average rating
        match_rating = match_stats.get('rating', 0)
        if match_rating > 0:
            if self.average_rating is None:
                self.average_rating = match_rating
            else:
                total_matches = self.appearances - 1  # Current match not yet counted
                self.average_rating = (
                    (self.average_rating * total_matches) + match_rating
                ) / self.appearances
        
        # Update man of the match
        if match_stats.get('man_of_the_match', False):
            self.man_of_the_match += 1
    
    @classmethod
    def get_player_career_stats(cls, player_id: int) -> Dict[str, Any]:
        """Get career statistics for a player across all seasons"""
        from sqlalchemy import func
        
        # Get all statistics for the player
        stats = cls.query.filter_by(player_id=player_id).all()
        
        if not stats:
            return {}
        
        # Initialize career totals
        career_stats = {
            'appearances': 0,
            'starts': 0,
            'minutes_played': 0,
            'goals': 0,
            'assists': 0,
            'yellow_cards': 0,
            'red_cards': 0,
            'clean_sheets': 0,
            'man_of_the_match': 0,
            'seasons_played': len({s.season_id for s in stats}),
            'teams_played': len({s.team_id for s in stats}),
            'competitions_played': len({s.competition_id for s in stats if s.competition_id}),
            'by_season': [],
            'by_competition': {},
            'by_position': {}
        }
        
        # Calculate totals
        for stat in stats:
            career_stats['appearances'] += stat.appearances or 0
            career_stats['starts'] += stat.starts or 0
            career_stats['minutes_played'] += stat.minutes_played or 0
            career_stats['goals'] += stat.goals or 0
            career_stats['assists'] += stat.assists or 0
            career_stats['yellow_cards'] += stat.yellow_cards or 0
            career_stats['red_cards'] += stat.red_cards or 0
            career_stats['clean_sheets'] += stat.clean_sheets or 0
            career_stats['man_of_the_match'] += stat.man_of_the_match or 0
            
            # Group by season
            season_stat = {
                'season_id': stat.season_id,
                'season_name': stat.season.name if stat.season else None,
                'team_id': stat.team_id,
                'team_name': stat.team.name if stat.team else None,
                'appearances': stat.appearances,
                'goals': stat.goals,
                'assists': stat.assists,
                'goals_per_game': round(stat.goals / stat.appearances, 2) if stat.appearances > 0 else 0,
                'average_rating': round(stat.average_rating, 2) if stat.average_rating else 0
            }
            career_stats['by_season'].append(season_stat)
            
            # Group by competition
            if stat.competition_id:
                comp_id = stat.competition_id
                if comp_id not in career_stats['by_competition']:
                    career_stats['by_competition'][comp_id] = {
                        'competition_id': comp_id,
                        'competition_name': stat.competition.name if stat.competition else None,
                        'appearances': 0,
                        'goals': 0,
                        'assists': 0
                    }
                
                career_stats['by_competition'][comp_id]['appearances'] += stat.appearances
                career_stats['by_competition'][comp_id]['goals'] += stat.goals
                career_stats['by_competition'][comp_id]['assists'] += stat.assists
        
        # Convert competitions to list
        career_stats['by_competition'] = list(career_stats['by_competition'].values())
        
        # Sort seasons by season_id (newest first)
        career_stats['by_season'].sort(key=lambda x: x['season_id'], reverse=True)
        
        # Calculate additional metrics
        career_stats['minutes_per_goal'] = (
            round(career_stats['minutes_played'] / career_stats['goals'], 1)
            if career_stats['goals'] > 0 else 0
        )
        
        career_stats['goal_contribution'] = career_stats['goals'] + career_stats['assists']
        career_stats['goal_contribution_per_game'] = (
            round(career_stats['goal_contribution'] / career_stats['appearances'], 2)
            if career_stats['appearances'] > 0 else 0
        )
        
        return career_stats
