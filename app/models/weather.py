from .. import db
from datetime import datetime

class WeatherData(db.Model):
    __tablename__ = 'weather_data'
    
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    timestamp = db.Column(db.DateTime, nullable=False)
    temperature = db.Column(db.Float)  # Celsius
    wind_speed = db.Column(db.Float)    # m/s
    wind_direction = db.Column(db.Float) # degrees
    wind_gust = db.Column(db.Float)     # m/s
    wave_height = db.Column(db.Float)   # meters
    wave_period = db.Column(db.Float)   # seconds
    wave_direction = db.Column(db.Float) # degrees
    humidity = db.Column(db.Float)      # percentage
    pressure = db.Column(db.Float)      # hPa
    visibility = db.Column(db.Float)    # km
    weather_code = db.Column(db.String(32))
    source = db.Column(db.String(64))   # API name or 'manual'
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<WeatherData {self.location_id} @ {self.timestamp}>'
