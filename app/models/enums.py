"""Uygulama genelinde kullanılan enum'lar."""
from enum import Enum

class MatchStatus(str, Enum):
    """Maç durumları"""
    SCHEDULED = "scheduled"  # Planlandı
    TIMED = "timed"  # Zamanı belli
    IN_PLAY = "in_play"  # Oynanıyor
    FINISHED = "finished"  # Tamamlandı
    POSTPONED = "postponed"  # Ertelendi
    CANCELLED = "cancelled"  # İptal edildi

class TeamStatus(str, Enum):
    """Takım durumları"""
    ACTIVE = "active"  # Aktif
    INACTIVE = "inactive"  # Pasif

class PredictionOutcome(str, Enum):
    """Tahmin sonuçları"""
    HOME_WIN = "1"  # Ev sahibi kazanır
    DRAW = "X"      # Beraberlik
    AWAY_WIN = "2"  # Deplasman kazanır
