"""
Test script for the PredictionEngine class.
This script demonstrates how to use the PredictionEngine with sample data.
"""
import os
import sys
import logging
import numpy as np
from pprint import pprint

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_prediction_engine():
    """Test the PredictionEngine with sample data."""
    try:
        from app.services.prediction_engine import PredictionEngine
        import numpy as np
        
        # Initialize prediction engine
        logger.info("Initializing PredictionEngine...")
        engine = PredictionEngine()
        
        # Create sample training data for result prediction
        logger.info("\nCreating sample training data...")
        
        # Feature order for result prediction model
        feature_names = [
            'home_form', 'home_goals_scored_avg', 'home_goals_conceded_avg',
            'home_win_rate', 'home_draw_rate', 'home_loss_rate',
            'away_form', 'away_goals_scored_avg', 'away_goals_conceded_avg',
            'away_win_rate', 'away_draw_rate', 'away_loss_rate',
            'form_difference', 'goal_difference', 'attack_strength', 'defense_strength'
        ]
        
        # Generate random training data (100 samples)
        np.random.seed(42)
        X = np.random.rand(100, len(feature_names)) * 2  # Random features
        
        # Generate random labels (1: home win, 0: draw, -1: away win)
        y = np.random.choice([-1, 0, 1], size=100, p=[0.3, 0.2, 0.5])
        
        # Train the result prediction model
        logger.info("Training result prediction model...")
        metrics = engine.train_model(
            model_type='result',
            X=X,
            y=y,
            test_size=0.2,
            random_state=42
        )
        
        logger.info("\nModel training completed. Metrics:")
        for metric, value in metrics.items():
            logger.info(f"{metric}: {value:.4f}")
        
        # Create sample match data for prediction
        logger.info("\nCreating sample match data for prediction...")
        home_stats = {
            'form': 2.1,
            'goals_scored_avg': 1.8,
            'goals_conceded_avg': 0.9,
            'win_rate': 0.6,
            'draw_rate': 0.2,
            'loss_rate': 0.2,
            'clean_sheets': 0.4,
            'corners_avg': 6.2
        }
        
        away_stats = {
            'form': 1.7,
            'goals_scored_avg': 1.2,
            'goals_conceded_avg': 1.1,
            'win_rate': 0.4,
            'draw_rate': 0.3,
            'loss_rate': 0.3,
            'clean_sheets': 0.3,
            'corners_avg': 4.8
        }
        
        # Add derived features needed for prediction
        home_stats['form_difference'] = home_stats['form'] - away_stats['form']
        home_stats['goal_difference'] = home_stats['goals_scored_avg'] - home_stats['goals_conceded_avg']
        home_stats['attack_strength'] = home_stats['goals_scored_avg'] / (home_stats['goals_scored_avg'] + away_stats['goals_conceded_avg'])
        home_stats['defense_strength'] = home_stats['goals_conceded_avg'] / (away_stats['goals_scored_avg'] + home_stats['goals_conceded_avg'])
        
        away_stats['form_difference'] = away_stats['form'] - home_stats['form']
        away_stats['goal_difference'] = away_stats['goals_scored_avg'] - away_stats['goals_conceded_avg']
        away_stats['attack_strength'] = away_stats['goals_scored_avg'] / (home_stats['goals_conceded_avg'] + away_stats['goals_scored_avg'])
        away_stats['defense_strength'] = away_stats['goals_conceded_avg'] / (home_stats['goals_scored_avg'] + away_stats['goals_conceded_avg'])
        
        # Make predictions
        logger.info("\nMaking predictions...")
        try:
            predictions = engine.predict_all(home_stats, away_stats)
            
            # Print prediction results
            print("\n" + "="*50)
            print("PREDICTION RESULTS")
            print("="*50)
            
            # Display match result prediction
            if 'result' in predictions:
                result = predictions['result']
                print("\nMatch Result Probabilities:")
                print(f"  Home Win: {result.get('home_win', 0):.1%}")
                print(f"  Draw: {result.get('draw', 0):.1%}")
                print(f"  Away Win: {result.get('away_win', 0):.1%}")
            
            # Display over/under prediction if available
            if 'over_under' in predictions:
                ou = predictions['over_under']
                print("\nOver/Under 2.5 Goals:")
                print(f"  Over: {ou.get('over_2.5', 0):.1%}")
                print(f"  Under: {ou.get('under_2.5', 0):.1%}")
            
            # Display BTTS prediction if available
            if 'btts' in predictions:
                btts = predictions['btts']
                print("\nBoth Teams To Score:")
                print(f"  Yes: {btts.get('btts_yes', 0):.1%}")
                print(f"  No: {btts.get('btts_no', 0):.1%}")
            
            # Display score prediction if available
            if 'score' in predictions and predictions['score']:
                print("\nMost Likely Scores:")
                for score, prob in list(predictions['score'].items())[:3]:  # Show top 3
                    print(f"  {score}: {prob:.1%}")
            
            # Test feature importance if model is trained
            try:
                importance = engine.get_feature_importance('result')
                print("\nFeature Importance for Result Model:")
                pprint(importance)
            except Exception as e:
                logger.warning(f"Could not get feature importance: {e}")
            
            logger.info("\nPrediction test completed successfully!")
            return True
            
        except Exception as pred_error:
            logger.error(f"Error during prediction: {str(pred_error)}")
            return False
        
    except Exception as e:
        logger.error(f"Error in test_prediction_engine: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    test_prediction_engine()
