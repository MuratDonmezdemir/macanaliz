from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models.user import User
from app.models.athlete import Athlete
from app.models.equipment import Equipment, EquipmentType
from app.models.location import Location
from app.models.race import Race, RaceResult
from app.models.weather import WeatherData

def create_sample_data():
    app = create_app()
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True
        )
        admin.set_password('admin123')
        
        # Create regular user
        user1 = User(
            username='athlete1',
            email='athlete1@example.com'
        )
        user1.set_password('password123')
        
        db.session.add_all([admin, user1])
        db.session.commit()
        
        # Create athlete profiles
        athlete1 = Athlete(
            user_id=user1.id,
            first_name='John',
            last_name='Doe',
            date_of_birth=datetime(1990, 5, 15),
            weight=75.5,  # kg
            height=180,   # cm
            experience_level='Intermediate',
            dominant_side='right'
        )
        
        db.session.add(athlete1)
        db.session.commit()
        
        # Create equipment types
        sail_type = EquipmentType(name='Sail', description='Windsurfing sail')
        board_type = EquipmentType(name='Board', description='Windsurfing board')
        
        db.session.add_all([sail_type, board_type])
        db.session.commit()
        
        # Create equipment
        sail1 = Equipment(
            athlete_id=athlete1.id,
            equipment_type_id=sail_type.id,
            brand='North Sails',
            model='E-Type',
            size=6.2,  # m²
            purchase_date=datetime(2023, 3, 1),
            is_active=True
        )
        
        board1 = Equipment(
            athlete_id=athlete1.id,
            equipment_type_id=board_type.id,
            brand='JP Australia',
            model='Magic Ride',
            size=112,  # liters
            purchase_date=datetime(2023, 3, 1),
            is_active=True
        )
        
        db.session.add_all([sail1, board1])
        db.session.commit()
        
        # Create locations
        alacati = Location(
            name='Alaçatı',
            latitude=38.2833,
            longitude=26.3833,
            country='Turkey',
            region='İzmir',
            is_active=True,
            description='Famous windsurfing spot in Turkey'
        )
        
        db.session.add(alacati)
        db.session.commit()
        
        # Create race
        race1 = Race(
            name='Alaçatı Windsurf Challenge 2025',
            location_id=alacati.id,
            start_date=datetime(2025, 7, 15, 10, 0),
            end_date=datetime(2025, 7, 17, 18, 0),
            status='scheduled',
            race_type='Slalom',
            description='Annual windsurfing competition in Alaçatı'
        )
        
        db.session.add(race1)
        db.session.commit()
        
        # Create weather data
        weather1 = WeatherData(
            location_id=alacati.id,
            timestamp=datetime(2025, 7, 15, 10, 0),
            temperature=28.5,  # Celsius
            wind_speed=8.2,    # m/s
            wind_direction=270, # degrees (west)
            wind_gust=10.5,    # m/s
            wave_height=1.2,   # meters
            wave_period=5.5,   # seconds
            humidity=65,       # percentage
            pressure=1015,     # hPa
            visibility=10,     # km
            weather_code='clear_sky',
            source='sample_data'
        )
        
        db.session.add(weather1)
        db.session.commit()
        
        # Create race result
        result1 = RaceResult(
            race_id=race1.id,
            athlete_id=athlete1.id,
            equipment_id=sail1.id,
            position=1,
            score=100,
            notes='Great performance with consistent speed'
        )
        
        db.session.add(result1)
        db.session.commit()
        
        print('Sample data created successfully!')

if __name__ == '__main__':
    create_sample_data()
