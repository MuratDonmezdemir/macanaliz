import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any

import requests
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models import Team, Match, Player
from config import Config

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FootballAPI:
    """Football API integration class for fetching and processing football data."""

    def __init__(self, api_key: str = None, base_url: str = None):
        """Initialize the Football API client.

        Args:
            api_key: Football API key (optional, will use from config if not provided)
            base_url: Base URL for the API (optional, will use from config if not provided)
        """
        self.api_key = api_key or Config.FOOTBALL_API_KEY
        self.base_url = base_url or Config.FOOTBALL_API_BASE_URL
        self.headers = {"X-Auth-Token": self.api_key} if self.api_key else {}
        self.rate_limit_remaining = 10
        self.rate_limit_reset = 60
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a request to the Football API.

        Args:
            endpoint: API endpoint (e.g., 'competitions/PL/teams')
            params: Query parameters for the request

        Returns:
            dict: JSON response from the API
        """
        if not self.api_key:
            logger.warning("No API key provided. Using sample data.")
            return {}

        url = f"{self.base_url}/{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            # Update rate limit info
            self.rate_limit_remaining = int(
                response.headers.get("X-Requests-Available", 10)
            )
            self.rate_limit_reset = int(
                response.headers.get("X-RequestCounter-Reset", 60)
            )

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {}

    def get_competitions(self) -> List[Dict]:
        """Get all available competitions.

        Returns:
            list: List of competition dictionaries
        """
        return self._make_request("competitions").get("competitions", [])

    def get_teams(self, competition_code: str, season: int = None) -> List[Dict]:
        """Get teams for a specific competition.

        Args:
            competition_code: Competition code (e.g., 'PL', 'PD', 'TR1')
            season: Season year (e.g., 2024)

        Returns:
            list: List of team dictionaries
        """
        params = {"season": season} if season else {}
        endpoint = f"competitions/{competition_code}/teams"
        return self._make_request(endpoint, params).get("teams", [])

    def get_matches(
        self,
        competition_code: str = None,
        team_id: int = None,
        status: str = None,
        date_from: str = None,
        date_to: str = None,
        limit: int = 10,
    ) -> List[Dict]:
        """Get matches based on filters.

        Args:
            competition_code: Filter by competition code
            team_id: Filter by team ID
            status: Filter by match status (e.g., 'FINISHED', 'SCHEDULED')
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            limit: Maximum number of matches to return

        Returns:
            list: List of match dictionaries
        """
        params = {}
        if competition_code:
            endpoint = f"competitions/{competition_code}/matches"
        elif team_id:
            endpoint = f"teams/{team_id}/matches"
        else:
            endpoint = "matches"

        if status:
            params["status"] = status
        if date_from:
            params["dateFrom"] = date_from
        if date_to:
            params["dateTo"] = date_to
        if limit:
            params["limit"] = limit

        return self._make_request(endpoint, params).get("matches", [])

    def get_team(self, team_id: int) -> Dict:
        """Get team details by ID.

        Args:
            team_id: Team ID

        Returns:
            dict: Team details
        """
        return self._make_request(f"teams/{team_id}")

    def get_standings(self, competition_code: str, season: int = None) -> List[Dict]:
        """Get competition standings.

        Args:
            competition_code: Competition code
            season: Season year

        Returns:
            list: List of standing tables
        """
        params = {"season": season} if season else {}
        endpoint = f"competitions/{competition_code}/standings"
        return self._make_request(endpoint, params).get("standings", [])

    def sync_teams_to_db(
        self, competition_code: str, season: int = None
    ) -> Tuple[int, int]:
        """Sync teams from API to database.

        Args:
            competition_code: Competition code
            season: Season year

        Returns:
            tuple: (number_of_teams_added, number_of_teams_updated)
        """
        try:
            teams_data = self.get_teams(competition_code, season)
            added = 0
            updated = 0

            for team_data in teams_data:
                team = Team.query.filter_by(api_id=team_data["id"]).first()

                if not team:
                    team = Team(
                        api_id=team_data["id"],
                        name=team_data["name"],
                        short_name=team_data.get("shortName", ""),
                        tla=team_data.get("tla", ""),
                        crest_url=team_data.get("crest", ""),
                        venue=team_data.get("venue", ""),
                        founded=team_data.get("founded"),
                        country=team_data.get("area", {}).get("name", ""),
                    )
                    db.session.add(team)
                    added += 1
                else:
                    team.name = team_data["name"]
                    team.short_name = team_data.get("shortName", team.short_name or "")
                    team.tla = team_data.get("tla", team.tla or "")
                    team.crest_url = team_data.get("crest", team.crest_url or "")
                    team.venue = team_data.get("venue", team.venue or "")
                    team.founded = team_data.get("founded", team.founded)
                    team.country = team_data.get("area", {}).get(
                        "name", team.country or ""
                    )
                    updated += 1

            db.session.commit()
            return added, updated

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error while syncing teams: {e}")
            return 0, 0
        except Exception as e:
            logger.error(f"Error syncing teams: {e}")
            return 0, 0


# Singleton instance
football_api = FootballAPI()
