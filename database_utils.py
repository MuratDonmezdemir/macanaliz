from app import db
from app.models import Team, Player, Match, Injury, TeamStatistics, Prediction
from datetime import datetime, timedelta
import random


def initialize_sample_data():
    """Initialize the database with sample teams and data"""

    # Check if data already exists
    if Team.query.count() > 0:
        print("Sample data already exists")
        return

    # Create sample teams (Turkish Super League)
    teams_data = [
        {
            "name": "Galatasaray",
            "country": "Turkey",
            "league": "Super Lig",
            "founded": 1905,
            "stadium": "Türk Telekom Stadium",
            "attack_strength": 85,
            "defense_strength": 75,
            "home_advantage": 8,
            "current_form": 78,
        },
        {
            "name": "Fenerbahçe",
            "country": "Turkey",
            "league": "Super Lig",
            "founded": 1907,
            "stadium": "Şükrü Saracoğlu Stadium",
            "attack_strength": 82,
            "defense_strength": 77,
            "home_advantage": 7,
            "current_form": 75,
        },
        {
            "name": "Beşiktaş",
            "country": "Turkey",
            "league": "Super Lig",
            "founded": 1903,
            "stadium": "Vodafone Park",
            "attack_strength": 78,
            "defense_strength": 72,
            "home_advantage": 9,
            "current_form": 70,
        },
        {
            "name": "Trabzonspor",
            "country": "Turkey",
            "league": "Super Lig",
            "founded": 1967,
            "stadium": "Medical Park Stadium",
            "attack_strength": 75,
            "defense_strength": 74,
            "home_advantage": 10,
            "current_form": 72,
        },
        {
            "name": "Başakşehir",
            "country": "Turkey",
            "league": "Super Lig",
            "founded": 1990,
            "stadium": "Başakşehir Fatih Terim Stadium",
            "attack_strength": 70,
            "defense_strength": 75,
            "home_advantage": 5,
            "current_form": 68,
        },
        {
            "name": "Konyaspor",
            "country": "Turkey",
            "league": "Super Lig",
            "founded": 1922,
            "stadium": "Konya Metropolitan Stadium",
            "attack_strength": 65,
            "defense_strength": 70,
            "home_advantage": 6,
            "current_form": 65,
        },
        {
            "name": "Antalyaspor",
            "country": "Turkey",
            "league": "Super Lig",
            "founded": 1966,
            "stadium": "Antalya Stadium",
            "attack_strength": 68,
            "defense_strength": 68,
            "home_advantage": 4,
            "current_form": 62,
        },
        {
            "name": "Kayserispor",
            "country": "Turkey",
            "league": "Super Lig",
            "founded": 1966,
            "stadium": "Kadir Has Stadium",
            "attack_strength": 62,
            "defense_strength": 65,
            "home_advantage": 5,
            "current_form": 60,
        },
        {
            "name": "Sivasspor",
            "country": "Turkey",
            "league": "Super Lig",
            "founded": 1967,
            "stadium": "Yeni 4 Eylül Stadium",
            "attack_strength": 63,
            "defense_strength": 72,
            "home_advantage": 7,
            "current_form": 64,
        },
        {
            "name": "Alanyaspor",
            "country": "Turkey",
            "league": "Super Lig",
            "founded": 1948,
            "stadium": "Bahçeşehir Okulları Stadium",
            "attack_strength": 69,
            "defense_strength": 66,
            "home_advantage": 4,
            "current_form": 66,
        },
    ]

    teams = []
    for team_data in teams_data:
        team = Team(**team_data)
        db.session.add(team)
        teams.append(team)

    db.session.commit()
    print(f"Created {len(teams)} teams")

    # Create sample players for each team
    positions = ["GK", "CB", "LB", "RB", "CDM", "CM", "CAM", "LW", "RW", "ST"]

    for team in teams:
        for i, position in enumerate(positions):
            player = Player(
                name=f"{team.name} {position} {i+1}",
                position=position,
                team_id=team.id,
                rating=random.randint(60, 90),
                goals=random.randint(0, 15)
                if position in ["ST", "CAM", "LW", "RW"]
                else random.randint(0, 5),
                assists=random.randint(0, 10) if position not in ["GK", "CB"] else 0,
                minutes_played=random.randint(500, 2500),
                is_injured=random.choice([True, False])
                if random.random() < 0.1
                else False,
            )
            db.session.add(player)

            # Add some injuries
            if player.is_injured:
                injury = Injury(
                    player_id=player.id,
                    injury_type=random.choice(
                        ["Muscle strain", "Ankle sprain", "Knee injury", "Hamstring"]
                    ),
                    severity=random.randint(20, 80),
                    start_date=datetime.now() - timedelta(days=random.randint(1, 30)),
                    expected_return_date=datetime.now()
                    + timedelta(days=random.randint(5, 45)),
                    is_active=True,
                )
                db.session.add(injury)

    db.session.commit()
    print("Created players and injuries")

    # Create sample matches and statistics
    current_date = datetime.now()
    season = "2024-25"

    for i in range(50):  # Create 50 sample matches
        home_team = random.choice(teams)
        away_team = random.choice([t for t in teams if t.id != home_team.id])

        match_date = current_date - timedelta(days=random.randint(1, 180))

        # Generate realistic match scores
        home_goals = random.choices(
            [0, 1, 2, 3, 4, 5], weights=[10, 25, 30, 20, 10, 5]
        )[0]
        away_goals = random.choices([0, 1, 2, 3, 4], weights=[15, 30, 30, 15, 10])[0]

        match = Match(
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            match_date=match_date,
            season=season,
            competition="Super Lig",
            home_goals=home_goals,
            away_goals=away_goals,
            home_goals_first_half=random.randint(0, max(1, home_goals)),
            away_goals_first_half=random.randint(0, max(1, away_goals)),
            home_shots=random.randint(8, 25),
            away_shots=random.randint(8, 25),
            home_shots_on_target=random.randint(2, 12),
            away_shots_on_target=random.randint(2, 12),
            home_possession=random.randint(35, 75),
            away_possession=random.randint(25, 65),
            home_pass_accuracy=random.randint(75, 95),
            away_pass_accuracy=random.randint(75, 95),
            is_played=True,
        )
        db.session.add(match)

    db.session.commit()
    print("Created sample matches")

    # Create team statistics
    for team in teams:
        team_matches = (
            Match.query.filter(
                (Match.home_team_id == team.id) | (Match.away_team_id == team.id)
            )
            .filter(Match.is_played == True)
            .all()
        )

        wins = draws = losses = 0
        goals_for = goals_against = 0
        home_wins = home_draws = home_losses = 0
        home_goals_for = home_goals_against = 0
        away_wins = away_draws = away_losses = 0
        away_goals_for = away_goals_against = 0
        clean_sheets = 0

        for match in team_matches:
            is_home = match.home_team_id == team.id

            if is_home:
                team_goals = match.home_goals
                opp_goals = match.away_goals
                goals_for += team_goals
                goals_against += opp_goals
                home_goals_for += team_goals
                home_goals_against += opp_goals

                if team_goals > opp_goals:
                    wins += 1
                    home_wins += 1
                elif team_goals == opp_goals:
                    draws += 1
                    home_draws += 1
                else:
                    losses += 1
                    home_losses += 1

                if opp_goals == 0:
                    clean_sheets += 1
            else:
                team_goals = match.away_goals
                opp_goals = match.home_goals
                goals_for += team_goals
                goals_against += opp_goals
                away_goals_for += team_goals
                away_goals_against += opp_goals

                if team_goals > opp_goals:
                    wins += 1
                    away_wins += 1
                elif team_goals == opp_goals:
                    draws += 1
                    away_draws += 1
                else:
                    losses += 1
                    away_losses += 1

                if opp_goals == 0:
                    clean_sheets += 1

        matches_played = len(team_matches)
        home_matches = len([m for m in team_matches if m.home_team_id == team.id])
        away_matches = matches_played - home_matches

        stats = TeamStatistics(
            team_id=team.id,
            season=season,
            matches_played=matches_played,
            wins=wins,
            draws=draws,
            losses=losses,
            goals_for=goals_for,
            goals_against=goals_against,
            home_matches=home_matches,
            home_wins=home_wins,
            home_draws=home_draws,
            home_losses=home_losses,
            home_goals_for=home_goals_for,
            home_goals_against=home_goals_against,
            away_matches=away_matches,
            away_wins=away_wins,
            away_draws=away_draws,
            away_losses=away_losses,
            away_goals_for=away_goals_for,
            away_goals_against=away_goals_against,
            average_goals_per_match=goals_for / max(matches_played, 1),
            average_goals_conceded=goals_against / max(matches_played, 1),
            clean_sheets=clean_sheets,
        )
        db.session.add(stats)

    db.session.commit()
    print("Created team statistics")
    print("Sample data initialization completed successfully!")


def get_team_recent_form(team_id, limit=5):
    """Get recent form for a team"""
    recent_matches = (
        Match.query.filter(
            (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
        )
        .filter(Match.is_played == True)
        .order_by(Match.match_date.desc())
        .limit(limit)
        .all()
    )

    form_data = []
    for match in recent_matches:
        is_home = match.home_team_id == team_id
        team_goals = match.home_goals if is_home else match.away_goals
        opp_goals = match.away_goals if is_home else match.home_goals

        if team_goals > opp_goals:
            result = "W"
        elif team_goals == opp_goals:
            result = "D"
        else:
            result = "L"

        form_data.append(
            {
                "date": match.match_date.strftime("%Y-%m-%d"),
                "opponent": match.away_team.name if is_home else match.home_team.name,
                "result": result,
                "score": f"{team_goals}-{opp_goals}",
                "is_home": is_home,
            }
        )

    return form_data


def get_head_to_head_stats(home_team_id, away_team_id, limit=10):
    """Get head-to-head statistics between two teams"""
    h2h_matches = (
        Match.query.filter(
            (
                (Match.home_team_id == home_team_id)
                & (Match.away_team_id == away_team_id)
            )
            | (
                (Match.home_team_id == away_team_id)
                & (Match.away_team_id == home_team_id)
            )
        )
        .filter(Match.is_played == True)
        .order_by(Match.match_date.desc())
        .limit(limit)
        .all()
    )

    home_wins = draws = away_wins = 0
    total_home_goals = total_away_goals = 0

    matches_data = []
    for match in h2h_matches:
        if match.home_team_id == home_team_id:
            # Current home team was home in this match
            home_goals = match.home_goals
            away_goals = match.away_goals
        else:
            # Current home team was away in this match
            home_goals = match.away_goals
            away_goals = match.home_goals

        total_home_goals += home_goals
        total_away_goals += away_goals

        if home_goals > away_goals:
            home_wins += 1
            result = "H"
        elif home_goals == away_goals:
            draws += 1
            result = "D"
        else:
            away_wins += 1
            result = "A"

        matches_data.append(
            {
                "date": match.match_date.strftime("%Y-%m-%d"),
                "score": f"{home_goals}-{away_goals}",
                "result": result,
            }
        )

    total_matches = len(h2h_matches)

    return {
        "total_matches": total_matches,
        "home_wins": home_wins,
        "draws": draws,
        "away_wins": away_wins,
        "home_win_percentage": (home_wins / max(total_matches, 1)) * 100,
        "away_win_percentage": (away_wins / max(total_matches, 1)) * 100,
        "average_home_goals": total_home_goals / max(total_matches, 1),
        "average_away_goals": total_away_goals / max(total_matches, 1),
        "matches": matches_data,
    }


def update_team_form(team_id):
    """Update team's current form based on recent matches"""
    recent_matches = (
        Match.query.filter(
            (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
        )
        .filter(Match.is_played == True)
        .order_by(Match.match_date.desc())
        .limit(5)
        .all()
    )

    if not recent_matches:
        return 50.0  # Default form

    form_points = 0
    total_matches = len(recent_matches)

    for i, match in enumerate(recent_matches):
        is_home = match.home_team_id == team_id
        team_goals = match.home_goals if is_home else match.away_goals
        opp_goals = match.away_goals if is_home else match.home_goals

        # Calculate points for this match
        if team_goals > opp_goals:
            points = 3  # Win
        elif team_goals == opp_goals:
            points = 1  # Draw
        else:
            points = 0  # Loss

        # Weight recent matches more heavily
        weight = 1.0 - (i * 0.1)  # Most recent = 1.0, oldest = 0.6
        form_points += points * weight

    # Convert to 0-100 scale
    max_possible_points = sum(3 * (1.0 - i * 0.1) for i in range(total_matches))
    form_percentage = (form_points / max_possible_points) * 100

    # Update team's current form
    team = Team.query.get(team_id)
    if team:
        team.current_form = form_percentage
        db.session.commit()

    return form_percentage
