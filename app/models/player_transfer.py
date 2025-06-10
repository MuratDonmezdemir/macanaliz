"""Player transfer model to track player transfers between clubs"""
from datetime import date, datetime
from typing import Optional, Dict, Any
from enum import Enum
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Enum as SQLAEnum
from sqlalchemy.orm import relationship

from .base import BaseModel
from app.extensions import db


class TransferType(Enum):
    """Transfer type enumeration"""
    PERMANENT = 'permanent'  # Kalıcı transfer
    LOAN = 'loan'  # Kiralık transfer
    LOAN_END = 'loan_end'  # Kiralık süresi bitimi
    FREE = 'free'  # Bedelsiz transfer
    END_OF_CONTRACT = 'end_of_contract'  # Sözleşme bitimi
    RETIRED = 'retired'  # Futbolu bırakma
    RELEASED = 'released'  # Sözleşme feshi
    


class TransferStatus(Enum):
    """Transfer status enumeration"""
    RUMOR = 'rumor'  # Söylenti
    CONFIRMED = 'confirmed'  # Onaylandı
    COMPLETED = 'completed'  # Tamamlandı
    FAILED = 'failed'  # Başarısız oldu
    LOAN_RETURN = 'loan_return'  # Kiralık dönüşü


class PlayerTransfer(BaseModel):
    """Tracks player transfers between clubs"""
    __tablename__ = 'player_transfers'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Player and team relationships
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False, index=True)
    from_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), index=True)
    to_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False, index=True)
    
    # Transfer details
    transfer_type = db.Column(SQLAEnum(TransferType), nullable=False)
    status = db.Column(SQLAEnum(TransferStatus), default=TransferStatus.CONFIRMED, nullable=False)
    
    # Dates
    transfer_date = db.Column(db.Date, nullable=False, index=True)
    effective_date = db.Column(db.Date)  # When the transfer takes effect
    contract_start = db.Column(db.Date)
    contract_end = db.Column(db.Date)
    
    # Financial details
    fee = db.Column(db.Numeric(12, 2))  # Transfer ücreti
    fee_currency = db.Column(db.String(3), default='EUR')
    add_ons = db.Column(db.JSON)  # Bonuslar, hedefler vb.
    
    # For loan transfers
    is_loan = db.Column(db.Boolean, default=False)
    loan_end_date = db.Column(db.Date)
    has_buy_option = db.Column(db.Boolean, default=False)
    buy_option_fee = db.Column(db.Numeric(12, 2))
    
    # Transfer metadata
    transfer_window = db.Column(db.String(20))  # e.g., 'summer_2023', 'winter_2024'
    market_value = db.Column(db.Numeric(12, 2))  # Oyuncunun transfer anındaki piyasa değeri
    
    # Additional info
    notes = db.Column(db.Text)
    source = db.Column(db.String(255))  # Transferin kaynağı (haber sitesi, resmi açıklama vb.)
    
    # System fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    player = relationship('Player', foreign_keys=[player_id], back_populates='transfers')
    from_team = relationship('Team', foreign_keys=[from_team_id])
    to_team = relationship('Team', foreign_keys=[to_team_id])
    
    def __init__(self, **kwargs):
        super(PlayerTransfer, self).__init__(**kwargs)
        if not self.transfer_date:
            self.transfer_date = date.today()
        if self.transfer_type == TransferType.LOAN and not self.loan_end_date:
            # Default loan end is end of season
            today = date.today()
            if today.month >= 7:  # If after July, loan until end of next season
                self.loan_end_date = date(today.year + 1, 6, 30)
            else:
                self.loan_end_date = date(today.year, 6, 30)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transfer to dictionary"""
        return {
            'id': self.id,
            'player_id': self.player_id,
            'player_name': f"{self.player.first_name} {self.player.last_name}" if self.player else None,
            'from_team_id': self.from_team_id,
            'from_team_name': self.from_team.name if self.from_team else None,
            'to_team_id': self.to_team_id,
            'to_team_name': self.to_team.name if self.to_team else None,
            'transfer_type': self.transfer_type.value if self.transfer_type else None,
            'transfer_type_display': self.transfer_type.name.replace('_', ' ').title() if self.transfer_type else None,
            'status': self.status.value if self.status else None,
            'transfer_date': self.transfer_date.isoformat() if self.transfer_date else None,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'contract_start': self.contract_start.isoformat() if self.contract_start else None,
            'contract_end': self.contract_end.isoformat() if self.contract_end else None,
            'fee': float(self.fee) if self.fee is not None else None,
            'fee_currency': self.fee_currency,
            'fee_formatted': self.get_formatted_fee(),
            'is_loan': self.is_loan,
            'loan_end_date': self.loan_end_date.isoformat() if self.loan_end_date else None,
            'has_buy_option': self.has_buy_option,
            'buy_option_fee': float(self.buy_option_fee) if self.buy_option_fee is not None else None,
            'transfer_window': self.transfer_window,
            'market_value': float(self.market_value) if self.market_value is not None else None,
            'notes': self.notes,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_formatted_fee(self) -> str:
        """Format transfer fee in a human-readable way"""
        if self.fee is None:
            return 'Free transfer' if self.transfer_type == TransferType.FREE else 'Undisclosed'
            
        fee = float(self.fee)
        currency = self.fee_currency or '€'
        
        if fee == 0:
            return 'Free transfer'
        elif fee < 1_000_000:
            return f"{currency}{fee/1_000:.1f}K"
        elif fee < 1_000_000_000:
            return f"{currency}{fee/1_000_000:.1f}M"
        else:
            return f"{currency}{fee/1_000_000_000:.1f}B"
    
    def complete_transfer(self):
        """Mark transfer as completed and update player's team"""
        self.status = TransferStatus.COMPLETED
        
        # Update player's team
        self.player.team_id = self.to_team_id
        
        # If this is a permanent transfer, update contract dates
        if self.transfer_type == TransferType.PERMANENT:
            if self.contract_start:
                self.player.contract_start = self.contract_start
            if self.contract_end:
                self.player.contract_end = self.contract_end
        
        # If this is a loan, update loan end date
        if self.transfer_type == TransferType.LOAN and self.loan_end_date:
            self.player.loan_end_date = self.loan_end_date
        
        db.session.commit()
    
    @classmethod
    def get_team_transfers(
        cls, 
        team_id: int, 
        transfer_type: TransferType = None, 
        season: str = None,
        incoming: bool = True,
        outgoing: bool = True
    ) -> list['PlayerTransfer']:
        """Get transfers for a team, with optional filters"""
        query = cls.query
        
        # Filter by team
        team_filters = []
        if incoming:
            team_filters.append(cls.to_team_id == team_id)
        if outgoing:
            team_filters.append(cls.from_team_id == team_id)
        
        if team_filters:
            query = query.filter(db.or_(*team_filters))
        
        # Apply filters
        if transfer_type:
            query = query.filter_by(transfer_type=transfer_type)
            
        if season:
            # Assuming season is in format '2022-2023'
            try:
                start_year = int(season.split('-')[0])
                start_date = date(start_year, 7, 1)
                end_date = date(start_year + 1, 6, 30)
                query = query.filter(
                    cls.transfer_date.between(start_date, end_date)
                )
            except (ValueError, IndexError):
                pass
        
        return query.order_by(cls.transfer_date.desc()).all()
    
    @classmethod
    def get_transfer_summary(cls, team_id: int, season: str = None) -> dict:
        """Get transfer summary for a team"""
        from sqlalchemy import func, case
        
        # Base query
        query = db.session.query(
            func.count(cls.id).label('total_transfers'),
            func.sum(case([(cls.to_team_id == team_id, cls.fee)], else_=0)).label('spent'),
            func.sum(case([(cls.from_team_id == team_id, cls.fee)], else_=0)).label('earned'),
            func.sum(case([
                (cls.to_team_id == team_id, 1),
                (cls.from_team_id == team_id, -1)
            ])).label('net_players')
        )
        
        # Apply team filter
        query = query.filter(
            (cls.to_team_id == team_id) | (cls.from_team_id == team_id)
        )
        
        # Apply season filter if provided
        if season:
            try:
                start_year = int(season.split('-')[0])
                start_date = date(start_year, 7, 1)
                end_date = date(start_year + 1, 6, 30)
                query = query.filter(
                    cls.transfer_date.between(start_date, end_date)
                )
            except (ValueError, IndexError):
                pass
        
        result = query.first()
        
        return {
            'total_transfers': result[0] or 0,
            'spent': float(result[1]) if result[1] else 0,
            'earned': float(result[2]) if result[2] else 0,
            'net_spend': float((result[1] or 0) - (result[2] or 0)),
            'net_players': result[3] or 0
        }
