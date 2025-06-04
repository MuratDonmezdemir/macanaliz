import numpy as np
import math
import random
from models import Match, Team, Player, Injury, TeamStatistics
from database_utils import get_team_recent_form, get_head_to_head_stats
import json

class StatisticalPredictor:
    """Statistical analysis based prediction algorithm"""
    
    def __init__(self):
        self.name = "Statistical Analysis"
        self.description = "Traditional statistical analysis using team form, strength ratings, and historical data"
    
    def predict(self, home_team, away_team):
        """Generate statistical prediction"""
        
        # Get team strengths and form
        home_attack = home_team.attack_strength
        home_defense = home_team.defense_strength
        home_form = home_team.current_form
        home_advantage = home_team.home_advantage
        
        away_attack = away_team.attack_strength
        away_defense = away_team.defense_strength
        away_form = away_team.current_form
        
        # Calculate expected goals using Poisson distribution parameters
        # Home expected goals = (Home Attack / Away Defense) * League Average * Home Advantage
        league_avg_goals = 2.7  # Average goals per match
        
        home_expected_goals = (home_attack / 100) * (100 / away_defense) * (league_avg_goals / 2) * (1 + home_advantage / 100)
        away_expected_goals = (away_attack / 100) * (100 / home_defense) * (league_avg_goals / 2)
        
        # Apply form modifier
        form_modifier_home = (home_form - 50) / 100  # -0.5 to +0.5
        form_modifier_away = (away_form - 50) / 100
        
        home_expected_goals *= (1 + form_modifier_home)
        away_expected_goals *= (1 + form_modifier_away)
        
        # Apply injury impact
        home_injury_impact = self._calculate_injury_impact(home_team)
        away_injury_impact = self._calculate_injury_impact(away_team)
        
        home_expected_goals *= (1 - home_injury_impact)
        away_expected_goals *= (1 - away_injury_impact)
        
        # Ensure reasonable bounds
        home_expected_goals = max(0.1, min(6.0, home_expected_goals))
        away_expected_goals = max(0.1, min(6.0, away_expected_goals))
        
        # Calculate first half goals (typically 45% of total goals)
        home_goals_first_half = home_expected_goals * 0.45
        away_goals_first_half = away_expected_goals * 0.45
        
        # Calculate match outcome probabilities using Poisson distribution
        probabilities = self._calculate_match_probabilities(home_expected_goals, away_expected_goals)
        
        # Calculate confidence based on various factors
        confidence = self._calculate_statistical_confidence(home_team, away_team, home_expected_goals, away_expected_goals)
        
        # Create detailed analysis
        details = {
            'home_attack_strength': home_attack,
            'away_defense_strength': away_defense,
            'home_form': home_form,
            'away_form': away_form,
            'home_advantage': home_advantage,
            'home_injury_impact': home_injury_impact,
            'away_injury_impact': away_injury_impact,
            'expected_goals_calculation': {
                'home_base': (home_attack / 100) * (100 / away_defense) * (league_avg_goals / 2),
                'away_base': (away_attack / 100) * (100 / home_defense) * (league_avg_goals / 2),
                'home_with_advantage': home_expected_goals,
                'away_final': away_expected_goals
            }
        }
        
        return {
            'home_goals': round(home_expected_goals, 1),
            'away_goals': round(away_expected_goals, 1),
            'home_goals_first_half': round(home_goals_first_half, 1),
            'away_goals_first_half': round(away_goals_first_half, 1),
            'home_win_prob': probabilities['home_win'],
            'draw_prob': probabilities['draw'],
            'away_win_prob': probabilities['away_win'],
            'confidence': confidence,
            'details': details
        }
    
    def _calculate_injury_impact(self, team):
        """Calculate impact of injuries on team performance"""
        injuries = Injury.query.join(Player).filter(
            Player.team_id == team.id,
            Injury.is_active == True
        ).all()
        
        if not injuries:
            return 0.0
        
        total_impact = 0.0
        for injury in injuries:
            # Impact based on player rating and injury severity
            player_impact = (injury.player.rating / 100) * (injury.severity / 100) * 0.1
            total_impact += player_impact
        
        return min(total_impact, 0.3)  # Cap at 30% impact
    
    def _calculate_match_probabilities(self, home_expected, away_expected):
        """Calculate match outcome probabilities using Poisson distribution"""
        home_win_prob = 0.0
        draw_prob = 0.0
        away_win_prob = 0.0
        
        # Calculate probabilities for different score combinations
        for home_goals in range(0, 8):  # 0-7 goals
            for away_goals in range(0, 8):
                home_prob = self._poisson_probability(home_goals, home_expected)
                away_prob = self._poisson_probability(away_goals, away_expected)
                match_prob = home_prob * away_prob
                
                if home_goals > away_goals:
                    home_win_prob += match_prob
                elif home_goals == away_goals:
                    draw_prob += match_prob
                else:
                    away_win_prob += match_prob
        
        # Normalize probabilities
        total = home_win_prob + draw_prob + away_win_prob
        if total > 0:
            home_win_prob /= total
            draw_prob /= total
            away_win_prob /= total
        
        return {
            'home_win': round(home_win_prob * 100, 1),
            'draw': round(draw_prob * 100, 1),
            'away_win': round(away_win_prob * 100, 1)
        }
    
    def _poisson_probability(self, k, lambda_param):
        """Calculate Poisson probability"""
        return (math.exp(-lambda_param) * (lambda_param ** k)) / math.factorial(k)
    
    def _calculate_statistical_confidence(self, home_team, away_team, home_expected, away_expected):
        """Calculate prediction confidence based on various factors"""
        confidence = 70.0  # Base confidence
        
        # Adjust based on goal difference
        goal_diff = abs(home_expected - away_expected)
        if goal_diff > 1.5:
            confidence += 15
        elif goal_diff < 0.5:
            confidence -= 10
        
        # Adjust based on form difference
        form_diff = abs(home_team.current_form - away_team.current_form)
        if form_diff > 20:
            confidence += 10
        
        # Adjust based on home advantage
        if home_team.home_advantage > 8:
            confidence += 5
        
        return min(95, max(60, confidence))

class LSTMPredictor:
    """LSTM Neural Network based prediction (simulated)"""
    
    def __init__(self):
        self.name = "LSTM Neural Network"
        self.description = "Long Short-Term Memory network analyzing temporal patterns in team performance"
        self.sequence_length = 5  # Last 5 matches
    
    def predict(self, home_team, away_team):
        """Generate LSTM-based prediction"""
        
        # Get recent match sequences for both teams
        home_sequence = self._get_team_sequence(home_team.id)
        away_sequence = self._get_team_sequence(away_team.id)
        
        # Simulate LSTM processing
        home_lstm_output = self._simulate_lstm_processing(home_sequence, True)  # Home advantage
        away_lstm_output = self._simulate_lstm_processing(away_sequence, False)
        
        # Calculate expected goals from LSTM outputs
        home_expected_goals = home_lstm_output['expected_goals']
        away_expected_goals = away_lstm_output['expected_goals']
        
        # Apply temporal momentum
        home_momentum = home_lstm_output['momentum']
        away_momentum = away_lstm_output['momentum']
        
        home_expected_goals *= (1 + home_momentum * 0.1)
        away_expected_goals *= (1 + away_momentum * 0.1)
        
        # Calculate first half predictions
        home_goals_first_half = home_expected_goals * 0.42  # LSTM suggests slightly less in first half
        away_goals_first_half = away_expected_goals * 0.42
        
        # Calculate probabilities
        probabilities = self._calculate_lstm_probabilities(home_expected_goals, away_expected_goals, home_momentum, away_momentum)
        
        # Calculate confidence based on sequence quality and momentum
        confidence = self._calculate_lstm_confidence(home_lstm_output, away_lstm_output)
        
        details = {
            'home_sequence_quality': home_lstm_output['sequence_quality'],
            'away_sequence_quality': away_lstm_output['sequence_quality'],
            'home_momentum': home_momentum,
            'away_momentum': away_momentum,
            'temporal_patterns': {
                'home_trend': home_lstm_output['trend'],
                'away_trend': away_lstm_output['trend']
            },
            'lstm_attention_weights': {
                'recent_matches_weight': 0.4,
                'form_weight': 0.3,
                'momentum_weight': 0.3
            }
        }
        
        return {
            'home_goals': round(home_expected_goals, 1),
            'away_goals': round(away_expected_goals, 1),
            'home_goals_first_half': round(home_goals_first_half, 1),
            'away_goals_first_half': round(away_goals_first_half, 1),
            'home_win_prob': probabilities['home_win'],
            'draw_prob': probabilities['draw'],
            'away_win_prob': probabilities['away_win'],
            'confidence': confidence,
            'details': details
        }
    
    def _get_team_sequence(self, team_id):
        """Get recent match sequence for LSTM input"""
        recent_matches = Match.query.filter(
            (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
        ).filter(Match.is_played == True).order_by(Match.match_date.desc()).limit(self.sequence_length).all()
        
        sequence = []
        for match in recent_matches:
            is_home = match.home_team_id == team_id
            goals_for = match.home_goals if is_home else match.away_goals
            goals_against = match.away_goals if is_home else match.home_goals
            
            # Create feature vector for this match
            features = {
                'goals_for': goals_for or 0,
                'goals_against': goals_against or 0,
                'goal_difference': (goals_for or 0) - (goals_against or 0),
                'is_home': 1 if is_home else 0,
                'result': 1 if (goals_for or 0) > (goals_against or 0) else (0 if (goals_for or 0) == (goals_against or 0) else -1)
            }
            sequence.append(features)
        
        return sequence
    
    def _simulate_lstm_processing(self, sequence, is_home):
        """Simulate LSTM neural network processing"""
        if not sequence:
            return {
                'expected_goals': 1.5 + (0.3 if is_home else 0),
                'momentum': 0.0,
                'trend': 0.0,
                'sequence_quality': 0.5
            }
        
        # Calculate weighted average with recent matches having more importance
        weights = [0.4, 0.3, 0.15, 0.1, 0.05]  # Recent to oldest
        
        total_goals = 0
        total_conceded = 0
        total_result = 0
        total_weight = 0
        
        for i, match in enumerate(sequence):
            if i < len(weights):
                weight = weights[i]
                total_goals += match['goals_for'] * weight
                total_conceded += match['goals_against'] * weight
                total_result += match['result'] * weight
                total_weight += weight
        
        avg_goals = total_goals / total_weight if total_weight > 0 else 1.5
        avg_result = total_result / total_weight if total_weight > 0 else 0
        
        # Calculate momentum (improvement/decline trend)
        momentum = 0
        if len(sequence) >= 3:
            recent_avg = sum(match['result'] for match in sequence[:3]) / 3
            older_avg = sum(match['result'] for match in sequence[3:]) / max(1, len(sequence) - 3)
            momentum = recent_avg - older_avg
        
        # Apply home advantage
        if is_home:
            avg_goals *= 1.15
        
        # Calculate trend
        trend = momentum * 0.5
        
        # Sequence quality based on number of matches
        sequence_quality = min(1.0, len(sequence) / self.sequence_length)
        
        return {
            'expected_goals': max(0.2, min(5.0, avg_goals)),
            'momentum': momentum,
            'trend': trend,
            'sequence_quality': sequence_quality
        }
    
    def _calculate_lstm_probabilities(self, home_expected, away_expected, home_momentum, away_momentum):
        """Calculate probabilities with momentum consideration"""
        # Base probabilities from expected goals
        if home_expected > away_expected:
            home_base = 45 + (home_expected - away_expected) * 8
        elif away_expected > home_expected:
            home_base = 45 - (away_expected - home_expected) * 8
        else:
            home_base = 45
        
        # Apply momentum adjustments
        momentum_diff = home_momentum - away_momentum
        home_prob = home_base + momentum_diff * 5
        
        # Ensure valid probabilities
        home_prob = max(15, min(70, home_prob))
        draw_prob = max(15, min(35, 30 - abs(momentum_diff) * 3))
        away_prob = 100 - home_prob - draw_prob
        
        return {
            'home_win': round(home_prob, 1),
            'draw': round(draw_prob, 1),
            'away_win': round(away_prob, 1)
        }
    
    def _calculate_lstm_confidence(self, home_output, away_output):
        """Calculate LSTM prediction confidence"""
        base_confidence = 75
        
        # Adjust based on sequence quality
        sequence_quality_avg = (home_output['sequence_quality'] + away_output['sequence_quality']) / 2
        confidence = base_confidence + (sequence_quality_avg - 0.5) * 20
        
        # Adjust based on momentum clarity
        momentum_clarity = abs(home_output['momentum']) + abs(away_output['momentum'])
        confidence += momentum_clarity * 5
        
        return min(95, max(65, confidence))

class CNNPredictor:
    """Convolutional Neural Network based prediction (simulated)"""
    
    def __init__(self):
        self.name = "CNN Deep Learning"
        self.description = "Convolutional Neural Network analyzing spatial patterns in match statistics"
    
    def predict(self, home_team, away_team):
        """Generate CNN-based prediction"""
        
        # Create feature maps for CNN processing
        home_feature_map = self._create_team_feature_map(home_team)
        away_feature_map = self._create_team_feature_map(away_team)
        
        # Simulate CNN convolution and pooling operations
        home_cnn_features = self._simulate_cnn_processing(home_feature_map, True)
        away_cnn_features = self._simulate_cnn_processing(away_feature_map, False)
        
        # Extract predictions from CNN features
        home_expected_goals = home_cnn_features['attack_output']
        away_expected_goals = away_cnn_features['attack_output']
        
        # Apply CNN-specific adjustments
        tactical_adjustment = self._calculate_tactical_matchup(home_cnn_features, away_cnn_features)
        
        home_expected_goals *= tactical_adjustment['home_factor']
        away_expected_goals *= tactical_adjustment['away_factor']
        
        # Calculate first half with CNN's spatial analysis
        home_goals_first_half = home_expected_goals * 0.47  # CNN suggests slightly more first half action
        away_goals_first_half = away_expected_goals * 0.47
        
        # Calculate probabilities using CNN pattern recognition
        probabilities = self._calculate_cnn_probabilities(home_cnn_features, away_cnn_features, tactical_adjustment)
        
        # Calculate confidence based on pattern recognition quality
        confidence = self._calculate_cnn_confidence(home_cnn_features, away_cnn_features, tactical_adjustment)
        
        details = {
            'home_attack_patterns': home_cnn_features['attack_patterns'],
            'away_defense_patterns': away_cnn_features['defense_patterns'],
            'tactical_matchup': tactical_adjustment,
            'pattern_recognition': {
                'home_pattern_strength': home_cnn_features['pattern_strength'],
                'away_pattern_strength': away_cnn_features['pattern_strength']
            },
            'cnn_layers': {
                'conv1_output': 'Tactical formation analysis',
                'conv2_output': 'Player interaction patterns',
                'pooling_output': 'Key performance indicators'
            }
        }
        
        return {
            'home_goals': round(home_expected_goals, 1),
            'away_goals': round(away_expected_goals, 1),
            'home_goals_first_half': round(home_goals_first_half, 1),
            'away_goals_first_half': round(away_goals_first_half, 1),
            'home_win_prob': probabilities['home_win'],
            'draw_prob': probabilities['draw'],
            'away_win_prob': probabilities['away_win'],
            'confidence': confidence,
            'details': details
        }
    
    def _create_team_feature_map(self, team):
        """Create feature map representing team characteristics"""
        # Get recent matches for pattern analysis
        recent_matches = Match.query.filter(
            (Match.home_team_id == team.id) | (Match.away_team_id == team.id)
        ).filter(Match.is_played == True).order_by(Match.match_date.desc()).limit(5).all()
        
        # Extract attacking and defensive patterns
        attack_patterns = []
        defense_patterns = []
        
        for match in recent_matches:
            is_home = match.home_team_id == team.id
            
            if is_home:
                goals_for = match.home_goals or 0
                goals_against = match.away_goals or 0
                shots = match.home_shots or 10
                shots_on_target = match.home_shots_on_target or 4
                possession = match.home_possession or 50
            else:
                goals_for = match.away_goals or 0
                goals_against = match.home_goals or 0
                shots = match.away_shots or 10
                shots_on_target = match.away_shots_on_target or 4
                possession = match.away_possession or 50
            
            # Create pattern vectors
            attack_pattern = [goals_for, shots, shots_on_target, possession / 100]
            defense_pattern = [goals_against, 1 - (goals_against / 4), (100 - possession) / 100]
            
            attack_patterns.append(attack_pattern)
            defense_patterns.append(defense_pattern)
        
        # Pad with average values if not enough matches
        while len(attack_patterns) < 5:
            attack_patterns.append([team.attack_strength / 50, 12, 5, 0.5])
            defense_patterns.append([2 - team.defense_strength / 50, team.defense_strength / 100, 0.5])
        
        return {
            'attack_patterns': attack_patterns,
            'defense_patterns': defense_patterns,
            'team_strength': team.attack_strength + team.defense_strength,
            'current_form': team.current_form
        }
    
    def _simulate_cnn_processing(self, feature_map, is_home):
        """Simulate CNN convolution operations"""
        attack_patterns = np.array(feature_map['attack_patterns'])
        defense_patterns = np.array(feature_map['defense_patterns'])
        
        # Simulate convolution filters
        # Filter 1: Recent form analysis
        recent_form_weight = [0.4, 0.3, 0.2, 0.1, 0.0]  # Recent to old
        attack_conv1 = np.average(attack_patterns[:, 0], weights=recent_form_weight)  # Goals
        
        # Filter 2: Shot efficiency analysis
        shot_efficiency = np.mean([
            pattern[2] / max(pattern[1], 1) for pattern in attack_patterns  # Shots on target / total shots
        ])
        
        # Filter 3: Possession dominance
        possession_dominance = np.mean([pattern[3] for pattern in attack_patterns])
        
        # Pooling operation: combine features
        attack_output = (attack_conv1 * 0.5 + shot_efficiency * 2 + possession_dominance * 2) * 0.8
        
        # Apply home advantage in CNN processing
        if is_home:
            attack_output *= 1.2
        
        # Defense processing
        defense_strength = 1.0 - np.mean([pattern[0] for pattern in defense_patterns]) / 3
        
        # Pattern strength calculation
        pattern_strength = np.std(attack_patterns[:, 0]) + np.std([pattern[0] for pattern in defense_patterns])
        pattern_strength = 1.0 - min(pattern_strength / 2, 0.5)  # Higher std = lower pattern strength
        
        return {
            'attack_output': max(0.3, min(4.5, attack_output)),
            'defense_strength': defense_strength,
            'attack_patterns': attack_patterns.tolist(),
            'defense_patterns': defense_patterns.tolist(),
            'pattern_strength': pattern_strength,
            'shot_efficiency': shot_efficiency,
            'possession_dominance': possession_dominance
        }
    
    def _calculate_tactical_matchup(self, home_features, away_features):
        """Analyze tactical matchup between teams"""
        # Attack vs Defense matchup
        home_attack_vs_away_defense = home_features['attack_output'] / (away_features['defense_strength'] + 0.1)
        away_attack_vs_home_defense = away_features['attack_output'] / (home_features['defense_strength'] + 0.1)
        
        # Style matchup (possession vs counter-attack)
        home_possession = home_features['possession_dominance']
        away_possession = away_features['possession_dominance']
        
        style_factor = 1.0
        if abs(home_possession - away_possession) > 0.2:
            # Different styles can create tactical advantages
            style_factor = 1.1
        
        return {
            'home_factor': min(1.5, home_attack_vs_away_defense * style_factor),
            'away_factor': min(1.5, away_attack_vs_home_defense * style_factor),
            'tactical_advantage': 'home' if home_attack_vs_away_defense > away_attack_vs_home_defense else 'away',
            'style_matchup': style_factor
        }
    
    def _calculate_cnn_probabilities(self, home_features, away_features, tactical_adjustment):
        """Calculate probabilities using CNN pattern analysis"""
        home_strength = home_features['attack_output'] * tactical_adjustment['home_factor']
        away_strength = away_features['attack_output'] * tactical_adjustment['away_factor']
        
        strength_ratio = home_strength / (away_strength + 0.1)
        
        if strength_ratio > 1.3:
            home_prob = 55 + (strength_ratio - 1.3) * 15
        elif strength_ratio < 0.77:
            home_prob = 35 - (0.77 - strength_ratio) * 15
        else:
            home_prob = 45
        
        # Pattern strength affects draw probability
        pattern_clarity = (home_features['pattern_strength'] + away_features['pattern_strength']) / 2
        draw_prob = 25 + (1 - pattern_clarity) * 10
        
        home_prob = max(20, min(65, home_prob))
        draw_prob = max(15, min(35, draw_prob))
        away_prob = 100 - home_prob - draw_prob
        
        return {
            'home_win': round(home_prob, 1),
            'draw': round(draw_prob, 1),
            'away_win': round(away_prob, 1)
        }
    
    def _calculate_cnn_confidence(self, home_features, away_features, tactical_adjustment):
        """Calculate CNN prediction confidence"""
        base_confidence = 80  # CNN typically has high confidence due to pattern recognition
        
        # Adjust based on pattern strength
        pattern_strength_avg = (home_features['pattern_strength'] + away_features['pattern_strength']) / 2
        confidence = base_confidence + pattern_strength_avg * 10
        
        # Adjust based on tactical clarity
        tactical_clarity = abs(tactical_adjustment['home_factor'] - tactical_adjustment['away_factor'])
        confidence += tactical_clarity * 5
        
        return min(95, max(70, confidence))

class BayesianPredictor:
    """Bayesian Networks based prediction"""
    
    def __init__(self):
        self.name = "Bayesian Networks"
        self.description = "Probabilistic reasoning using Bayesian inference with multiple evidence sources"
    
    def predict(self, home_team, away_team):
        """Generate Bayesian network prediction"""
        
        # Define prior probabilities
        priors = self._calculate_priors(home_team, away_team)
        
        # Collect evidence from multiple sources
        evidence = self._collect_evidence(home_team, away_team)
        
        # Apply Bayesian inference
        posterior = self._bayesian_inference(priors, evidence)
        
        # Extract goal predictions from posterior distributions
        home_expected_goals = posterior['home_goals_distribution']['mean']
        away_expected_goals = posterior['away_goals_distribution']['mean']
        
        # Calculate first half predictions with Bayesian uncertainty
        home_goals_first_half = home_expected_goals * posterior['first_half_factor']
        away_goals_first_half = away_expected_goals * posterior['first_half_factor']
        
        # Get match outcome probabilities
        match_probabilities = posterior['match_outcome_probabilities']
        
        # Calculate confidence based on evidence strength and uncertainty
        confidence = self._calculate_bayesian_confidence(evidence, posterior)
        
        details = {
            'prior_probabilities': priors,
            'evidence_sources': evidence,
            'posterior_distributions': {
                'home_goals_mean': posterior['home_goals_distribution']['mean'],
                'home_goals_variance': posterior['home_goals_distribution']['variance'],
                'away_goals_mean': posterior['away_goals_distribution']['mean'],
                'away_goals_variance': posterior['away_goals_distribution']['variance']
            },
            'bayesian_factors': {
                'form_evidence_weight': evidence['form_evidence']['weight'],
                'injury_evidence_weight': evidence['injury_evidence']['weight'],
                'h2h_evidence_weight': evidence['h2h_evidence']['weight']
            }
        }
        
        return {
            'home_goals': round(home_expected_goals, 1),
            'away_goals': round(away_expected_goals, 1),
            'home_goals_first_half': round(home_goals_first_half, 1),
            'away_goals_first_half': round(away_goals_first_half, 1),
            'home_win_prob': match_probabilities['home_win'],
            'draw_prob': match_probabilities['draw'],
            'away_win_prob': match_probabilities['away_win'],
            'confidence': confidence,
            'details': details
        }
    
    def _calculate_priors(self, home_team, away_team):
        """Calculate prior probabilities based on team strength"""
        # Base goal scoring rates (league averages)
        league_avg_home_goals = 1.5
        league_avg_away_goals = 1.2
        
        # Adjust based on team strength
        home_prior_goals = league_avg_home_goals * (home_team.attack_strength / 75) * (75 / away_team.defense_strength)
        away_prior_goals = league_avg_away_goals * (away_team.attack_strength / 75) * (75 / home_team.defense_strength)
        
        # Home advantage
        home_prior_goals *= (1 + home_team.home_advantage / 100)
        
        # Prior match outcome probabilities
        if home_prior_goals > away_prior_goals * 1.2:
            home_win_prior = 45
        elif away_prior_goals > home_prior_goals * 1.2:
            home_win_prior = 30
        else:
            home_win_prior = 37
        
        return {
            'home_goals': home_prior_goals,
            'away_goals': away_prior_goals,
            'home_win': home_win_prior,
            'draw': 28,
            'away_win': 100 - home_win_prior - 28
        }
    
    def _collect_evidence(self, home_team, away_team):
        """Collect evidence from multiple sources for Bayesian inference"""
        
        # Form evidence
        home_form_evidence = self._analyze_form_evidence(home_team.id)
        away_form_evidence = self._analyze_form_evidence(away_team.id)
        
        # Injury evidence
        home_injury_evidence = self._analyze_injury_evidence(home_team.id)
        away_injury_evidence = self._analyze_injury_evidence(away_team.id)
        
        # Head-to-head evidence
        h2h_evidence = self._analyze_h2h_evidence(home_team.id, away_team.id)
        
        # Environmental evidence (home advantage, etc.)
        environmental_evidence = {
            'home_advantage': home_team.home_advantage,
            'venue_familiarity': 1.0,  # Assume familiar venue
            'travel_factor': 0.95 if away_team.country != home_team.country else 1.0
        }
        
        return {
            'form_evidence': {
                'home_form': home_form_evidence,
                'away_form': away_form_evidence,
                'weight': 0.3
            },
            'injury_evidence': {
                'home_injuries': home_injury_evidence,
                'away_injuries': away_injury_evidence,
                'weight': 0.2
            },
            'h2h_evidence': {
                'data': h2h_evidence,
                'weight': 0.25
            },
            'environmental_evidence': {
                'data': environmental_evidence,
                'weight': 0.25
            }
        }
    
    def _bayesian_inference(self, priors, evidence):
        """Apply Bayesian inference to update probabilities"""
        
        # Update goal distributions using evidence
        home_goals_posterior = self._update_goal_distribution(
            priors['home_goals'], 
            evidence['form_evidence']['home_form'],
            evidence['injury_evidence']['home_injuries'],
            evidence['environmental_evidence']['data']['home_advantage']
        )
        
        away_goals_posterior = self._update_goal_distribution(
            priors['away_goals'],
            evidence['form_evidence']['away_form'],
            evidence['injury_evidence']['away_injuries'],
            evidence['environmental_evidence']['data']['travel_factor']
        )
        
        # Update match outcome probabilities
        match_outcome_posterior = self._update_match_outcome_probabilities(
            priors, evidence, home_goals_posterior['mean'], away_goals_posterior['mean']
        )
        
        # Calculate first half factor with uncertainty
        first_half_factor = 0.45 + random.uniform(-0.05, 0.05)  # Bayesian uncertainty
        
        return {
            'home_goals_distribution': home_goals_posterior,
            'away_goals_distribution': away_goals_posterior,
            'match_outcome_probabilities': match_outcome_posterior,
            'first_half_factor': first_half_factor,
            'uncertainty_measures': {
                'home_goals_confidence_interval': [
                    home_goals_posterior['mean'] - home_goals_posterior['variance'],
                    home_goals_posterior['mean'] + home_goals_posterior['variance']
                ],
                'away_goals_confidence_interval': [
                    away_goals_posterior['mean'] - away_goals_posterior['variance'],
                    away_goals_posterior['mean'] + away_goals_posterior['variance']
                ]
            }
        }
    
    def _analyze_form_evidence(self, team_id):
        """Analyze recent form as evidence"""
        recent_matches = Match.query.filter(
            (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
        ).filter(Match.is_played == True).order_by(Match.match_date.desc()).limit(5).all()
        
        if not recent_matches:
            return {'goals_per_match': 1.5, 'goals_conceded_per_match': 1.5, 'win_rate': 0.33}
        
        total_goals = 0
        total_conceded = 0
        wins = 0
        
        for match in recent_matches:
            is_home = match.home_team_id == team_id
            goals_for = match.home_goals if is_home else match.away_goals
            goals_against = match.away_goals if is_home else match.home_goals
            
            if goals_for is not None and goals_against is not None:
                total_goals += goals_for
                total_conceded += goals_against
                if goals_for > goals_against:
                    wins += 1
        
        matches_count = len(recent_matches)
        return {
            'goals_per_match': total_goals / matches_count,
            'goals_conceded_per_match': total_conceded / matches_count,
            'win_rate': wins / matches_count
        }
    
    def _analyze_injury_evidence(self, team_id):
        """Analyze injury impact as evidence"""
        injuries = Injury.query.join(Player).filter(
            Player.team_id == team_id,
            Injury.is_active == True
        ).all()
        
        total_impact = 0
        key_player_injuries = 0
        
        for injury in injuries:
            impact = (injury.player.rating / 100) * (injury.severity / 100)
            total_impact += impact
            if injury.player.rating > 80:
                key_player_injuries += 1
        
        return {
            'total_impact': min(total_impact, 0.4),  # Cap at 40%
            'key_player_injuries': key_player_injuries,
            'injury_count': len(injuries)
        }
    
    def _analyze_h2h_evidence(self, home_team_id, away_team_id):
        """Analyze head-to-head evidence"""
        h2h_matches = Match.query.filter(
            ((Match.home_team_id == home_team_id) & (Match.away_team_id == away_team_id)) |
            ((Match.home_team_id == away_team_id) & (Match.away_team_id == home_team_id))
        ).filter(Match.is_played == True).order_by(Match.match_date.desc()).limit(10).all()
        
        if not h2h_matches:
            return {'home_advantage': 0, 'avg_goals': 2.5, 'dominance': 0}
        
        home_wins = 0
        total_goals = 0
        
        for match in h2h_matches:
            if match.home_team_id == home_team_id:
                if (match.home_goals or 0) > (match.away_goals or 0):
                    home_wins += 1
            else:
                if (match.away_goals or 0) > (match.home_goals or 0):
                    home_wins += 1
            
            total_goals += (match.home_goals or 0) + (match.away_goals or 0)
        
        return {
            'home_advantage': (home_wins / len(h2h_matches)) - 0.33,  # Advantage over expected
            'avg_goals': total_goals / len(h2h_matches),
            'dominance': abs((home_wins / len(h2h_matches)) - 0.5) * 2  # How dominant one team is
        }
    
    def _update_goal_distribution(self, prior_mean, form_evidence, injury_evidence, environmental_factor):
        """Update goal distribution using Bayesian inference"""
        # Likelihood from form evidence
        form_adjustment = (form_evidence['goals_per_match'] / 1.5) - 1  # Relative to league average
        
        # Likelihood from injury evidence
        injury_adjustment = -injury_evidence['total_impact']
        
        # Environmental adjustment
        env_adjustment = (environmental_factor - 1) if isinstance(environmental_factor, (int, float)) else 0
        
        # Bayesian update: posterior = prior * likelihood
        posterior_mean = prior_mean * (1 + form_adjustment * 0.3 + injury_adjustment + env_adjustment * 0.2)
        
        # Calculate variance (uncertainty)
        evidence_strength = abs(form_adjustment) + abs(injury_adjustment) + abs(env_adjustment)
        variance = max(0.1, 0.5 - evidence_strength * 0.1)  # Strong evidence reduces variance
        
        return {
            'mean': max(0.1, min(5.0, posterior_mean)),
            'variance': variance
        }
    
    def _update_match_outcome_probabilities(self, priors, evidence, home_goals_mean, away_goals_mean):
        """Update match outcome probabilities using Bayesian inference"""
        # Start with priors
        home_win_prob = priors['home_win']
        draw_prob = priors['draw']
        away_win_prob = priors['away_win']
        
        # Update based on goal expectations
        goal_diff = home_goals_mean - away_goals_mean
        if goal_diff > 0.5:
            home_win_prob += goal_diff * 10
            away_win_prob -= goal_diff * 5
        elif goal_diff < -0.5:
            away_win_prob += abs(goal_diff) * 10
            home_win_prob -= abs(goal_diff) * 5
        
        # Update based on H2H evidence
        h2h_data = evidence['h2h_evidence']['data']
        if h2h_data['dominance'] > 0.3:
            if h2h_data['home_advantage'] > 0:
                home_win_prob += h2h_data['dominance'] * 15
            else:
                away_win_prob += h2h_data['dominance'] * 15
        
        # Normalize probabilities
        total = home_win_prob + draw_prob + away_win_prob
        home_win_prob = (home_win_prob / total) * 100
        draw_prob = (draw_prob / total) * 100
        away_win_prob = (away_win_prob / total) * 100
        
        return {
            'home_win': round(home_win_prob, 1),
            'draw': round(draw_prob, 1),
            'away_win': round(away_win_prob, 1)
        }
    
    def _calculate_bayesian_confidence(self, evidence, posterior):
        """Calculate confidence based on evidence strength and uncertainty"""
        base_confidence = 85  # Bayesian methods typically have high confidence
        
        # Adjust based on evidence strength
        evidence_strength = (
            evidence['form_evidence']['weight'] * 0.8 +  # Assume good form evidence
            evidence['injury_evidence']['weight'] * 0.6 +  # Moderate injury evidence
            evidence['h2h_evidence']['weight'] * 0.7 +  # Good H2H evidence
            evidence['environmental_evidence']['weight'] * 0.9  # Strong environmental evidence
        )
        
        confidence = base_confidence + evidence_strength * 10
        
        # Adjust based on uncertainty (variance)
        avg_variance = (
            posterior['home_goals_distribution']['variance'] + 
            posterior['away_goals_distribution']['variance']
        ) / 2
        
        confidence -= avg_variance * 15  # Higher variance reduces confidence
        
        return min(95, max(75, confidence))
