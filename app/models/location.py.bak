from .. import db

class Location(db.Model):
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    country = db.Column(db.String(64))
    region = db.Column(db.String(64))
    is_active = db.Column(db.Boolean, default=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), 
                         onupdate=db.func.current_timestamp())
    
    # İlişkiler
    races = db.relationship('Race', backref='location', lazy='dynamic')
    weather_data = db.relationship('WeatherData', backref='location', lazy='dynamic')
    
    def __repr__(self):
        return f'<Location {self.name}, {self.region}, {self.country}>'
