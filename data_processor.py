import numpy as np
from datetime import datetime, timedelta
from app.models import Team, Match, Player, InjuryReport
from app import db
from sqlalchemy import func, desc
import math


class DataProcessor:
    """Data processing and feature engineering for AI models"""

    def __init__(self):
        self.default_stats = {
            "attack_rating": 50.0,
            "defense_rating": 50.0,
            "home_advantage": 1.1,
            "recent_form": 50.0,
            "recent_matches": 0,
        }

    def prepare_team_data(self, home_team, away_team):
        """Prepare comprehensive team data for AI models"""
        home_data = self._get_team_features(home_team, is_home=True)
        away_data = self._get_team_features(away_team, is_home=False)

        # Add head-to-head statistics
        h2h_stats = self._get_head_to_head_stats(home_team, away_team)

        return {
            "home_team": home_data,
            "away_team": away_data,
            "head_to_head": h2h_stats,
            "match_context": self._get_match_context(),
        }

    def _get_team_features(self, team, is_home=True):
        """Extract comprehensive features for a team"""
        features = {
            "team_id": team.id,
            "team_name": team.name,
            "league": team.league,
            "attack_rating": team.attack_rating,
            "defense_rating": team.defense_rating,
            "home_advantage": team.home_advantage if is_home else 1.0,
            "current_form": team.current_form,
        }

        # Recent match statistics
        recent_matches = self._get_recent_match_stats(team, limit=5)
        features.update(recent_matches)

        # Player-based statistics
        player_stats = self._get_player_stats(team)
        features.update(player_stats)

        # Injury analysis
        injury_stats = self._get_injury_stats(team)
        features.update(injury_stats)

        # Performance trends
        trends = self._calculate_performance_trends(team)
        features.update(trends)

        return features

    def _get_recent_match_stats(self, team, limit=5):
        """Get statistics from recent matches"""
        recent_matches = (
            Match.query.filter(
                (Match.home_team_id == team.id) | (Match.away_team_id == team.id)
            )
            .filter(Match.played == True)
            .order_by(Match.match_date.desc())
            .limit(limit)
            .all()
        )

        if not recent_matches:
            return {
                "recent_matches": 0,
                "recent_form": 50.0,
                "avg_goals_scored": 1.5,
                "avg_goals_conceded": 1.5,
                "recent_wins": 0,
                "recent_draws": 0,
                "recent_losses": 0,
                "goal_difference": 0,
                "avg_shots": 12.0,
                "avg_shots_on_target": 5.0,
                "avg_possession": 50.0,
                "avg_corners": 5.0,
                "clean_sheets": 0,
                "scoring_frequency": 0.6,
            }

        stats = {
            "recent_matches": len(recent_matches),
            "avg_goals_scored": 0,
            "avg_goals_conceded": 0,
            "recent_wins": 0,
            "recent_draws": 0,
            "recent_losses": 0,
            "total_shots": 0,
            "total_shots_on_target": 0,
            "total_possession": 0,
            "total_corners": 0,
            "clean_sheets": 0,
        }

        for match in recent_matches:
            if match.home_team_id == team.id:
                # Home match
                goals_scored = match.home_score or 0
                goals_conceded = match.away_score or 0
                shots = match.home_shots or 12
                shots_on_target = match.home_shots_on_target or 5
                possession = match.home_possession or 50
                corners = match.home_corners or 5
            else:
                # Away match
                goals_scored = match.away_score or 0
                goals_conceded = match.home_score or 0
                shots = match.away_shots or 12
                shots_on_target = match.away_shots_on_target or 5
                possession = match.away_possession or 50
                corners = match.away_corners or 5

            stats["avg_goals_scored"] += goals_scored
            stats["avg_goals_conceded"] += goals_conceded
            stats["total_shots"] += shots
            stats["total_shots_on_target"] += shots_on_target
            stats["total_possession"] += possession
            stats["total_corners"] += corners

            if goals_conceded == 0:
                stats["clean_sheets"] += 1

            # Match result
            if goals_scored > goals_conceded:
                stats["recent_wins"] += 1
            elif goals_scored == goals_conceded:
                stats["recent_draws"] += 1
            else:
                stats["recent_losses"] += 1

        # Calculate averages
        num_matches = len(recent_matches)
        stats["avg_goals_scored"] /= num_matches
        stats["avg_goals_conceded"] /= num_matches
        stats["avg_shots"] = stats["total_shots"] / num_matches
        stats["avg_shots_on_target"] = stats["total_shots_on_target"] / num_matches
        stats["avg_possession"] = stats["total_possession"] / num_matches
        stats["avg_corners"] = stats["total_corners"] / num_matches

        # Calculate form (points from recent matches)
        points = stats["recent_wins"] * 3 + stats["recent_draws"]
        max_points = num_matches * 3
        stats["recent_form"] = (points / max_points) * 100 if max_points > 0 else 50

        # Goal difference
        stats["goal_difference"] = (
            stats["avg_goals_scored"] - stats["avg_goals_conceded"]
        )

        # Scoring frequency (goals per match)
        stats["scoring_frequency"] = stats["avg_goals_scored"]

        return stats

    def _get_player_stats(self, team):
        """Get player-based team statistics"""
        players = Player.query.filter_by(team_id=team.id).all()

        if not players:
            return {
                "squad_size": 0,
                "avg_skill_rating": 50.0,
                "top_scorer_goals": 0,
                "total_goals": 0,
                "total_assists": 0,
                "experienced_players": 0,
                "young_prospects": 0,
            }

        total_skill = sum(player.skill_rating for player in players)
        total_goals = sum(player.goals_scored for player in players)
        total_assists = sum(player.assists for player in players)

        # Player age analysis
        experienced_players = sum(
            1 for player in players if player.age and player.age >= 28
        )
        young_prospects = sum(
            1 for player in players if player.age and player.age <= 21
        )

        # Top scorer
        top_scorer_goals = (
            max(player.goals_scored for player in players) if players else 0
        )

        return {
            "squad_size": len(players),
            "avg_skill_rating": total_skill / len(players),
            "top_scorer_goals": top_scorer_goals,
            "total_goals": total_goals,
            "total_assists": total_assists,
            "experienced_players": experienced_players,
            "young_prospects": young_prospects,
        }

    def _get_injury_stats(self, team):
        """Get injury-related statistics"""
        # Current injuries
        current_injuries = (
            InjuryReport.query.join(Player)
            .filter(Player.team_id == team.id, InjuryReport.status == "injured")
            .all()
        )

        # Key player injuries (high skill rating players)
        key_players_injured = sum(
            1 for injury in current_injuries if injury.player.skill_rating >= 70
        )

        # Total injury impact
        total_impact = 0
        position_impact = {"GK": 0, "DEF": 0, "MID": 0, "ATT": 0}

        for injury in current_injuries:
            player = injury.player
            impact = (player.skill_rating / 100) * (injury.severity / 10)
            total_impact += impact

            # Categorize position impact
            if player.position in ["GK"]:
                position_impact["GK"] += impact
            elif player.position in ["CB", "LB", "RB"]:
                position_impact["DEF"] += impact
            elif player.position in ["CM", "CDM", "CAM", "LW", "RW"]:
                position_impact["MID"] += impact
            elif player.position in ["ST", "CF"]:
                position_impact["ATT"] += impact

        return {
            "current_injuries": len(current_injuries),
            "key_players_injured": key_players_injured,
            "total_injury_impact": min(1.0, total_impact),  # Cap at 100%
            "goalkeeper_injuries": position_impact["GK"],
            "defense_injuries": position_impact["DEF"],
            "midfield_injuries": position_impact["MID"],
            "attack_injuries": position_impact["ATT"],
            "injury_severity_avg": sum(injury.severity for injury in current_injuries)
            / len(current_injuries)
            if current_injuries
            else 0,
        }

    def _calculate_performance_trends(self, team):
        """Calculate performance trends over time"""
        # Get matches from last 3 months
        three_months_ago = datetime.utcnow() - timedelta(days=90)
        recent_matches = (
            Match.query.filter(
                (Match.home_team_id == team.id) | (Match.away_team_id == team.id),
                Match.played == True,
                Match.match_date >= three_months_ago,
            )
            .order_by(Match.match_date.desc())
            .all()
        )

        if len(recent_matches) < 3:
            return {
                "scoring_trend": 0.0,
                "defensive_trend": 0.0,
                "form_trend": 0.0,
                "momentum": 0.0,
            }

        # Divide matches into recent and older periods
        mid_point = len(recent_matches) // 2
        recent_period = recent_matches[:mid_point]
        older_period = recent_matches[mid_point:]

        # Calculate trends
        def calculate_period_stats(matches):
            if not matches:
                return {"goals_for": 0, "goals_against": 0, "points": 0}

            goals_for = goals_against = points = 0
            for match in matches:
                if match.home_team_id == team.id:
                    gf, ga = match.home_score or 0, match.away_score or 0
                else:
                    gf, ga = match.away_score or 0, match.home_score or 0

                goals_for += gf
                goals_against += ga

                if gf > ga:
                    points += 3
                elif gf == ga:
                    points += 1

            return {
                "goals_for": goals_for / len(matches),
                "goals_against": goals_against / len(matches),
                "points": points / len(matches),
            }

        recent_stats = calculate_period_stats(recent_period)
        older_stats = calculate_period_stats(older_period)

        # Calculate trends (positive = improving, negative = declining)
        scoring_trend = recent_stats["goals_for"] - older_stats["goals_for"]
        defensive_trend = (
            older_stats["goals_against"] - recent_stats["goals_against"]
        )  # Lower goals against is better
        form_trend = recent_stats["points"] - older_stats["points"]

        # Overall momentum (weighted combination)
        momentum = scoring_trend * 0.4 + defensive_trend * 0.3 + form_trend * 0.3

        return {
            "scoring_trend": round(scoring_trend, 2),
            "defensive_trend": round(defensive_trend, 2),
            "form_trend": round(form_trend, 2),
            "momentum": round(momentum, 2),
        }

    def _get_head_to_head_stats(self, home_team, away_team):
        """Get head-to-head statistics between teams"""
        h2h_matches = (
            Match.query.filter(
                (
                    (Match.home_team_id == home_team.id)
                    & (Match.away_team_id == away_team.id)
                )
                | (
                    (Match.home_team_id == away_team.id)
                    & (Match.away_team_id == home_team.id)
                )
            )
            .filter(Match.played == True)
            .order_by(Match.match_date.desc())
            .limit(10)
            .all()
        )

        if not h2h_matches:
            return {
                "total_matches": 0,
                "home_team_wins": 0,
                "away_team_wins": 0,
                "draws": 0,
                "avg_goals_home": 1.5,
                "avg_goals_away": 1.5,
                "last_meeting": None,
                "home_team_dominance": 0.5,
            }

        stats = {
            "total_matches": len(h2h_matches),
            "home_team_wins": 0,
            "away_team_wins": 0,
            "draws": 0,
            "total_goals_home": 0,
            "total_goals_away": 0,
        }

        for match in h2h_matches:
            if match.home_team_id == home_team.id:
                # home_team was playing at home
                home_goals = match.home_score or 0
                away_goals = match.away_score or 0
            else:
                # home_team was playing away
                home_goals = match.away_score or 0
                away_goals = match.home_score or 0

            stats["total_goals_home"] += home_goals
            stats["total_goals_away"] += away_goals

            if home_goals > away_goals:
                stats["home_team_wins"] += 1
            elif home_goals < away_goals:
                stats["away_team_wins"] += 1
            else:
                stats["draws"] += 1

        stats["avg_goals_home"] = stats["total_goals_home"] / len(h2h_matches)
        stats["avg_goals_away"] = stats["total_goals_away"] / len(h2h_matches)
        stats["last_meeting"] = h2h_matches[0].match_date if h2h_matches else None

        # Calculate home team dominance (0-1 scale)
        total_points_home = stats["home_team_wins"] * 3 + stats["draws"]
        total_points_away = stats["away_team_wins"] * 3 + stats["draws"]
        total_points = total_points_home + total_points_away

        stats["home_team_dominance"] = (
            total_points_home / total_points if total_points > 0 else 0.5
        )

        return stats

    def _get_match_context(self):
        """Get additional match context factors"""
        return {
            "season": "2024-25",
            "league_competitiveness": 0.8,  # 0-1 scale
            "current_month": datetime.utcnow().month,
            "is_weekend": datetime.utcnow().weekday() >= 5,
            "weather_factor": 1.0,  # Neutral weather assumed
        }

    def calculate_team_statistics(self, team):
        """Calculate comprehensive team statistics for display"""
        stats = self._get_team_features(team, is_home=True)

        # Additional display statistics
        all_matches = Match.query.filter(
            (Match.home_team_id == team.id) | (Match.away_team_id == team.id),
            Match.played == True,
        ).all()

        if all_matches:
            total_matches = len(all_matches)
            wins = draws = losses = 0
            goals_for = goals_against = 0

            for match in all_matches:
                if match.home_team_id == team.id:
                    gf, ga = match.home_score or 0, match.away_score or 0
                else:
                    gf, ga = match.away_score or 0, match.home_score or 0

                goals_for += gf
                goals_against += ga

                if gf > ga:
                    wins += 1
                elif gf == ga:
                    draws += 1
                else:
                    losses += 1

            stats.update(
                {
                    "total_matches_played": total_matches,
                    "total_wins": wins,
                    "total_draws": draws,
                    "total_losses": losses,
                    "total_goals_for": goals_for,
                    "total_goals_against": goals_against,
                    "win_percentage": (wins / total_matches) * 100
                    if total_matches > 0
                    else 0,
                    "avg_goals_per_match": goals_for / total_matches
                    if total_matches > 0
                    else 0,
                    "goals_conceded_per_match": goals_against / total_matches
                    if total_matches > 0
                    else 0,
                }
            )
        else:
            stats.update(
                {
                    "total_matches_played": 0,
                    "total_wins": 0,
                    "total_draws": 0,
                    "total_losses": 0,
                    "total_goals_for": 0,
                    "total_goals_against": 0,
                    "win_percentage": 0,
                    "avg_goals_per_match": 0,
                    "goals_conceded_per_match": 0,
                }
            )

        return stats

    def normalize_features(self, features):
        """Normalize features for machine learning models"""
        normalized = {}

        # Define normalization ranges for different feature types
        normalization_rules = {
            "ratings": (0, 100),  # attack_rating, defense_rating, etc.
            "percentages": (0, 100),  # possession, form, etc.
            "counts": (0, 50),  # goals, shots, etc.
            "ratios": (0, 5),  # goals per match, etc.
        }

        for key, value in features.items():
            if isinstance(value, (int, float)):
                if "rating" in key or "form" in key:
                    normalized[key] = self._min_max_normalize(value, 0, 100)
                elif "possession" in key or "percentage" in key:
                    normalized[key] = self._min_max_normalize(value, 0, 100)
                elif "goals" in key or "shots" in key:
                    normalized[key] = self._min_max_normalize(value, 0, 10)
                else:
                    normalized[key] = value
            else:
                normalized[key] = value

        return normalized

    @staticmethod
    def _min_max_normalize(value, min_val, max_val):
        """Min-max normalization"""
        return (value - min_val) / (max_val - min_val) if max_val > min_val else 0
