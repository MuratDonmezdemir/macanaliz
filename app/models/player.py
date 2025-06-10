from datetime import datetime, date
from enum import Enum
from typing import Dict, List, Optional, Any, Union, TYPE_CHECKING
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, Text, Numeric, Enum as SQLAEnum
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property

from . import MatchLineup
from .base import BaseModel
from .enums import PlayerPosition, PlayerStatus, PlayerFoot
from app.extensions import db

if TYPE_CHECKING:
    from .player_injury import PlayerInjury
    from .player_transfer import PlayerTransfer
    from .player_statistics import PlayerStatistics

class Player(BaseModel):
    """Futbol oyuncularını temsil eden model.
    
    Attributes:
        id: Benzersiz tanımlayıcı
        first_name: Oyuncunun adı
        last_name: Oyuncunun soyadı
        full_name: Tam ad (first_name + last_name)
        short_name: Kısa ad
        date_of_birth: Doğum tarihi
        country: Ülke kodu (TR, GB, ES, ...)
        nationality: Milliyet
        height: Boy (cm)
        weight: Ağırlık (kg)
        foot: Kullandığı ayak (right/left/both)
        position: Ana mevkii
        positions: Oynayabildiği tüm mevkiler
        jersey_number: Forma numarası
        team_id: Bağlı olduğu takım ID'si
        team: Bağlı olduğu takım
        contract_start: Sözleşme başlangıç tarihi
        contract_end: Sözleşme bitiş tarihi
        market_value: Piyasa değeri (EUR)
        image_url: Oyuncu resim URL'si
        social_media: Sosyal medya hesapları
        status: Oyuncunun mevcut durumu
        is_active: Aktif mi?
        created_at: Oluşturulma tarihi
        updated_at: Son güncellenme tarihi
    """
    __tablename__ = 'players'
    
    # Temel Bilgiler
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False, index=True)
    last_name = db.Column(db.String(50), nullable=False, index=True)
    full_name = db.Column(db.String(120), index=True)  # Arama performansı için ayrı tutuldu
    short_name = db.Column(db.String(30))
    
    # Kişisel Bilgiler
    date_of_birth = db.Column(db.Date, nullable=False, index=True)
    place_of_birth = db.Column(db.String(100))
    country = db.Column(db.String(2), nullable=False)  # ISO 3166-1 alpha-2
    nationality = db.Column(db.String(50))
    second_nationality = db.Column(db.String(50))
    height = db.Column(db.Integer)  # cm cinsinden
    weight = db.Column(db.Integer)  # kg cinsinden
    foot = db.Column(SQLAEnum(PlayerFoot))
    
    # Kariyer Bilgileri
    position = db.Column(SQLAEnum(PlayerPosition), nullable=False)
    positions = db.Column(ARRAY(SQLAEnum(PlayerPosition)))  # Oynayabildiği tüm mevkiler
    jersey_number = db.Column(db.Integer)
    preferred_position = db.Column(SQLAEnum(PlayerPosition))  # Tercih ettiği mevki
    
    # Sözleşme Bilgileri
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), index=True)
    contract_start = db.Column(db.Date)
    contract_end = db.Column(db.Date)
    market_value = db.Column(db.Numeric(12, 2))  # EUR cinsinden
    market_value_currency = db.Column(db.String(3), default='EUR')
    market_value_last_update = db.Column(db.DateTime)
    
    # Medya ve Tanıtım
    image_url = db.Column(db.String(255))
    thumbnail_url = db.Column(db.String(255))
    social_media = db.Column(JSON)  # {twitter: '', instagram: '', facebook: ''}
    
    # Durum
    status = db.Column(SQLAEnum(PlayerStatus), default=PlayerStatus.ACTIVE, nullable=False)
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_injured = db.Column(db.Boolean, default=False)
    injury_details = db.Column(JSON)  # {type: str, return_date: date, description: str}
    
    # Sistem Bilgileri
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    team = relationship('Team', back_populates='players')
    
    # Career relationships
    statistics: Mapped[List['PlayerStatistics']] = relationship(
        'PlayerStatistics', 
        back_populates='player', 
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    transfers: Mapped[List['PlayerTransfer']] = relationship(
        'PlayerTransfer', 
        foreign_keys='PlayerTransfer.player_id',
        back_populates='player',
        order_by='desc(PlayerTransfer.transfer_date)',
        lazy='dynamic'
    )
    
    injuries: Mapped[List['PlayerInjury']] = relationship(
        'PlayerInjury',
        back_populates='player',
        order_by='desc(PlayerInjury.start_date)',
        lazy='dynamic'
    )
    
    # Match relationships
    lineups = relationship('MatchLineup', back_populates='player')
    
    substitutions_in = relationship(
        'MatchSubstitution',
        foreign_keys='MatchSubstitution.player_in_id',
        back_populates='player_in',
        lazy='dynamic'
    )
    
    substitutions_out = relationship(
        'MatchSubstitution',
        foreign_keys='MatchSubstitution.player_out_id',
        back_populates='player_out',
        lazy='dynamic'
    )
    
    cards = relationship('MatchCard', back_populates='player', lazy='dynamic')
    
    goals_scored = relationship(
        'MatchGoal',
        foreign_keys='MatchGoal.scorer_id',
        back_populates='scorer',
        lazy='dynamic'
    )
    
    goal_assists = relationship(
        'MatchGoal',
        foreign_keys='MatchGoal.assist_id',
        back_populates='assist',
        lazy='dynamic'
    )
    
    def __init__(self, **kwargs):
        super(Player, self).__init__(**kwargs)
        if not self.full_name and (self.first_name or self.last_name):
            self.full_name = f"{self.first_name or ''} {self.last_name or ''}".strip()
    
    def __repr__(self):
        return f'<Player {self.full_name} ({self.position.value if self.position else "N/A"})>'
    
    @hybrid_property
    def age(self) -> int:
        """Oyuncunun yaşını hesaplar"""
        if not self.date_of_birth:
            return 0
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @hybrid_property
    def contract_status(self) -> Dict[str, Any]:
        """Sözleşme durumunu döndürür"""
        if not self.contract_end:
            return {'status': 'unknown', 'days_remaining': None}
            
        today = date.today()
        days_left = (self.contract_end - today).days
        
        if days_left < 0:
            return {'status': 'expired', 'days_remaining': 0}
        elif days_left <= 180:  # 6 aydan az
            return {'status': 'expiring_soon', 'days_remaining': days_left}
        else:
            return {'status': 'active', 'days_remaining': days_left}
    
    def to_dict(self, detailed: bool = False) -> Dict[str, Any]:
        """Oyuncu bilgilerini sözlük olarak döndürür
        
        Args:
            detailed: Detaylı bilgileri de ekler
        """
        data = {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'short_name': self.short_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'age': self.age,
            'country': self.country,
            'nationality': self.nationality,
            'second_nationality': self.second_nationality,
            'height': self.height,
            'weight': self.weight,
            'foot': self.foot.value if self.foot else None,
            'position': self.position.value if self.position else None,
            'positions': [pos.value for pos in self.positions] if self.positions else [],
            'preferred_position': self.preferred_position.value if self.preferred_position else None,
            'jersey_number': self.jersey_number,
            'team_id': self.team_id,
            'team_name': self.team.name if self.team else None,
            'contract_start': self.contract_start.isoformat() if self.contract_start else None,
            'contract_end': self.contract_end.isoformat() if self.contract_end else None,
            'contract_status': self.contract_status,
            'market_value': float(self.market_value) if self.market_value is not None else None,
            'market_value_currency': self.market_value_currency,
            'image_url': self.image_url,
            'thumbnail_url': self.thumbnail_url,
            'status': self.status.value if self.status else None,
            'is_active': self.is_active,
            'is_injured': self.is_injured,
            'injury_details': self.injury_details,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if detailed:
            data.update({
                'social_media': self.social_media or {},
                'statistics': [stat.to_dict() for stat in self.statistics],
                'transfers': [transfer.to_dict() for transfer in self.transfers],
                'injuries': [injury.to_dict() for injury in self.injuries]
            })
            
        return data
    
    def get_season_statistics(self, season_id: int, competition_id: int = None) -> Optional['PlayerStatistics']:
        """Belirli bir sezona ve isteğe bağlı olarak bir müsabakaya ait istatistikleri getirir"""
        query = self.statistics.filter_by(season_id=season_id)
        if competition_id:
            query = query.filter_by(competition_id=competition_id)
        return query.first()
    
    def get_career_statistics(self) -> Dict[str, Any]:
        """Kariyer istatistiklerini toplu olarak döndürür
        
        Returns:
            Dict containing aggregated career statistics
        """
        from .player_statistics import PlayerStatistics
        return PlayerStatistics.get_player_career_stats(self.id)
    
    def update_injury(self, injury_type: str, return_date: date, description: str = None):
        """Oyuncunun sakatlık durumunu günceller"""
        self.is_injured = True
        self.status = PlayerStatus.INJURED
        self.injury_details = {
            'type': injury_type,
            'start_date': datetime.utcnow().isoformat(),
            'return_date': return_date.isoformat(),
            'description': description
        }
        
        # Sakatlık kaydı oluştur
        injury = PlayerInjury(
            player_id=self.id,
            team_id=self.team_id,
            type=injury_type,
            start_date=date.today(),
            expected_return=return_date,
            description=description
        )
        db.session.add(injury)
        db.session.commit()
    
    def clear_injury(self):
        """Oyuncunun sakatlık durumunu temizler"""
        self.is_injured = False
        if self.status == PlayerStatus.INJURED:
            self.status = PlayerStatus.ACTIVE
        self.injury_details = None
        
        # Aktif sakatlık kaydını kapat
        active_injury = PlayerInjury.query.filter_by(
            player_id=self.id,
            end_date=None
        ).first()
        
        if active_injury:
            active_injury.end_date = date.today()
            active_injury.status = 'recovered'
        
        db.session.commit()
    
    @classmethod
    def search(cls, query: str, limit: int = 10) -> List['Player']:
        """İsim veya soyisme göre oyuncu arar"""
        search = f"%{query}%"
        return cls.query.filter(
            (cls.full_name.ilike(search)) |
            (cls.first_name.ilike(search)) |
            (cls.last_name.ilike(search))
        ).limit(limit).all()
    
    @classmethod
    def get_by_country(cls, country_code: str) -> List['Player']:
        """Ülke koduna göre oyuncuları getirir"""
        return cls.query.filter_by(country=country_code.upper()).all()
    
    @classmethod
    def get_by_position(cls, position: PlayerPosition) -> List['Player']:
        """Pozisyona göre oyuncuları getirir"""
        return cls.query.filter(
            (cls.position == position) | 
            (cls.positions.contains([position]))
        ).all()
    
    def get_transfer_history(self) -> List[Dict]:
        """Oyuncunun transfer geçmişini döndürür"""
        return sorted(
            [t.to_dict() for t in self.transfers],
            key=lambda x: x.get('date', ''),
            reverse=True
        )
    
    def get_injury_history(self) -> List[Dict]:
        """Oyuncunun sakatlık geçmişini döndürür"""
        return [i.to_dict() for i in sorted(
            self.injuries,
            key=lambda x: x.start_date,
            reverse=True
        )]
    
    def get_last_matches(self, limit: int = 5) -> List[Dict]:
        """Oyuncunun son maçlarını getirir"""
        from .match import Match, MatchStatus
        
        # Oyuncunun oynadığı maçları bul
        matches = Match.query.join(
            Match.lineups
        ).filter(
            (Match.status == MatchStatus.FINISHED) &
            (MatchLineup.player_id == self.id)
        ).order_by(
            Match.match_date.desc()
        ).limit(limit).all()
        
        result = []
        for match in matches:
            lineup = next((l for l in match.lineups if l.player_id == self.id), None)
            if lineup:
                result.append({
                    'match_id': match.id,
                    'date': match.match_date.isoformat(),
                    'home_team': match.home_team.name,
                    'away_team': match.away_team.name,
                    'score': f"{match.home_goals} - {match.away_goals}",
                    'minutes_played': lineup.minutes_played,
                    'rating': lineup.rating,
                    'goals': lineup.goals,
                    'assists': lineup.assists,
                    'yellow_cards': lineup.yellow_cards,
                    'red_cards': lineup.red_cards
                })
                
        return result

class PlayerStatistics(BaseModel):
    """Oyuncu istatistikleri modeli"""
    __tablename__ = 'player_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))
    season_id = db.Column(db.Integer, db.ForeignKey('seasons.id'))
    
    # İlişkiler
    # Player, Team, Match ve Season ilişkileri backref ile tanımlanıyor
    
    # Temel istatistikler
    position = db.Column(db.String(5))  # GK, DEF, MID, FWD
    minutes_played = db.Column(db.Integer, default=0)
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    yellow_cards = db.Column(db.Integer, default=0)
    red_cards = db.Column(db.Integer, default=0)
    
    # Hücum istatistikleri
    shots = db.Column(db.Integer, default=0)
    shots_on_target = db.Column(db.Integer, default=0)
    key_passes = db.Column(db.Integer, default=0)
    dribbles = db.Column(db.Integer, default=0)
    dribbles_successful = db.Column(db.Integer, default=0)
    
    # Pas istatistikleri
    passes = db.Column(db.Integer, default=0)
    pass_accuracy = db.Column(db.Float)
    
    # Defans istatistikleri
    tackles = db.Column(db.Integer, default=0)
    interceptions = db.Column(db.Integer, default=0)
    clearances = db.Column(db.Integer, default=0)
    
    # Diğer
    rating = db.Column(db.Float)
    is_motm = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    pass_accuracy = db.Column(db.Float, default=0.0)  # Yüzde olarak
    long_balls = db.Column(db.Integer, default=0)
    crosses = db.Column(db.Integer, default=0)
    
    # Defans istatistikleri
    tackles = db.Column(db.Integer, default=0)
    interceptions = db.Column(db.Integer, default=0)
    clearances = db.Column(db.Integer, default=0)
    blocks = db.Column(db.Integer, default=0)
    
    # Kaleci istatistikleri
    saves = db.Column(db.Integer, default=0)
    goals_conceded = db.Column(db.Integer, default=0)
    clean_sheets = db.Column(db.Boolean, default=False)
    penalty_saves = db.Column(db.Integer, default=0)
    
    # Diğer
    fouls_committed = db.Column(db.Integer, default=0)
    fouls_suffered = db.Column(db.Integer, default=0)
    offsides = db.Column(db.Integer, default=0)
    
    # Puanlama ve değerlendirme
    rating = db.Column(db.Float, default=0.0)  # 1-10 arası performans puanı
    is_motm = db.Column(db.Boolean, default=False)  # Maçın adamı mı?
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    team = db.relationship('Team', backref=db.backref('player_statistics', lazy='dynamic'))
    match = db.relationship('Match', backref=db.backref('player_stats', lazy='dynamic'))
    season = db.relationship('Season')
    
    def __repr__(self):
        return f'<PlayerStatistics {self.player_name} - {self.match_id}>'
    
    def to_dict(self):
        """İstatistikleri sözlük olarak döndürür"""
        return {
            'player_name': self.player_name,
            'team_id': self.team_id,
            'match_id': self.match_id,
            'position': self.position,
            'goals': self.goals,
            'assists': self.assists,
            'rating': self.rating,
            'is_motm': self.is_motm
        }
