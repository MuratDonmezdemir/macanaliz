# Football Match Prediction System

A comprehensive football match analysis and prediction system that uses machine learning to predict match outcomes, scores, and statistics.

## Features

- **Match Prediction**: Predicts match outcomes (Home Win/Draw/Away Win) with probability scores
- **Score Prediction**: Predicts most likely scores and goal expectations
- **Team Statistics**: Detailed team performance metrics and form analysis
- **Historical Data**: Analysis of historical match data
- **API Endpoints**: RESTful API for integration with other systems
- **Admin Dashboard**: Web interface for monitoring and managing predictions

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/football-prediction-system.git
   cd football-prediction-system
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   python init_db.py
   ```

5. Create test data (optional):
   ```bash
   python init_test_data.py
   ```

## Usage

1. Start the development server:
   ```bash
   python app.py
   ```

2. Access the web interface at `http://localhost:8000`

3. Access the admin dashboard at `http://localhost:8000/dashboard`

## API Endpoints

- `GET /` - Homepage with upcoming matches and predictions
- `GET /api/predict/<int:match_id>` - Get prediction for a specific match
- `POST /api/train` - Retrain the prediction model
- `GET /api/teams/<int:team_id>/stats` - Get team statistics

## Project Structure

```
.
├── app.py                 # Main application file
├── ai_predictor.py        # AI prediction engine
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── init_db.py             # Database initialization
├── init_test_data.py      # Test data generation
├── static/                # Static files (CSS, JS, images)
│   ├── css/
│   └── js/
└── templates/             # HTML templates
    ├── base.html
    ├── index.html
    └── admin/
        └── dashboard.html
```

## Machine Learning Models

The system uses multiple machine learning models for different prediction tasks:

1. **Match Outcome Prediction**: XGBoost classifier for full-time results
2. **Half-Time Prediction**: LightGBM classifier for half-time results
3. **Goals Prediction**: CatBoost classifier for total goals
4. **BTTS (Both Teams to Score)**: Random Forest classifier
5. **Over/Under**: Gradient Boosting classifier

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Acknowledgments

- Thanks to all open-source projects that made this possible
- Data providers and football statistics APIs
- Machine learning community for their valuable resources