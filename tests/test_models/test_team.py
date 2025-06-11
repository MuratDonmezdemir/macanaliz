"""
Team modeli için testler.
"""
import os
import sys
import pytest
from datetime import datetime, timedelta

# Proje kök dizinini Python path'ine ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app import create_app, db
from app.models.team import Team, TeamSocialMedia, TeamColors
from app.models.enums import TeamStatus, TeamType, TeamGender, TeamFormation


@pytest.fixture
def app():
    """Test uygulamasını oluşturur."""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test istemcisini döndürür."""
    return app.test_client()


@pytest.fixture
def init_database():
    """Test veritabanını başlatır."""
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()


class TestTeamModel:
    """Team modeli için test sınıfı."""

    def test_create_team(self, app):
        """Yeni bir takım oluşturma testi."""
        with app.app_context():
            # Test verileri
            team_data = {
                "name": "Galatasaray SK",
                "short_name": "Galatasaray",
                "code": "GAL",
                "tff_id": 1001,
                "country": "Türkiye",
                "country_code": "TUR",
                "city": "İstanbul",
                "founded": 1905,
                "logo": "https://example.com/logo.png",
                "status": TeamStatus.ACTIVE,
                "team_type": TeamType.CLUB,
                "gender": TeamGender.MALE,
                "website": "https://www.galatasaray.org",
                "email": "info@galatasaray.org",
                "phone": "+902123111111",
                "address": "Türk Telekom Stadyumu, İstanbul",
                "nickname": "Cimbom",
                "description": "Galatasaray Spor Kulübü",
                "budget": 50000000.00,
                "market_value": 250000000.00,
                "average_age": 25.5,
                "foreign_players": 12,
                "formation": TeamFormation.FORMATION_433,
                "social_media": TeamSocialMedia(
                    facebook="galatasaray",
                    twitter="GalatasaraySK",
                    instagram="galatasaray",
                    youtube="galatasaray",
                    tiktok="galatasaray",
                    linkedin="galatasaray",
                ).to_dict(),
                "colors": TeamColors(
                    primary="E30A17", secondary="F9A01B", text="FFFFFF", accent="E30A17"
                ).to_dict(),
                "trophies": [
                    {"name": "Süper Lig", "count": 23},
                    {"name": "Türkiye Kupası", "count": 18},
                    {"name": "Süper Kupa", "count": 16},
                    {"name": "UEFA Kupası", "count": 1},
                    {"name": "UEFA Süper Kupası", "count": 1},
                ],
            }

            # Takım oluştur
            team = Team(**team_data)
            db.session.add(team)
            db.session.commit()

            # Veritabanından çek
            db_team = Team.query.first()

            # Doğrulamalar
            assert db_team is not None
            assert db_team.name == "Galatasaray SK"
            assert db_team.short_name == "Galatasaray"
            assert db_team.code == "GAL"
            assert db_team.tff_id == 1001
            assert db_team.country == "Türkiye"
            assert db_team.country_code == "TUR"
            assert db_team.city == "İstanbul"
            assert db_team.founded == 1905
            assert db_team.logo == "https://example.com/logo.png"
            assert db_team.status == TeamStatus.ACTIVE
            assert db_team.team_type == TeamType.CLUB
            assert db_team.gender == TeamGender.MALE
            assert db_team.website == "https://www.galatasaray.org"
            assert db_team.email == "info@galatasaray.org"
            assert db_team.phone == "+902123111111"
            assert db_team.address == "Türk Telekom Stadyumu, İstanbul"
            assert db_team.nickname == "Cimbom"
            assert db_team.description == "Galatasaray Spor Kulübü"
            assert float(db_team.budget) == 50000000.00
            assert float(db_team.market_value) == 250000000.00
            assert db_team.average_age == 25.5
            assert db_team.foreign_players == 12
            assert db_team.formation == TeamFormation.FORMATION_433
            assert isinstance(db_team.social_media, dict)
            assert "facebook" in db_team.social_media
            assert "youtube" in db_team.social_media
            assert isinstance(db_team.colors, dict)
            assert "primary" in db_team.colors
            assert "secondary" in db_team.colors
            assert isinstance(db_team.trophies, list)
            assert len(db_team.trophies) == 5
            assert db_team.created_at is not None
            assert db_team.updated_at is not None

    def test_team_relationships(self, app):
        """Takım ilişkilerini test eder."""
        with app.app_context():
            # Test verileri
            team = Team(
                name="Test Takımı",
                short_name="Test",
                code="TST",
                country="Türkiye",
                status=TeamStatus.ACTIVE,
                team_type=TeamType.CLUB,
                gender=TeamGender.MALE,
            )
            db.session.add(team)
            db.session.commit()

            # İlişkilerin varlığını kontrol et
            assert hasattr(team, "players")
            assert hasattr(team, "home_matches")
            assert hasattr(team, "away_matches")
            assert hasattr(team, "match_statistics")
            assert hasattr(team, "standings")
            assert hasattr(team, "statistics")
            assert hasattr(team, "lineups")
            assert hasattr(team, "substitutions")
            assert hasattr(team, "cards")
            assert hasattr(team, "goals")

    def test_team_methods(self, app):
        """Takım metodlarını test eder."""
        with app.app_context():
            # Test takımı oluştur
            team = Team(
                name="Test Takımı",
                short_name="Test",
                code="TST",
                country="Türkiye",
                status=TeamStatus.ACTIVE,
                team_type=TeamType.CLUB,
                gender=TeamGender.MALE,
                founded=2020,
            )
            db.session.add(team)
            db.session.commit()

            # to_dict() metodu
            team_dict = team.to_dict()
            assert isinstance(team_dict, dict)
            assert team_dict["name"] == "Test Takımı"
            assert team_dict["short_name"] == "Test"
            assert team_dict["code"] == "TST"

            # include_related=True ile to_dict()
            team_dict_with_related = team.to_dict(include_related=True)
            assert "stadium" in team_dict_with_related
            assert "league" in team_dict_with_related
            assert "recent_matches" in team_dict_with_related
            assert "upcoming_matches" in team_dict_with_related
            assert "top_scorers" in team_dict_with_related

            # get_form() metodu
            form = team.get_form(5)
            assert isinstance(form, list)

            # get_top_scorers() metodu
            top_scorers = team.get_top_scorers(5)
            assert isinstance(top_scorers, list)

            # goal_difference ve win_percentage özellikleri
            assert hasattr(team, "goal_difference")
            assert hasattr(team, "win_percentage")

            # current_season_stats özelliği
            assert hasattr(team, "current_season_stats")

    def test_team_validation(self, app):
        """Takım doğrulama kurallarını test eder."""
        with app.app_context():
            # Geçersiz veri ile takım oluşturmayı dene
            with pytest.raises(ValueError):
                team = Team(
                    name="A" * 101,  # Çok uzun isim
                    short_name="Test",
                    code="TST",
                    country="Türkiye",
                )
                db.session.add(team)
                db.session.commit()

            # Geçersiz enum değeri ile deneme
            with pytest.raises(ValueError):
                team = Team(
                    name="Geçersiz Takım",
                    short_name="Test",
                    code="TST",
                    country="Türkiye",
                    status="INVALID_STATUS",  # Geçersiz durum
                )
                db.session.add(team)
                db.session.commit()

            # Negatif bütçe ile deneme
            with pytest.raises(ValueError):
                team = Team(
                    name="Negatif Bütçe",
                    short_name="Test",
                    code="TST",
                    country="Türkiye",
                    budget=-1000,  # Negatif bütçe
                )
                db.session.add(team)
                db.session.commit()


class TestTeamSocialMedia:
    """TeamSocialMedia veri sınıfı için testler."""

    def test_create_social_media(self):
        """Sosyal medya bilgileri oluşturma testi."""
        sm = TeamSocialMedia(
            website="https://example.com",
            facebook="example",
            twitter="example",
            instagram="example",
            youtube="example",
            tiktok="example",
            linkedin="example",
        )

        assert sm.website == "https://example.com"
        assert sm.facebook == "example"
        assert sm.twitter == "example"
        assert sm.instagram == "example"
        assert sm.youtube == "example"
        assert sm.tiktok == "example"
        assert sm.linkedin == "example"

        # to_dict() metodu
        sm_dict = sm.to_dict()
        assert isinstance(sm_dict, dict)
        assert sm_dict["website"] == "https://example.com"
        assert sm_dict["facebook"] == "example"


class TestTeamColors:
    """TeamColors veri sınıfı için testler."""

    def test_create_colors(self):
        """Takım renkleri oluşturma testi."""
        colors = TeamColors(
            primary="#FF0000", secondary="#FFFFFF", text="#000000", accent="#FFA500"
        )

        assert colors.primary == "#FF0000"
        assert colors.secondary == "#FFFFFF"
        assert colors.text == "#000000"
        assert colors.accent == "#FFA500"

        # to_dict() metodu
        colors_dict = colors.to_dict()
        assert isinstance(colors_dict, dict)
        assert colors_dict["primary"] == "#FF0000"
        assert colors_dict["secondary"] == "#FFFFFF"
