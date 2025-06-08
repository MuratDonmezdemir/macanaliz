import requests
from datetime import datetime, timedelta
from app import db
from app.models.weather import WeatherData
from app.models.location import Location
from config import Config

class WeatherService:
    """Service for handling weather data operations"""
    
    @staticmethod
    def get_weather_forecast(location_id, days=7):
        """
        Get weather forecast for a location
        
        Args:
            location_id (int): ID of the location
            days (int): Number of days to forecast (default: 7)
            
        Returns:
            dict: Weather forecast data or None if error
        """
        location = Location.query.get(location_id)
        if not location:
            return None
            
        # Check if we have recent data in the database (less than 1 hour old)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_weather = WeatherData.query.filter(
            WeatherData.location_id == location_id,
            WeatherData.timestamp >= one_hour_ago
        ).order_by(WeatherData.timestamp.desc()).first()
        
        if recent_weather:
            return {
                'temperature': recent_weather.temperature,
                'wind_speed': recent_weather.wind_speed,
                'wind_direction': recent_weather.wind_direction,
                'wind_gust': recent_weather.wind_gust,
                'wave_height': recent_weather.wave_height,
                'source': 'database',
                'timestamp': recent_weather.timestamp.isoformat()
            }
            
        # If no recent data, fetch from Open-Meteo API
        return WeatherService._fetch_from_openmeteo(location.latitude, location.longitude, days)
    
    @staticmethod
    def _fetch_from_openmeteo(latitude, longitude, days=7):
        """Fetch weather data from Open-Meteo API"""
        try:
            # Make API request to Open-Meteo
            url = f"{Config.OPEN_METEO_URL}/forecast"
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min', 
                         'windspeed_10m_max', 'winddirection_10m_dominant', 'windgusts_10m_max'],
                'timezone': 'auto',
                'forecast_days': days
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process and save the data
            return WeatherService._process_weather_data(data, latitude, longitude)
            
        except Exception as e:
            print(f"Error fetching weather data: {str(e)}")
            return None
    
    @staticmethod
    def _process_weather_data(data, latitude, longitude):
        """Process weather data from Open-Meteo and save to database"""
        if 'daily' not in data:
            return None
            
        daily = data['daily']
        time_list = daily.get('time', [])
        
        if not time_list:
            return None
            
        # Get or create location
        location = Location.query.filter_by(
            latitude=round(latitude, 4),
            longitude=round(longitude, 4)
        ).first()
        
        if not location:
            location = Location(
                name=f"Custom Location ({latitude}, {longitude})",
                latitude=latitude,
                longitude=longitude,
                country="Unknown",
                is_active=True
            )
            db.session.add(location)
            db.session.commit()
        
        # Save weather data for each day
        for i in range(len(time_list)):
            try:
                timestamp = datetime.strptime(time_list[i], '%Y-%m-%d')
                
                weather = WeatherData(
                    location_id=location.id,
                    timestamp=timestamp,
                    temperature=(daily['temperature_2m_max'][i] + daily['temperature_2m_min'][i]) / 2,
                    wind_speed=daily['windspeed_10m_max'][i],
                    wind_direction=daily['winddirection_10m_dominant'][i],
                    wind_gust=daily['windgusts_10m_max'][i],
                    weather_code=str(daily['weathercode'][i]),
                    source='openmeteo',
                    wave_height=None  # Not provided by Open-Meteo
                )
                db.session.add(weather)
            except (IndexError, KeyError, ValueError) as e:
                print(f"Error processing weather data: {str(e)}")
                continue
        
        db.session.commit()
        
        # Return the most recent forecast
        return {
            'temperature': weather.temperature,
            'wind_speed': weather.wind_speed,
            'wind_direction': weather.wind_direction,
            'wind_gust': weather.wind_gust,
            'wave_height': weather.wave_height,
            'source': 'openmeteo',
            'timestamp': timestamp.isoformat()
        }
