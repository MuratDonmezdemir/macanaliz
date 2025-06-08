from .. import db
from datetime import datetime

class Race(db.Model):
    __tablename__ = 'races'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(32), default='scheduled')  # scheduled, ongoing, completed, cancelled
    race_type = db.Column(db.String(64))  # Slalom, Wave, Freestyle, Race, etc.
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    results = db.relationship('RaceResult', backref='race', lazy='dynamic')
    
    def __repr__(self):
        return f'<Race {self.name} ({self.start_date})>'

class RaceResult(db.Model):
    __tablename__ = 'race_results'
    
    id = db.Column(db.Integer, primary_key=True)
    race_id = db.Column(db.Integer, db.ForeignKey('races.id'), nullable=False)
    athlete_id = db.Column(db.Integer, db.ForeignKey('athletes.id'), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    position = db.Column(db.Integer)
    score = db.Column(db.Float)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    equipment = db.relationship('Equipment')
    
    def __repr__(self):
        return f'<RaceResult Race:{self.race_id} Athlete:{self.athlete_id} Position:{self.position}>'
