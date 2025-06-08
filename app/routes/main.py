from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.weather_service import WeatherService
from app.services.equipment_service import EquipmentService
from app import db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')

@bp.route('/about')
def about():
    return render_template('main/about.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard showing weather and equipment recommendations"""
    # Get the first location for demo purposes
    # In a real app, you'd let the user select a location
    from app.models.location import Location
    location = Location.query.first()
    
    weather_data = None
    equipment_recommendations = None
    
    if location:
        # Get weather data
        weather_data = WeatherService.get_weather_forecast(location.id)
        
        # Get equipment recommendations if athlete profile exists
        athlete = current_user.athlete
        if athlete:
            equipment_recommendations = EquipmentService.recommend_equipment(
                athlete.id, location.id
            )
    
    return render_template(
        'main/dashboard.html',
        weather=weather_data,
        recommendations=equipment_recommendations,
        location=location
    )
