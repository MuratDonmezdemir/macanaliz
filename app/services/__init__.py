"""
Servis katmanı modülleri.

Bu paket, uygulamanın iş mantığını içeren servis sınıflarını içerir.
"""

# Servisleri burada import edelim
from .football_data import FootballDataService

__all__ = [
    'FootballDataService',
]
