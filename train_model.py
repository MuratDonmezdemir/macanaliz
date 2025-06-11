import os
import logging
from datetime import datetime, timedelta
from prediction_engine import MatchPredictor
from app import create_app, db
from app.models import Match

# Uygulama bağlamını oluştur
app = create_app()
app.app_context().push()

# Loglama ayarı
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def train_and_save_model():
    """Mevcut verilerle modeli eğitir ve kaydeder"""
    try:
        logger.info("Model eğitimi başlatılıyor...")

        # Tahmin motorunu başlat
        predictor = MatchPredictor(db.session)

        # Son 2 yılın maçlarını getir
        two_years_ago = datetime.utcnow() - timedelta(days=730)
        matches = Match.query.filter(
            Match.match_date >= two_years_ago,
            Match.status == "FINISHED",
            Match.home_team_score.isnot(None),
            Match.away_team_score.isnot(None),
        ).all()

        if not matches:
            logger.warning("Eğitim için yeterli maç verisi bulunamadı.")
            return False

        logger.info(f"{len(matches)} adet maç ile model eğitiliyor...")

        # Modeli eğit
        predictor.train_model(matches)

        # Modeli kaydet
        predictor.save_model()

        logger.info("Model başarıyla eğitildi ve kaydedildi.")
        return True

    except Exception as e:
        logger.error(f"Model eğitilirken hata oluştu: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    train_and_save_model()
