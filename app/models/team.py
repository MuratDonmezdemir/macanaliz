"""Futbol takımlarını temsil eden model modülü."""
from datetime import datetime, date
from typing import List, Optional, Dict, Any, TYPE_CHECKING, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto

from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey, DateTime, Text, 
    Float, Date, JSON, Index, CheckConstraint, func, and_, or_
)
from sqlalchemy.orm import relationship, object_session, Session, joinedload
from sqlalchemy.ext.hybrid import hybrid_property

from .base import BaseModel
from app.extensions import db
from app.utils.enums import TeamFormation, TeamStatus, TeamType, TeamGender

if TYPE_CHECKING:
    from .match import Match
    from .player import Player
    from .coach import Coach
    from .stadium import Stadium
    from .league import League
    from .team_statistics import TeamStatistics
    from .standing import Standing
    from .transfer import Transfer
    from .match_event import MatchEvent
    from .prediction import Prediction


@dataclass
class TeamSocialMedia:
    """Takımın sosyal medya hesaplarını tutan veri sınıfı"""
    website: str = None
    facebook: str = None
    twitter: str = None
    instagram: str = None
    youtube: str = None
    tiktok: str = None
    linkedin: str = None


@dataclass
class TeamColors:
    """Takımın renklerini tutan veri sınıfı"""
    primary: str = "#000000"  # Ana renk
    secondary: str = "#FFFFFF"  # İkincil renk
    text: str = "#000000"  # Yazı rengi
    accent: str = "#FF0000"  # Vurgu rengi

class Team(BaseModel):
    """Futbol takımını temsil eden model sınıfı.
    
    Attributes:
        name: Takımın tam adı (örn: "Galatasaray Spor Kulübü")
        short_name: Kısa ad (örn: "GAL")
        code: 3 harfli kısaltma (örn: "GAL")
        country: Ülke adı (örn: "Türkiye")
        city: Şehir adı (örn: "İstanbul")
        founded: Kuruluş yılı (örn: 1905)
        logo: Logo URL'si
        stadium_id: Ana stadyum ID'si
        league_id: Bağlı olduğu lig ID'si
        status: Takım durumu (aktif, pasif, feshedildi)
        team_type: Takım türü (kulüp, milli takım, akademi)
        gender: Cinsiyet (erkek, kadın, karma)
        colors: Takım renkleri (JSON)
        social_media: Sosyal medya hesapları (JSON)
        website: Resmi web sitesi
        email: İletişim e-posta adresi
        phone: İletişim telefonu
        address: Fiziksel adres
        description: Takım hakkında açıklama
        nickname: Takımın lakabı (örn: "Aslanlar", "Cimbom")
        budget: Yıllık bütçe (euro)
        market_value: Piyasa değeri (euro)
        average_age: Takım yaş ortalaması
        foreign_players: Yabancı oyuncu sayısı
        formation: Varsayılan oyun dizilişi
        trophies: Kupa sayısı (JSON)
        last_updated: Son güncelleme tarihi
    """
    __tablename__ = 'teams'
    __table_args__ = (
        # Bileşik indeksler
        db.Index('idx_teams_league', 'league_id'),
        db.Index('idx_teams_stadium', 'stadium_id'),
        db.Index('idx_teams_country', 'country'),
        db.Index('idx_teams_city', 'city'),
        db.Index('idx_teams_name', 'name'),
        db.Index('idx_teams_short_name', 'short_name'),
        db.Index('idx_teams_code', 'code'),
        
        # Benzersiz kısıtlamalar
        db.UniqueConstraint('name', 'country', name='uq_team_name_country'),
        db.UniqueConstraint('code', name='uq_team_code'),
        
        # Kontrol kısıtlamaları
        db.CheckConstraint('founded <= extract(year from current_date)', name='ck_team_founded'),
        db.CheckConstraint('budget >= 0', name='ck_team_budget'),
        db.CheckConstraint('market_value >= 0', name='ck_team_market_value'),
        db.CheckConstraint('average_age >= 0', name='ck_team_avg_age'),
        
        # Tablo yorumu
        {'comment': 'Futbol takımlarının kaydedildiği tablo'}
    )
    
    # Temel bilgiler
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(100), 
        nullable=False, 
        index=True,
        comment='Takımın tam adı (örn: Galatasaray Spor Kulübü)'
    )
    short_name = db.Column(
        db.String(20),
        nullable=False,
        comment='Takımın kısa adı (örn: Galatasaray)'
    )
    code = db.Column(
        db.String(3),
        unique=True,
        nullable=False,
        comment='3 harfli kısaltma (örn: GAL)'
    )
    
    # Konum bilgileri
    country = db.Column(
        db.String(50),
        index=True,
        nullable=False,
        comment='Takımın ülkesi (örn: Türkiye)'
    )
    city = db.Column(
        db.String(50),
        nullable=False,
        comment='Takımın şehri (örn: İstanbul)'
    )
    
    # Temel özellikler
    founded = db.Column(
        db.Integer,
        nullable=True,
        comment='Kuruluş yılı (örn: 1905)'
    )
    logo = db.Column(
        db.String(255),
        nullable=True,
        comment='Takım logosu URL\'si (https://example.com/logo.png)'
    )
    
    # İlişkisel alanlar
    stadium_id = db.Column(
        db.Integer, 
        db.ForeignKey('stadiums.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment='Takımın ana stadyumunun ID\'si'
    )
    league_id = db.Column(
        db.Integer, 
        db.ForeignKey('leagues.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment='Takımın bağlı olduğu lig ID\'si'
    )
    
    # Durum ve tür bilgileri
    status = db.Column(
        db.Enum(TeamStatus),
        default=TeamStatus.ACTIVE,
        nullable=False,
        comment='Takımın durumu (AKTİF/PASİF/FESHEDİLDİ)'
    )
    team_type = db.Column(
        db.Enum(TeamType),
        default=TeamType.CLUB,
        nullable=False,
        comment='Takım türü (KULÜP/MİLLİ TAKIM/AKADEMİ)'
    )
    gender = db.Column(
        db.Enum(TeamGender),
        default=TeamGender.MALE,
        nullable=False,
        comment='Takım cinsiyeti (ERKEK/KADIN/KARMA)'
    )
    
    # İletişim bilgileri
    website = db.Column(
        db.String(100),
        nullable=True,
        comment='Resmi web sitesi URL\'si'
    )
    email = db.Column(
        db.String(100),
        nullable=True,
        comment='İletişim e-posta adresi'
    )
    phone = db.Column(
        db.String(20),
        nullable=True,
        comment='İletişim telefonu'
    )
    address = db.Column(
        db.Text,
        nullable=True,
        comment='Fiziksel adres'
    )
    
    # Ekstra bilgiler
    nickname = db.Column(
        db.String(50),
        nullable=True,
        comment='Takımın lakabı (örn: Aslanlar, Cimbom)'
    )
    description = db.Column(
        db.Text,
        nullable=True,
        comment='Takım hakkında detaylı açıklama'
    )
    
    # Finansal bilgiler
    budget = db.Column(
        db.Numeric(15, 2),
        default=0,
        nullable=False,
        comment='Yıllık bütçe (EUR)'
    )
    market_value = db.Column(
        db.Numeric(15, 2),
        default=0,
        nullable=False,
        comment='Piyasa değeri (EUR)'
    )
    
    # Performans metrikleri
    average_age = db.Column(
        db.Float,
        nullable=True,
        comment='Takımın yaş ortalaması'
    )
    foreign_players = db.Column(
        db.Integer,
        default=0,
        nullable=False,
        comment='Yabancı oyuncu sayısı'
    )
    formation = db.Column(
        db.Enum(TeamFormation),
        default=TeamFormation.FORMATION_442,
        nullable=False,
        comment='Varsayılan oyun dizilişi'
    )
    
    # Sosyal medya ve renkler (JSON formatında)
    social_media = db.Column(
        JSON,
        nullable=True,
        comment='Sosyal medya hesapları (JSON formatında)'
    )
    colors = db.Column(
        JSON,
        nullable=True,
        comment='Takım renkleri (JSON formatında)'
    )
    
    # Kupa bilgileri
    trophies = db.Column(
        JSON,
        nullable=True,
        comment='Kupa kazanımları (JSON formatında)'
    )
    
    # Zaman damgaları
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment='Oluşturulma tarihi'
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment='Son güncelleme tarihi'
    )
    
    # İlişkiler
    stadium = db.relationship(
        'Stadium', 
        back_populates='teams',
        lazy='joined'
    )
    league = db.relationship(
        'League', 
        back_populates='teams',
        lazy='joined'
    )
    players = db.relationship(
        'Player', 
        back_populates='team', 
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    # Maç ilişkileri
    home_matches = db.relationship(
        'Match',
        foreign_keys='Match.home_team_id',
        back_populates='home_team',
        lazy='dynamic'
    )
    away_matches = db.relationship(
        'Match',
        foreign_keys='Match.away_team_id',
        back_populates='away_team',
        lazy='dynamic'
    )
    
    # İstatistik ilişkileri
    match_statistics = db.relationship(
        'MatchStatistics', 
        back_populates='team',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='MatchStatistics.team_id'
    )
    
    # Puan durumu ilişkisi
    standings = db.relationship(
        'Standing', 
        back_populates='team',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='Standing.team_id'
    )
    
    # Sezon istatistikleri
    statistics = db.relationship(
        'TeamStatistics',
        back_populates='team',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='TeamStatistics.team_id'
    )
    
    # Yeni ilişkiler
    lineups = db.relationship('MatchLineup', back_populates='team')
    substitutions = db.relationship('MatchSubstitution', back_populates='team')
    cards = db.relationship('MatchCard', back_populates='team')
    goals = db.relationship('MatchGoal', back_populates='team')
    
    def __repr__(self):
        return f'<Team {self.name} ({self.code})>'
    
    @hybrid_property
    def full_name(self) -> str:
        """Takımın tam adını döndürür"""
        return f"{self.name} {self.nickname if self.nickname else ''}".strip()
    
    @hybrid_property
    def total_matches(self) -> int:
        """Toplam oynanan maç sayısını döndürür"""
        return self.home_matches.count() + self.away_matches.count()
    
    @hybrid_property
    def home_record(self) -> Dict[str, int]:
        """Evindeki maç istatistiklerini döndürür"""
        from .match import Match, MatchStatus
        
        matches = Match.query.filter(
            (Match.home_team_id == self.id) &
            (Match.status == MatchStatus.FINISHED)
        ).all()
        
        wins = sum(1 for m in matches if m.home_goals > m.away_goals)
        draws = sum(1 for m in matches if m.home_goals == m.away_goals)
        losses = sum(1 for m in matches if m.home_goals < m.away_goals)
        
        return {
            'played': len(matches),
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'goals_for': sum(m.home_goals for m in matches if m.home_goals is not None),
            'goals_against': sum(m.away_goals for m in matches if m.away_goals is not None)
        }
    
    @hybrid_property
    def away_record(self) -> Dict[str, int]:
        """Deplasmanda oynadığı maç istatistiklerini döndürür"""
        from .match import Match, MatchStatus
        
        matches = Match.query.filter(
            (Match.away_team_id == self.id) &
            (Match.status == MatchStatus.FINISHED)
        ).all()
        
        wins = sum(1 for m in matches if m.away_goals > m.home_goals)
        draws = sum(1 for m in matches if m.away_goals == m.home_goals)
        losses = sum(1 for m in matches if m.away_goals < m.home_goals)
        
        return {
            'played': len(matches),
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'goals_for': sum(m.away_goals for m in matches if m.away_goals is not None),
            'goals_against': sum(m.home_goals for m in matches if m.home_goals is not None)
        }
    
    @hybrid_property
    def overall_record(self) -> Dict[str, int]:
        """Genel maç istatistiklerini döndürür"""
        home = self.home_record
        away = self.away_record
        
        return {
            'played': home['played'] + away['played'],
            'wins': home['wins'] + away['wins'],
            'draws': home['draws'] + away['draws'],
            'losses': home['losses'] + away['losses'],
            'goals_for': home['goals_for'] + away['goals_for'],
            'goals_against': home['goals_against'] + away['goals_against']
        }
    
    def to_dict(self):
        """Takım bilgilerini sözlük olarak döndürür"""
        return {
            'id': self.id,
            'name': self.name,
            'short_name': self.short_name,
            'code': self.code,
            'country': self.country,
            'city': self.city,
            'founded': self.founded,
            'logo': self.logo,
            'stadium_id': self.stadium_id,
            'league_id': self.league_id,
            'status': self.status.value if self.status else None,
            'team_type': self.team_type.value if self.team_type else None,
            'gender': self.gender.value if self.gender else None,
            'website': self.website,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'nickname': self.nickname,
            'description': self.description,
            'budget': float(self.budget) if self.budget else 0,
            'market_value': float(self.market_value) if self.market_value else 0,
            'average_age': self.average_age,
            'foreign_players': self.foreign_players,
            'formation': self.formation.value if self.formation else None,
            'social_media': self.social_media or {},
            'colors': self.colors or {},
            'trophies': self.trophies or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'record': self.overall_record,
            'stadium': self.stadium.to_dict() if self.stadium else None,
            'league': self.league.to_dict() if self.league else None
        }
    
    def get_statistics(self):
        """Takım istatistiklerini getirir"""
        from .match import MatchStatistics
        return MatchStatistics.query.filter_by(team_id=self.id).first()
    
    def get_season_statistics(self, season_id: int) -> 'TeamStatistics':
        """Belirli bir sezona ait takım istatistiklerini getirir"""
        from .team_statistics import TeamStatistics
        return TeamStatistics.query.filter_by(
            team_id=self.id,
            season_id=season_id
        ).first()
    
    def get_standings(self, season_id: int) -> 'Standing':
        """Takımın lig sıralamasındaki durumunu getirir"""
        from .standing import Standing
        return Standing.query.filter_by(
            team_id=self.id,
            season_id=season_id
        ).first()
    
    def get_recent_form(self, limit: int = 5) -> List[str]:
        """Takımın son maçlardaki performansını döndürür (W: Galibiyet, D: Beraberlik, L: Mağlubiyet)"""
        matches = self.get_recent_matches(limit)
        form = []
        
        for match in matches:
            if match.status != 'FINISHED':
                continue
                
            if match.home_team_id == self.id:
                if match.home_goals > match.away_goals:
                    form.append('W')
                elif match.home_goals < match.away_goals:
                    form.append('L')
                else:
                    form.append('D')
            else:
                if match.away_goals > match.home_goals:
                    form.append('W')
                elif match.away_goals < match.home_goals:
                    form.append('L')
                else:
                    form.append('D')
        
        return form
    
    def get_recent_matches(self, limit: int = 5) -> List['Match']:
        """Takımın son maçlarını getirir"""
        from .match import Match
        return Match.query.filter(
            ((Match.home_team_id == self.id) | (Match.away_team_id == self.id)) &
            (Match.status == 'FINISHED')
        ).order_by(Match.match_date.desc()).limit(limit).all()
    
    def get_upcoming_matches(self, limit: int = 5) -> List['Match']:
        """Takımın yaklaşan maçlarını getirir"""
        from .match import Match
        return Match.query.filter(
            ((Match.home_team_id == self.id) | (Match.away_team_id == self.id)) &
            (Match.status.in_(['SCHEDULED', 'TIMED', 'POSTPONED']))
        ).order_by(Match.match_date.asc()).limit(limit).all()
    
    def get_head_to_head(self, opponent_id: int, limit: int = 10) -> List['Match']:
        """İki takım arasındaki geçmiş maçları döndürür"""
        from .match import Match
        
        return Match.query.filter(
            (
                ((Match.home_team_id == self.id) & (Match.away_team_id == opponent_id)) |
                ((Match.home_team_id == opponent_id) & (Match.away_team_id == self.id))
            ) & (Match.status == 'FINISHED')
        ).order_by(Match.match_date.desc()).limit(limit).all()
    
    def add_trophy(self, competition: str, season: str) -> None:
        """Takıma yeni kupa ekler"""
        if not self.trophies:
            self.trophies = []
            
        self.trophies.append({
            'competition': competition,
            'season': season,
            'date': datetime.utcnow().isoformat()
        })
        db.session.commit()
    
    def update_statistics(self) -> None:
        """Takım istatistiklerini günceller"""
        if not self.statistics:
            from .team_statistics import TeamStatistics
            self.statistics = TeamStatistics(team_id=self.id)
        
        # İstatistik güncellemeleri
        stats = self.statistics
        
        # Genel istatistikler
        overall = self.overall_record
        stats.matches_played = overall['played']
        stats.wins = overall['wins']
        stats.draws = overall['draws']
        stats.losses = overall['losses']
        stats.goals_for = overall['goals_for']
        stats.goals_against = overall['goals_against']
        stats.goal_difference = stats.goals_for - stats.goals_against
        
        # Ev sahibi istatistikleri
        home = self.home_record
        stats.home_matches_played = home['played']
        stats.home_wins = home['wins']
        stats.home_draws = home['draws']
        stats.home_losses = home['losses']
        stats.home_goals_for = home['goals_for']
        stats.home_goals_against = home['goals_against']
        
        # Deplasman istatistikleri
        away = self.away_record
        stats.away_matches_played = away['played']
        stats.away_wins = away['wins']
        stats.away_draws = away['draws']
        stats.away_losses = away['losses']
        stats.away_goals_for = away['goals_for']
        stats.away_goals_against = away['goals_against']
        
        # Puan hesaplama (3 puanlık sistem)
        stats.points = (stats.wins * 3) + stats.draws
        
        # Ortalama goller
        if stats.matches_played > 0:
            stats.avg_goals_for = round(stats.goals_for / stats.matches_played, 2)
            stats.avg_goals_against = round(stats.goals_against / stats.matches_played, 2)
        else:
            stats.avg_goals_for = 0
            stats.avg_goals_against = 0
        
        # Temiz sayfa ve gol yememe yüzdeleri
        clean_sheets = sum(1 for m in self.get_recent_matches(100) 
                          if (m.home_team_id == self.id and m.away_goals == 0) or 
                             (m.away_team_id == self.id and m.home_goals == 0))
        
        stats.clean_sheets = clean_sheets
        stats.clean_sheet_percentage = round((clean_sheets / stats.matches_played) * 100, 2) if stats.matches_played > 0 else 0
        
        # Son güncelleme zamanı
        stats.updated_at = datetime.utcnow()
        
        db.session.commit()
    
    def get_players_by_position(self, position: str = None) -> List['Player']:
        """Pozisyona göre oyuncuları getirir"""
        from .player import Player
        
        query = Player.query.filter_by(team_id=self.id)
        if position:
            query = query.filter_by(position=position)
            
        return query.order_by(Player.jersey_number).all()
    
    def get_top_scorers(self, limit: int = 5) -> List[Dict]:
        """En çok gol atan oyuncuları getirir"""
        from .match_goal import MatchGoal
        from .player import Player
        from sqlalchemy import func, desc
        
        top_scorers = db.session.query(
            Player,
            func.count(MatchGoal.id).label('goals')
        ).join(
            MatchGoal,
            MatchGoal.scorer_id == Player.id
        ).filter(
            Player.team_id == self.id
        ).group_by(
            Player.id
        ).order_by(
            desc('goals')
        ).limit(limit).all()
        
        return [{'player': player.to_dict(), 'goals': goals} for player, goals in top_scorers]
    
    def get_most_assists(self, limit: int = 5) -> List[Dict]:
        """En çok asist yapan oyuncuları getirir"""
        from .match_goal import MatchGoal
        from .player import Player
        from sqlalchemy import func, desc
        
        top_assisters = db.session.query(
            Player,
            func.count(MatchGoal.id).label('assists')
        ).join(
            MatchGoal,
            MatchGoal.assist_id == Player.id
        ).filter(
            Player.team_id == self.id,
            MatchGoal.assist_id.isnot(None)
        ).group_by(
            Player.id
        ).order_by(
            desc('assists')
        ).limit(limit).all()
        
        return [{'player': player.to_dict(), 'assists': assists} for player, assists in top_assisters]
    
    def get_players_with_most_yellow_cards(self, limit: int = 5) -> List[Dict]:
        """En çok sarı kart gören oyuncuları getirir"""
        from .match_card import MatchCard
        from .player import Player
        from sqlalchemy import func, desc
        
        players = db.session.query(
            Player,
            func.count(MatchCard.id).label('yellow_cards')
        ).join(
            MatchCard,
            MatchCard.player_id == Player.id
        ).filter(
            Player.team_id == self.id,
            MatchCard.card_type == 'yellow'
        ).group_by(
            Player.id
        ).order_by(
            desc('yellow_cards')
        ).limit(limit).all()
        
        return [{'player': player.to_dict(), 'yellow_cards': cards} for player, cards in players]
    
    def get_players_with_red_cards(self, limit: int = 10) -> List[Dict]:
        """Kırmızı kart gören oyuncuları getirir"""
        from .match_card import MatchCard
        from .player import Player
        from sqlalchemy import func, desc
        
        players = db.session.query(
            Player,
            func.count(MatchCard.id).label('red_cards')
        ).join(
            MatchCard,
            MatchCard.player_id == Player.id
        ).filter(
            Player.team_id == self.id,
            MatchCard.card_type == 'red'
        ).group_by(
            Player.id
        ).order_by(
            desc('red_cards')
        ).limit(limit).all()
        
        return [{'player': player.to_dict(), 'red_cards': cards} for player, cards in players]
