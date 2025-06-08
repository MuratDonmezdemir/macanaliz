from .. import db
from datetime import datetime

class EquipmentType(db.Model):
    __tablename__ = 'equipment_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)  # Yelken, Board, Sörf Tahtası
    description = db.Column(db.Text)
    
    def __repr__(self):
        return f'<EquipmentType {self.name}>'

class Equipment(db.Model):
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, db.ForeignKey('athletes.id'))
    equipment_type_id = db.Column(db.Integer, db.ForeignKey('equipment_types.id'))
    brand = db.Column(db.String(64))
    model = db.Column(db.String(64))
    size = db.Column(db.Float)  # Yelken için m², board için litre
    purchase_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    equipment_type = db.relationship('EquipmentType')
    
    def __repr__(self):
        return f'<Equipment {self.brand} {self.model} {self.size}>'
