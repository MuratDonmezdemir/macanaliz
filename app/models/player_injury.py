"""Player injury model to track player injuries"""
from datetime import date, datetime
from typing import Optional, Dict, Any
from enum import Enum, auto
from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, Enum as SQLAEnum
from sqlalchemy.orm import relationship

from .base import BaseModel
from app.extensions import db
from .enums import PlayerStatus


class InjuryStatus(Enum):
    """Injury status enumeration"""
    ACTIVE = 'active'  # Sakatlık devam ediyor
    RECOVERED = 'recovered'  # İyileşti
    RELAPSED = 'relapsed'  # Tekrar etti
    CAREER_ENDING = 'career_ending'  # Kariyeri bitiren sakatlık


class InjuryType(Enum):
    """Common injury types in football"""
    # Kas sakatlıkları
    HAMSTRING = 'hamstring'  # Arka adale
    CALF = 'calf'  # Baldır
    GROIN = 'groin'  # Kasık
    QUADRICEPS = 'quadriceps'  # Ön adale
    
    # Eklem sakatlıkları
    ANKLE_SPRAIN = 'ankle_sprain'  # Ayak bileği burkulması
    KNEE_SPRAIN = 'knee_sprain'  # Diz burkulması
    KNEE_LIGAMENT = 'knee_ligament'  # Diz bağı
    ACL = 'acl'  # Ön çapraz bağ
    PCL = 'pcl'  # Arka çapraz bağ
    MCL = 'mcl'  # İç yan bağ
    LCL = 'lcl'  # Dış yan bağ
    MENISCUS = 'meniscus'  # Menisküs
    
    # Kırıklar
    FOOT_FRACTURE = 'foot_fracture'  # Ayak kırığı
    ANKLE_FRACTURE = 'ankle_fracture'  # Ayak bileği kırığı
    LEG_FRACTURE = 'leg_fracture'  # Bacak kırığı
    ARM_FRACTURE = 'arm_fracture'  # Kol kırığı
    RIBS_FRACTURE = 'ribs_fracture'  # Kaburga kırığı
    
    # Sırt ve bel sakatlıkları
    BACK = 'back'  # Bel
    HERNIA = 'hernia'  # Fıtık
    
    # Baş yaralanmaları
    CONCUSSION = 'concussion'  # Sarsıntı
    HEAD = 'head'  # Kafa yaralanması
    
    # Diğer
    ILLNESS = 'illness'  # Hastalık
    COVID = 'covid'  # COVID-19
    OTHER = 'other'  # Diğer


class PlayerInjury(BaseModel):
    """Tracks player injuries throughout their career"""
    __tablename__ = 'player_injuries'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Relationships
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False, index=True)
    
    # Player and team relationships
    player = relationship('Player', back_populates='injuries')
    team = relationship('Team')
    
    # Injury details
    type = db.Column(SQLAEnum(InjuryType), nullable=False)
    description = db.Column(db.Text)
    
    # Injury period
    start_date = db.Column(db.Date, nullable=False, index=True)
    expected_return = db.Column(db.Date)  # Expected return date
    end_date = db.Column(db.Date)  # Actual return date
    
    # Status tracking
    status = db.Column(SQLAEnum(InjuryStatus), default=InjuryStatus.ACTIVE, nullable=False)
    
    # Medical details
    severity = db.Column(db.String(20))  # minor, moderate, major
    recurrence = db.Column(db.Integer, default=0)  # Number of times this injury has recurred
    is_national_team = db.Column(db.Boolean, default=False)  # If injury occurred during national team duty
    
    # Medical notes and treatment
    diagnosis = db.Column(db.Text)
    treatment = db.Column(db.Text)
    recovery_protocol = db.Column(db.Text)
    
    # System fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(PlayerInjury, self).__init__(**kwargs)
        if not self.severity:
            self._set_default_severity()
    
    def _set_default_severity(self):
        """Set default severity based on injury type if not provided"""
        minor_injuries = [
            InjuryType.HAMSTRING, InjuryType.CALF, InjuryType.GROIN, 
            InjuryType.QUADRICEPS, InjuryType.ANKLE_SPRAIN, InjuryType.KNEE_SPRAIN
        ]
        
        moderate_injuries = [
            InjuryType.MCL, InjuryType.LCL, InjuryType.MENISCUS,
            InjuryType.FOOT_FRACTURE, InjuryType.ANKLE_FRACTURE,
            InjuryType.HERNIA, InjuryType.CONCUSSION
        ]
        
        if self.type in minor_injuries:
            self.severity = 'minor'
        elif self.type in moderate_injuries:
            self.severity = 'moderate'
        else:
            self.severity = 'major'
    
    @property
    def duration_days(self) -> Optional[int]:
        """Calculate duration of injury in days"""
        end = self.end_date or date.today()
        if self.start_date and end >= self.start_date:
            return (end - self.start_date).days
        return None
    
    @property
    def is_active(self) -> bool:
        """Check if injury is currently active"""
        if self.status == InjuryStatus.ACTIVE:
            if self.expected_return:
                return self.expected_return >= date.today()
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert injury to dictionary"""
        return {
            'id': self.id,
            'player_id': self.player_id,
            'team_id': self.team_id,
            'type': self.type.value if self.type else None,
            'type_display': self.type.name.replace('_', ' ').title() if self.type else None,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'expected_return': self.expected_return.isoformat() if self.expected_return else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status.value if self.status else None,
            'severity': self.severity,
            'recurrence': self.recurrence,
            'is_national_team': self.is_national_team,
            'diagnosis': self.diagnosis,
            'treatment': self.treatment,
            'recovery_protocol': self.recovery_protocol,
            'duration_days': self.duration_days,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def mark_recovered(self, recovery_notes: str = None):
        """Mark injury as recovered"""
        self.status = InjuryStatus.RECOVERED
        self.end_date = date.today()
        if recovery_notes:
            self.recovery_notes = recovery_notes
        
        # Update player's injury status if this was their only active injury
        active_injuries = PlayerInjury.query.filter_by(
            player_id=self.player_id,
            status=InjuryStatus.ACTIVE
        ).count()
        
        if active_injuries <= 1:  # This injury is the only active one
            from .player import Player
            player = Player.query.get(self.player_id)
            if player:
                player.is_injured = False
                if player.status == PlayerStatus.INJURED:
                    player.status = PlayerStatus.ACTIVE
        
        db.session.commit()
    
    def update_recovery(self, new_expected_return: date = None, notes: str = None):
        """Update recovery information"""
        if new_expected_return:
            self.expected_return = new_expected_return
        if notes:
            self.recovery_notes = notes
        db.session.commit()
    
    @classmethod
    def get_active_injuries(cls, team_id: int = None) -> list['PlayerInjury']:
        """Get all active injuries, optionally filtered by team"""
        query = cls.query.filter_by(status=InjuryStatus.ACTIVE)
        if team_id:
            query = query.filter_by(team_id=team_id)
        return query.order_by(cls.expected_return).all()
    
    @classmethod
    def get_player_injuries(cls, player_id: int, limit: int = None) -> list['PlayerInjury']:
        """Get all injuries for a specific player"""
        query = cls.query.filter_by(player_id=player_id).order_by(cls.start_date.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @classmethod
    def get_team_injuries(cls, team_id: int, active_only: bool = True) -> list['PlayerInjury']:
        """Get injuries for a team, optionally filtered by active status"""
        query = cls.query.filter_by(team_id=team_id)
        if active_only:
            query = query.filter_by(status=InjuryStatus.ACTIVE)
        return query.order_by(cls.expected_return).all()
    
    @classmethod
    def get_injury_stats(cls, team_id: int = None) -> dict:
        """Get injury statistics, optionally filtered by team"""
        from sqlalchemy import func, and_
        
        query = db.session.query(
            cls.type,
            func.count(cls.id).label('count'),
            func.avg(func.julianday(func.ifnull(cls.end_date, func.date('now'))) - 
                    func.julianday(cls.start_date)).label('avg_duration')
        )
        
        if team_id:
            query = query.filter_by(team_id=team_id)
            
        results = query.group_by(cls.type).all()
        
        return {
            'by_type': [
                {
                    'type': r[0].value,
                    'type_display': r[0].name.replace('_', ' ').title(),
                    'count': r[1],
                    'avg_duration': round(r[2], 1) if r[2] else None
                }
                for r in results
            ],
            'total': sum(r[1] for r in results),
            'active': cls.query.filter_by(status=InjuryStatus.ACTIVE).count()
        }
