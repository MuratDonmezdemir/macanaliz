from app import db
from app.models.equipment import Equipment, EquipmentType
from app.models.athlete import Athlete
from app.services.weather_service import WeatherService
import numpy as np

class EquipmentService:
    """Service for equipment recommendations and management"""
    
    @staticmethod
    def recommend_equipment(athlete_id, location_id):
        """
        Recommend equipment for an athlete based on weather conditions and profile
        
        Args:
            athlete_id (int): ID of the athlete
            location_id (int): ID of the location
            
        Returns:
            dict: Recommended equipment and reasoning
        """
        # Get athlete data
        athlete = Athlete.query.get(athlete_id)
        if not athlete:
            return {'error': 'Athlete not found'}
        
        # Get weather data
        weather = WeatherService.get_weather_forecast(location_id)
        if not weather:
            return {'error': 'Could not get weather data'}
        
        # Get athlete's equipment
        equipment = Equipment.query.filter_by(athlete_id=athlete_id, is_active=True).all()
        if not equipment:
            return {'error': 'No equipment found for this athlete'}
        
        # Categorize equipment
        sails = [eq for eq in equipment if eq.equipment_type.name.lower() == 'sail']
        boards = [eq for eq in equipment if eq.equipment_type.name.lower() == 'board']
        
        # Make recommendations
        recommendations = {
            'sail': EquipmentService._recommend_sail(sails, weather, athlete),
            'board': EquipmentService._recommend_board(boards, weather, athlete),
            'weather_conditions': {
                'wind_speed': weather['wind_speed'],
                'wind_gust': weather['wind_gust'],
                'wind_direction': weather['wind_direction']
            },
            'athlete_profile': {
                'weight': athlete.weight,
                'experience_level': athlete.experience_level,
                'dominant_side': athlete.dominant_side
            }
        }
        
        return recommendations
    
    @staticmethod
    def _recommend_sail(sails, weather, athlete):
        """Recommend the best sail size based on conditions"""
        if not sails:
            return None
            
        wind_speed = weather['wind_speed']
        
        # Simple algorithm to recommend sail size based on wind speed and weight
        # This can be enhanced with more sophisticated logic
        base_size = 5.0  # Base size for average conditions
        
        # Adjust for wind speed (stronger wind = smaller sail)
        if wind_speed < 5:  # Light wind
            size_adjustment = 1.0
        elif wind_speed < 10:  # Medium wind
            size_adjustment = 0
        elif wind_speed < 15:  # Strong wind
            size_adjustment = -1.0
        else:  # Very strong wind
            size_adjustment = -2.0
            
        # Adjust for weight (heavier rider = larger sail)
        weight_adjustment = (athlete.weight - 75) * 0.01  # 0.1m² per 10kg from 75kg
        
        # Adjust for experience (beginners might prefer smaller sails)
        experience_adjustment = 0
        if athlete.experience_level.lower() == 'beginner':
            experience_adjustment = -0.5
            
        recommended_size = round(base_size + size_adjustment + weight_adjustment + experience_adjustment, 1)
        
        # Find closest matching sail
        best_match = min(sails, key=lambda x: abs(x.size - recommended_size))
        
        return {
            'recommended_size': recommended_size,
            'best_match': {
                'id': best_match.id,
                'brand': best_match.brand,
                'model': best_match.model,
                'size': best_match.size,
                'size_difference': round(abs(best_match.size - recommended_size), 1)
            },
            'reasoning': f"Recommended for {wind_speed} m/s wind, {athlete.weight}kg rider"
        }
    
    @staticmethod
    def _recommend_board(boards, weather, athlete):
        """Recommend the best board based on conditions"""
        if not boards:
            return None
            
        wind_speed = weather['wind_speed']
        
        # Simple algorithm to recommend board size based on wind speed and weight
        # This can be enhanced with more sophisticated logic
        base_volume = 100  # Base volume for average conditions
        
        # Adjust for wind speed (stronger wind = smaller board)
        if wind_speed < 5:  # Light wind
            volume_adjustment = 20
        elif wind_speed < 10:  # Medium wind
            volume_adjustment = 0
        elif wind_speed < 15:  # Strong wind
            volume_adjustment = -20
        else:  # Very strong wind
            volume_adjustment = -40
            
        # Adjust for weight (heavier rider = larger board)
        weight_adjustment = (athlete.weight - 75) * 0.5  # 5L per 10kg from 75kg
        
        # Adjust for experience (beginners might prefer larger boards)
        experience_adjustment = 0
        if athlete.experience_level.lower() == 'beginner':
            experience_adjustment = 10
            
        recommended_volume = round(base_volume + volume_adjustment + weight_adjustment + experience_adjustment)
        
        # Find closest matching board
        best_match = min(boards, key=lambda x: abs(x.size - recommended_volume))
        
        return {
            'recommended_volume': recommended_volume,
            'best_match': {
                'id': best_match.id,
                'brand': best_match.brand,
                'model': best_match.model,
                'volume': best_match.size,
                'volume_difference': abs(best_match.size - recommended_volume)
            },
            'reasoning': f"Recommended for {wind_speed} m/s wind, {athlete.weight}kg rider"
        }
