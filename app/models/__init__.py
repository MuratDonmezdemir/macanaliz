"""
Modeller paketi

Bu paket, uygulamanın veritabanı modellerini içerir.
"""
from .base import db, BaseModel
from .enums import MatchStatus, TeamStatus, PredictionOutcome
from .team import Team
from .match import Match
from .prediction import Prediction
from .league import League

# Tüm modelleri dışa aktar
__all__ = [
    # Base
    "BaseModel",
    "db",
    # Enums
    "MatchStatus",
    "TeamStatus",
    "PredictionOutcome",
    # Core models
    "Team",
    "Match",
    "Prediction",
    "League",
    "MatchCard",
    "MatchGoal",
    "Prediction",
    "_TeamStatistics",
    "Player",
    "PlayerStatistics",
    "PlayerInjury",
    "PlayerTransfer",
    "Referee",
    # Yardımcı fonksiyonlar
    "init_models",
    "league_teams",  # Association tablosunu da dışa aktar
]

from ..utils.enums import TeamFormation, TeamStatus, TeamType, TeamGender
from .league import LeagueLevel, LeagueType


def init_models():
    """Modeller arası ilişkileri başlatır"""
    # Dairesel import sorunlarını önlemek için burada import ediyoruz
    from . import (
        user,
        athlete,
        stadium,
        season,
        league,
        team,
        match,
        standing,
        match_event,
        match_lineup,
        match_substitution,
        match_card,
        match_goal,
        prediction,
        team_statistics,
        player,
        player_injury,
        player_transfer,
    )

    # User - Athlete ilişkisi
    user.User.athlete = db.relationship(
        "Athlete",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True,
    )

    athlete.Athlete.user = db.relationship(
        "User", back_populates="athlete", uselist=False
    )

    # Team - Stadium ilişkisi
    team.Team.stadium = db.relationship(
        "Stadium", back_populates="teams", foreign_keys="Team.stadium_id", lazy="joined"
    )

    stadium.Stadium.teams = db.relationship(
        "Team",
        back_populates="stadium",
        foreign_keys="Team.stadium_id",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # League - Team ilişkisi (many-to-many)
    league.League.teams = db.relationship(
        "Team", secondary=league_teams, back_populates="leagues", lazy="dynamic"
    )

    team.Team.leagues = db.relationship(
        "League", secondary=league_teams, back_populates="teams", lazy="dynamic"
    )

    # League - Match ilişkisi
    league.League.matches = db.relationship(
        "Match",
        back_populates="league",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="Match.match_datetime.desc()",
        overlaps="league_matches",
    )

    match.Match.league = db.relationship(
        "League",
        back_populates="matches",
        foreign_keys="Match.league_id",
        lazy="joined",
        overlaps="league_matches,matches",
    )

    # Team - Match ilişkileri (home/away)
    team.Team.home_matches = db.relationship(
        "Match",
        foreign_keys="Match.home_team_id",
        back_populates="home_team",
        lazy="dynamic",
        cascade="all, delete-orphan",
        overlaps="away_team,home_team",
        order_by="desc(Match.match_datetime)",
    )

    team.Team.away_matches = db.relationship(
        "Match",
        foreign_keys="Match.away_team_id",
        back_populates="away_team",
        lazy="dynamic",
        cascade="all, delete-orphan",
        overlaps="home_team,away_team",
        order_by="desc(Match.match_datetime)",
    )

    match.Match.home_team = db.relationship(
        "Team",
        foreign_keys="Match.home_team_id",
        back_populates="home_matches",
        lazy="joined",
        overlaps="home_matches,home_team",
    )

    match.Match.away_team = db.relationship(
        "Team",
        foreign_keys="Match.away_team_id",
        back_populates="away_matches",
        lazy="joined",
        overlaps="away_matches,away_team",
    )

    # Match - Stadium ilişkisi
    match.Match.venue = db.relationship(
        "Stadium",
        foreign_keys="Match.venue_id",
        back_populates="matches",
        lazy="joined",
    )

    stadium.Stadium.matches = db.relationship(
        "Match",
        back_populates="venue",
        foreign_keys="Match.venue_id",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="desc(Match.match_datetime)",
    )

    # Match - MatchEvent ilişkisi
    match.Match.events = db.relationship(
        "MatchEvent",
        back_populates="match",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="MatchEvent.minute, MatchEvent.added_time, MatchEvent.id",
    )

    match_event.MatchEvent.match = db.relationship(
        "Match",
        back_populates="events",
        foreign_keys="MatchEvent.match_id",
        lazy="joined",
    )

    # Team - Player ilişkisi
    team.Team.players = db.relationship(
        "Player",
        back_populates="team",
        lazy="dynamic",
        cascade="all, delete-orphan",
        foreign_keys="Player.team_id",
        order_by="Player.jersey_number, Player.last_name, Player.first_name",
    )

    player.Player.team = db.relationship(
        "Team", back_populates="players", foreign_keys="Player.team_id", lazy="joined"
    )

    # Player - PlayerStatistics ilişkisi
    player.Player.statistics = db.relationship(
        "PlayerStatistics",
        back_populates="player",
        lazy="dynamic",
        cascade="all, delete-orphan",
        foreign_keys="PlayerStatistics.player_id",
    )

    # Player - PlayerInjury ilişkisi
    player.Player.injuries = db.relationship(
        "PlayerInjury",
        back_populates="player",
        lazy="dynamic",
        cascade="all, delete-orphan",
        foreign_keys="PlayerInjury.player_id",
        order_by="desc(PlayerInjury.injury_date)",
    )

    # Player - PlayerTransfer ilişkisi
    player.Player.transfers = db.relationship(
        "PlayerTransfer",
        back_populates="player",
        lazy="dynamic",
        cascade="all, delete-orphan",
        foreign_keys="PlayerTransfer.player_id",
        order_by="desc(PlayerTransfer.transfer_date)",
    )

    # Season ilişkileri
    season.Season.matches = db.relationship(
        "Match",
        back_populates="season",
        lazy="dynamic",
        foreign_keys="Match.season_id",
        order_by="desc(Match.match_datetime)",
    )

    season.Season.standings = db.relationship(
        "Standing",
        back_populates="season",
        lazy="dynamic",
        cascade="all, delete-orphan",
        foreign_keys="Standing.season_id",
        order_by="Standing.position",
    )

    # Standing ilişkileri
    standing.Standing.season = db.relationship(
        "Season",
        back_populates="standings",
        foreign_keys="Standing.season_id",
        lazy="joined",
    )

    standing.Standing.team = db.relationship(
        "Team", foreign_keys="Standing.team_id", lazy="joined"
    )

    # Prediction ilişkileri
    prediction.Prediction.match = db.relationship(
        "Match", foreign_keys="Prediction.match_id", lazy="joined"
    )

    prediction.Prediction.user = db.relationship(
        "User", foreign_keys="Prediction.user_id", lazy="joined"
    )

    # Model sınıflarını güncelle
    models: Dict[str, Type[BaseModel]] = {
        "User": user.User,
        "Athlete": athlete.Athlete,
        "Stadium": stadium.Stadium,
        "Season": season.Season,
        "League": league.League,
        "Team": team.Team,
        "Match": match.Match,
        "MatchStatistics": match.MatchStatistics,
        "MatchEvent": match_event.MatchEvent,
        "MatchLineup": match_lineup.MatchLineup,
        "MatchSubstitution": match_substitution.MatchSubstitution,
        "MatchCard": match_card.MatchCard,
        "MatchGoal": match_goal.MatchGoal,
        "Prediction": prediction.Prediction,
        "TeamStatistics": team_statistics.TeamStatistics,
        "Player": player.Player,
        "PlayerStatistics": player.PlayerStatistics,
        "PlayerInjury": player_injury.PlayerInjury,
        "PlayerTransfer": player_transfer.PlayerTransfer,
        "Standing": standing.Standing,
    }

    # Tüm modelleri BaseModel'in _registry'sine ekle
    for name, model in models.items():
        if not hasattr(BaseModel, name):
            setattr(BaseModel, name, model)

    return models
