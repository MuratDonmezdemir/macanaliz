import os
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from app import db

from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from app.models.match import Match
from sklearn.ensemble import GradientBoostingClassifier
from joblib import dump, load
from typing import Dict, List, Tuple, Optional, Union
from scipy.stats import poisson
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.multioutput import MultiOutputRegressor
from sqlalchemy.orm import Session

# Loglama ayarı
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MatchPredictor:
    """Futbol maçı tahminleri için makine öğrenmesi tabanlı tahmin motoru"""

    def __init__(self, db_session: Session, league_id: int = None):
        """
        Tahmin motorunu başlat

        Args:
            db_session: SQLAlchemy veritabanı oturumu
            league_id: Belirli bir lig için model kullanılacaksa lig ID'si
        """
        self.db = db_session
        self.league_id = league_id
        self.model = None
        self.scaler = StandardScaler()

        # Model dosya yollarını lige özgü hale getir
        if league_id:
            self.model_path = f"models/match_predictor_league_{league_id}.joblib"
            self.scaler_path = f"models/scaler_league_{league_id}.joblib"
        else:
            self.model_path = "models/match_predictor_global.joblib"
            self.scaler_path = "models/scaler_global.joblib"

        self._initialize_model()

    def _initialize_model(self) -> None:
        """Tahmin modelini başlat veya önceden eğitilmiş modeli yükle"""
        try:
            os.makedirs("models", exist_ok=True)

            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = load(self.model_path)
                self.scaler = load(self.scaler_path)
                logger.info("Önceden eğitilmiş model ve scaler yüklendi")
            else:
                self._create_new_model()
        except Exception as e:
            logger.error(f"Model yüklenirken hata oluştu: {str(e)}")
            self._create_new_model()

    def _create_new_model(self) -> None:
        """Yeni bir tahmin modeli oluştur"""
        try:
            base_model = GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=5,
                random_state=42,
                min_samples_split=8,
                min_samples_leaf=4,
                subsample=0.8,
            )

            self.model = MultiOutputRegressor(base_model)
            logger.info("Yeni çoklu çıktılı model oluşturuldu")

            # Modeli kaydet
            self.save_model()

        except Exception as e:
            logger.error(f"Yeni model oluşturulurken hata: {str(e)}")
            raise

    def save_model(self) -> bool:
        """Modeli ve scaler'ı diske kaydet"""
        try:
            if self.model:
                dump(self.model, self.model_path)
                dump(self.scaler, self.scaler_path)
                logger.info("Model ve scaler başarıyla kaydedildi")
                return True
            return False
        except Exception as e:
            logger.error(f"Model kaydedilirken hata: {str(e)}")
            return False

    def get_team_form(
        self,
        team_id: int,
        match_date: datetime,
        matches_back: int = 5,
        league_id: int = None,
    ) -> Dict[str, Union[int, float, List[str]]]:
        """
        Takımın son maçlardaki formunu getirir

        Args:
            team_id: Takım ID'si
            match_date: Referans tarihi
            matches_back: İncelenecek maç sayısı

        Returns:
            Takım formu ile ilgili istatistikler
        """
        from app.models import Match

        try:
            from app.models import Match, Team

            query = (
                self.db.query(Match)
                .join(
                    Team,
                    ((Match.home_team_id == Team.id) | (Match.away_team_id == Team.id)),
                )
                .filter(
                    ((Match.home_team_id == team_id) | (Match.away_team_id == team_id)),
                    Match.match_date < match_date,
                    Match.status == "FINISHED",
                    Match.home_score.isnot(None),
                    Match.away_score.isnot(None),
                )
            )

            if league_id is not None:
                query = query.filter(Team.league_id == league_id)

            matches = query.order_by(Match.match_date.desc()).limit(matches_back).all()

            if not matches:
                return {
                    "wins": 0,
                    "draws": 0,
                    "losses": 0,
                    "goals_for": 0,
                    "goals_against": 0,
                    "form": [],
                    "points": 0,
                    "avg_goals_for": 0,
                    "avg_goals_against": 0,
                    "clean_sheets": 0,
                    "failed_to_score": 0,
                }

            form = []
            wins = draws = losses = 0
            goals_for = goals_against = 0
            clean_sheets = failed_to_score = 0

            for match in matches:
                is_home = match.home_team_id == team_id
                team_goals = match.home_goals if is_home else match.away_goals
                opponent_goals = match.away_goals if is_home else match.home_goals

                team_goals = team_goals or 0
                opponent_goals = opponent_goals or 0

                goals_for += team_goals
                goals_against += opponent_goals

                if opponent_goals == 0:
                    clean_sheets += 1
                if team_goals == 0:
                    failed_to_score += 1

                if team_goals > opponent_goals:
                    form.append("W")
                    wins += 1
                elif team_goals == opponent_goals:
                    form.append("D")
                    draws += 1
                else:
                    form.append("L")
                    losses += 1

            total_matches = len(matches)
            return {
                "wins": wins,
                "draws": draws,
                "losses": losses,
                "goals_for": goals_for,
                "goals_against": goals_against,
                "form": form,
                "points": wins * 3 + draws,
                "avg_goals_for": round(goals_for / total_matches, 2)
                if total_matches > 0
                else 0,
                "avg_goals_against": round(goals_against / total_matches, 2)
                if total_matches > 0
                else 0,
                "clean_sheets": clean_sheets,
                "clean_sheet_percent": round((clean_sheets / total_matches) * 100, 1)
                if total_matches > 0
                else 0,
                "failed_to_score": failed_to_score,
                "failed_to_score_percent": round(
                    (failed_to_score / total_matches) * 100, 1
                )
                if total_matches > 0
                else 0,
            }

        except Exception as e:
            logger.error(f"Takım formu alınırken hata (Takım ID: {team_id}): {str(e)}")
            return {
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "goals_for": 0,
                "goals_against": 0,
                "form": [],
                "points": 0,
                "avg_goals_for": 0,
                "avg_goals_against": 0,
                "clean_sheets": 0,
                "failed_to_score": 0,
                "clean_sheet_percent": 0,
                "failed_to_score_percent": 0,
            }

    def _simple_prediction(self, home_form: dict, away_form: dict) -> dict:
        """Model yokken kullanılacak basit tahmin metodu"""
        try:
            # Basit bir skor tahmini
            home_attack = home_form.get("avg_goals_for", 1.2)
            away_attack = away_form.get("avg_goals_for", 1.0)
            home_defense = home_form.get("avg_goals_against", 1.0)
            away_defense = away_form.get("avg_goals_against", 1.2)

            # Ev sahibi avantajı (%15)
            home_advantage = 1.15

            # Beklenen goller
            home_expected = (home_attack + away_defense) / 2 * home_advantage
            away_expected = (away_attack + home_defense) / 2

            # 5+ gol olasılığı
            high_scoring_prob = self._calculate_high_scoring_prob(
                home_expected, away_expected
            )

            # Maç sonucu olasılıkları
            (
                home_win_prob,
                draw_prob,
                away_win_prob,
            ) = self._calculate_outcome_probabilities(home_expected, away_expected)

            return {
                "match_prediction": {
                    "home_win_prob": round(home_win_prob, 3),
                    "draw_prob": round(draw_prob, 3),
                    "away_win_prob": round(away_win_prob, 3),
                },
                "expected_goals": {
                    "home": round(home_expected, 2),
                    "away": round(away_expected, 2),
                },
                "high_scoring_prob": round(high_scoring_prob, 3),
                "home_team_form": home_form,
                "away_team_form": away_form,
                "model_used": "simple",
                "note": "Basit model kullanıldı (ML modeli yok veya yetersiz veri)",
            }

        except Exception as e:
            logger.error(f"Basit tahmin yapılırken hata: {str(e)}")
            return {"error": "Tahmin yapılırken bir hata oluştu", "details": str(e)}

    def _calculate_high_scoring_prob(
        self, home_goals: float, away_goals: float
    ) -> float:
        """5+ gol olma olasılığını hesaplar"""
        try:
            total_goals = home_goals + away_goals
            # 0-4 gol olma olasılığını hesapla
            prob_under_5 = sum(poisson.pmf(i, total_goals) for i in range(5))
            # 5+ gol olma olasılığı
            return max(0, min(1, 1 - prob_under_5))
        except Exception as e:
            logger.error(f"Yüksek skor olasılığı hesaplanırken hata: {str(e)}")
            return 0.0

    def _calculate_outcome_probabilities(
        self, home_goals: float, away_goals: float
    ) -> Tuple[float, float, float]:
        """Maç sonucu olasılıklarını hesaplar"""
        try:
            # Poisson dağılımına göre olasılıkları hesapla
            home_win_prob = 0.0
            draw_prob = 0.0
            away_win_prob = 0.0

            # Maksimum gol sayısı (hesaplama için)
            max_goals = 10

            for i in range(max_goals):  # Ev sahibi golleri
                for j in range(max_goals):  # Deplasman golleri
                    prob = poisson.pmf(i, home_goals) * poisson.pmf(j, away_goals)
                    if i > j:
                        home_win_prob += prob
                    elif i == j:
                        draw_prob += prob
                    else:
                        away_win_prob += prob

            # Olasılıkları normalize et
            total = home_win_prob + draw_prob + away_win_prob
            if total > 0:
                home_win_prob /= total
                draw_prob /= total
                away_win_prob /= total

            return home_win_prob, draw_prob, away_win_prob

        except Exception as e:
            logger.error(f"Maç sonucu olasılıkları hesaplanırken hata: {str(e)}")
            # Varsayılan olasılıklar
            return 0.4, 0.3, 0.3

    def prepare_match_features(
        self,
        home_team_id: int,
        away_team_id: int,
        match_date: datetime,
        league_id: int = None,
    ) -> Optional[np.ndarray]:
        """Maç için özellik vektörünü hazırlar"""
        try:
            # Takım formlarını al
            home_form = self.get_team_form(
                home_team_id, match_date, league_id=league_id
            )
            away_form = self.get_team_form(
                away_team_id, match_date, league_id=league_id
            )

            # Temel özellikler
            features = [
                home_form["avg_goals_for"],
                home_form["avg_goals_against"],
                home_form["points"]
                / (
                    3
                    * (
                        home_form["wins"] + home_form["draws"] + home_form["losses"]
                        or 1
                    )
                ),
                away_form["avg_goals_for"],
                away_form["avg_goals_against"],
                away_form["points"]
                / (
                    3
                    * (
                        away_form["wins"] + away_form["draws"] + away_form["losses"]
                        or 1
                    )
                ),
                home_form["clean_sheet_percent"] / 100,
                away_form["clean_sheet_percent"] / 100,
                home_form["failed_to_score_percent"] / 100,
                away_form["failed_to_score_percent"] / 100,
            ]

            # Son 5 maç formu (son maç en önemli)
            for i in range(min(5, len(home_form["form"]))):
                # Galibiyet: 1, Beraberlik: 0, Mağlubiyet: -1
                if home_form["form"][i] == "W":
                    features.append(1.0)
                elif home_form["form"][i] == "D":
                    features.append(0.0)
                else:
                    features.append(-1.0)

            for i in range(min(5, len(away_form["form"]))):
                if away_form["form"][i] == "W":
                    features.append(1.0)
                elif away_form["form"][i] == "D":
                    features.append(0.0)
                else:
                    features.append(-1.0)

            # Eksik form verileri için sıfır ekle
            while len(features) < 20:  # Toplam 20 özellik
                features.append(0.0)

            return np.array(features[:20])  # İlk 20 özelliği al

        except Exception as e:
            logger.error(f"Özellik hazırlanırken hata: {str(e)}")
            return None

    def predict_match(
        self,
        home_team_id: int,
        away_team_id: int,
        match_date: datetime = None,
        league_id: int = None,
    ) -> Dict:
        """
        Maç için kapsamlı tahmin yapar

        Args:
            home_team_id: Ev sahibi takım ID'si
            away_team_id: Deplasman takım ID'si
            match_date: Maç tarihi (varsayılan: şu an)
            league_id: Lig ID'si (isteğe bağlı)

        Returns:
            Tahmin sonuçları (skor, yarı sonuçları, 5+ gol olasılığı vb.)
        """
        if match_date is None:
            match_date = datetime.now()

        # Eğer farklı bir lig için tahmin yapılıyorsa, modeli güncelle
        if league_id is not None and league_id != self.league_id:
            self.league_id = league_id
            self.model_path = f"models/match_predictor_league_{league_id}.joblib"
            self.scaler_path = f"models/scaler_league_{league_id}.joblib"
            self._initialize_model()

        try:
            # Takım formlarını al
            home_form = self.get_team_form(
                home_team_id, match_date, league_id=league_id
            )
            away_form = self.get_team_form(
                away_team_id, match_date, league_id=league_id
            )

            # Eğer model yoksa veya boşsa, basit bir tahmin yap
            if self.model is None:
                return self._simple_prediction(home_form, away_form)

            # Özellik vektörünü hazırla
            features = self.prepare_match_features(
                home_team_id, away_team_id, match_date, league_id
            )
            if features is None:
                logger.warning("Özellik hazırlanamadı, basit tahmin yapılıyor...")
                return self._simple_prediction(home_form, away_form)

            # Tahmin yap
            predicted_scores = self.model.predict(features.reshape(1, -1))[0]
            home_goals = max(0, round(predicted_scores[0], 1))
            away_goals = max(0, round(predicted_scores[1], 1))

            # 5+ gol olasılığı
            high_scoring_prob = self._calculate_high_scoring_prob(
                home_goals, away_goals
            )

            # Maç sonucu olasılıkları
            (
                home_win_prob,
                draw_prob,
                away_win_prob,
            ) = self._calculate_outcome_probabilities(home_goals, away_goals)

            return {
                "match_prediction": {
                    "home_win_prob": round(home_win_prob, 3),
                    "draw_prob": round(draw_prob, 3),
                    "away_win_prob": round(away_win_prob, 3),
                },
                "expected_goals": {
                    "home": round(home_goals, 2),
                    "away": round(away_goals, 2),
                },
                "high_scoring_prob": round(high_scoring_prob, 3),
                "home_team_form": home_form,
                "away_team_form": away_form,
                "league_id": league_id if league_id else self.league_id,
                "model_used": f"league_{self.league_id}"
                if self.league_id
                else "global",
            }

        except Exception as e:
            logger.error(
                f"Maç tahmini yapılırken hata (Ev: {home_team_id}, Deplasman: {away_team_id}): {str(e)}"
            )
            return {"error": "Tahmin yapılırken bir hata oluştu", "details": str(e)}


class MatchPredictor:
    """Futbol maçı tahminleri için makine öğrenmesi tabanlı tahmin motoru"""

    def _initialize_model(self) -> None:
        """Tahmin modelini başlat veya önceden eğitilmiş modeli yükle"""
        try:
            os.makedirs("models", exist_ok=True)

            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = load(self.model_path)
                self.scaler = load(self.scaler_path)
                logger.info(
                    f"Önceden eğitilmiş model ve scaler yüklendi: {self.model_path}"
                )
            else:
                self._create_new_model()
        except Exception as e:
            logger.error(f"Model yüklenirken hata oluştu: {str(e)}")
            self._create_new_model()

    def _create_new_model(self) -> None:
        """Yeni bir tahmin modeli oluştur"""
        try:
            base_model = GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=5,
                random_state=42,
                min_samples_split=8,
                min_samples_leaf=4,
                subsample=0.8,
            )

            self.model = MultiOutputRegressor(base_model)
            logger.info("Yeni çoklu çıktılı model oluşturuldu")

            # Modeli kaydet
            self.save_model()

        except Exception as e:
            logger.error(f"Yeni model oluşturulurken hata: {str(e)}")
            raise

    def save_model(self):
        """Save the trained model to disk"""
        if self.model:
            dump(self.model, self.model_path)

    def find_high_draw_probability_matches(self, matches, min_draw_prob=0.35):
        """Berabere kalma ihtimali yüksek maçları bulur

        Args:
            matches: Tahmin yapılacak maç listesi
            min_draw_prob: Minimum beraberlik olasılığı (0-1 arası)

        Returns:
            list: Berabere kalma ihtimali yüksek maçların listesi
        """
        high_draw_matches = []

        for match in matches:
            try:
                # Maç tahminini yap
                prediction = self.predict_match(
                    match["home_team_id"],
                    match["away_team_id"],
                    datetime.strptime(match["match_date"], "%Y-%m-%d")
                    if isinstance(match["match_date"], str)
                    else match["match_date"],
                )

                # Beraberlik olasılığını kontrol et
                if (
                    prediction
                    and prediction.get("match_prediction", {}).get("draw_prob", 0)
                    >= min_draw_prob
                ):
                    high_draw_matches.append(
                        {
                            "match": match,
                            "prediction": prediction,
                            "draw_probability": prediction["match_prediction"][
                                "draw_prob"
                            ],
                        }
                    )

            except Exception as e:
                logger.error(
                    f"Berabere maç analizinde hata (Maç ID: {match.get('id')}): {str(e)}"
                )
                continue

        # Beraberlik olasılığına göre sırala (yüksekten düşüğe)
        return sorted(
            high_draw_matches, key=lambda x: x["draw_probability"], reverse=True
        )

    def get_team_form(self, team_id, match_date, matches_back=5):
        """Takımın son maçlardaki formunu getirir"""
        try:
            matches = (
                self.db.session.query(Match)
                .filter(
                    ((Match.home_team_id == team_id) | (Match.away_team_id == team_id)),
                    Match.match_date < match_date,
                    Match.status == "FINISHED",
                )
                .order_by(Match.match_date.desc())
                .limit(matches_back)
                .all()
            )

            if not matches:
                return {
                    "wins": 0,
                    "draws": 0,
                    "losses": 0,
                    "goals_for": 0,
                    "goals_against": 0,
                    "form": [],
                }

            form = []
            wins = draws = losses = 0
            goals_for = goals_against = 0

            for match in matches:
                is_home = match.home_team_id == team_id

                if is_home:
                    team_goals = match.home_goals or 0
                    opponent_goals = match.away_goals or 0
                else:
                    team_goals = match.away_goals or 0
                    opponent_goals = match.home_goals or 0

                goals_for += team_goals
                goals_against += opponent_goals

                if team_goals > opponent_goals:
                    form.append("W")
                    wins += 1
                elif team_goals == opponent_goals:
                    form.append("D")
                    draws += 1
                else:
                    form.append("L")
                    losses += 1

            return {
                "wins": wins,
                "draws": draws,
                "losses": losses,
                "goals_for": goals_for,
                "goals_against": goals_against,
                "form": form,
                "points": wins * 3 + draws,
                "avg_goals_for": round(goals_for / len(matches), 2) if matches else 0,
                "avg_goals_against": round(goals_against / len(matches), 2)
                if matches
                else 0,
            }

        except Exception as e:
            logger.error(f"Takım formu alınırken hata: {str(e)}")
            form = []

        # Pad with None if not enough matches
        while len(form) < matches_back:
            form.append(None)

        return form[:matches_back]

    def prepare_match_data(
        self, home_team_id, away_team_id, match_date, matches_back=5
    ):
        """Prepare feature vector for prediction"""
        home_form = self.get_team_form(home_team_id, match_date, matches_back)
        away_form = self.get_team_form(away_team_id, match_date, matches_back)

        # Convert form to features (count of W/D/L in last 5 matches)
        def form_to_features(form):
            return [
                form.count("W"),
                form.count("D"),
                form.count("L"),
                len([x for x in form if x is not None]),  # Number of matches available
            ]

        home_features = form_to_features(home_form)
        away_features = form_to_features(away_form)

        # Combine features
        features = home_features + away_features

        return np.array(features).reshape(1, -1)

    def predict_match(self, home_team_id, away_team_id, match_date=None):
        """Predict match outcome"""
        if match_date is None:
            match_date = datetime.now()

        # Prepare features
        X = self.prepare_match_data(home_team_id, away_team_id, match_date)

        # Make prediction
        if self.model:
            proba = self.model.predict_proba(X)[0]
            prediction = self.model.predict(X)[0]

            return {
                "home_win_prob": float(proba[0]),
                "draw_prob": float(proba[1]),
                "away_win_prob": float(proba[2]),
                "prediction": ["Home Win", "Draw", "Away Win"][prediction],
            }
        return None

    def calculate_high_scoring_probability(
        self, home_team_id: int, away_team_id: int, match_date: datetime = None
    ) -> float:
        """
        Maçta 5+ gol olma olasılığını hesaplar

        Args:
            home_team_id: Ev sahibi takım ID'si
            away_team_id: Deplasman takım ID'si
            match_date: Maç tarihi (varsayılan: şu an)

        Returns:
            float: 5+ gol olma olasılığı (0-1 arasında)
        """
        try:
            if match_date is None:
                match_date = datetime.now()

            # Son 10 maçın gol ortalamalarını al
            home_goals_avg = self._get_average_goals(
                home_team_id, match_date, is_home=True
            )
            away_goals_avg = self._get_average_goals(
                away_team_id, match_date, is_home=False
            )

            # Toplam gol ortalaması (ev sahibi avantajı ile birlikte)
            total_avg = (home_goals_avg * 1.2) + (away_goals_avg * 0.8)

            # Poisson dağılımı ile 5+ gol olasılığını hesapla
            prob = 1 - sum(
                [
                    (total_avg**k * np.exp(-total_avg)) / np.math.factorial(k)
                    for k in range(5)
                ]
            )

            return round(prob, 4)

        except Exception as e:
            logger.error(f"5+ gol olasılığı hesaplanırken hata: {str(e)}")
            return 0.0

    def _get_average_goals(
        self, team_id: int, match_date: datetime, is_home: bool
    ) -> float:
        """Takımın son maçlarındaki gol ortalamasını hesaplar"""
        try:
            # Son 10 maçı getir
            matches = (
                self.db.query(Match)
                .filter(
                    ((Match.home_team_id == team_id) | (Match.away_team_id == team_id)),
                    Match.date < match_date,
                    Match.home_goals.isnot(None),
                    Match.away_goals.isnot(None),
                )
                .order_by(Match.date.desc())
                .limit(10)
                .all()
            )

            if not matches:
                return 1.5  # Varsayılan ortalama

            total_goals = 0
            match_count = 0

            for match in matches:
                if match.home_team_id == team_id:
                    total_goals += match.home_goals
                else:
                    total_goals += match.away_goals
                match_count += 1

            return total_goals / match_count if match_count > 0 else 1.5

        except Exception as e:
            logger.error(f"Gol ortalaması hesaplanırken hata: {str(e)}")
            return 1.5

    def train_model(self, matches=None, league_id: int = None):
        """
        Tahmin modelini eğitir

        Args:
            matches: Eğitim verisi olarak kullanılacak maçlar (None ise tüm maçlar kullanılır)
            league_id: Belirli bir lig için eğitim yapılacaksa lig ID'si
        """
        if league_id is not None:
            logger.info(f"{league_id} ligi için model eğitimi başlatılıyor...")
            self.league_id = league_id
            self.model_path = f"models/match_predictor_league_{league_id}.joblib"
            self.scaler_path = f"models/scaler_league_{league_id}.joblib"
        else:
            logger.info("Tüm ligler için global model eğitimi başlatılıyor...")
            self.league_id = None
            self.model_path = "models/match_predictor_global.joblib"
            self.scaler_path = "models/scaler_global.joblib"

        # Eğitim verisi sağlanmamışsa veritabanından çek
        if matches is None:
            from app.models import Match, Team

            query = (
                self.db.query(Match)
                .join(Team, Match.home_team_id == Team.id)
                .filter(
                    Match.status == "FINISHED",
                    Match.home_score.isnot(None),
                    Match.away_score.isnot(None),
                )
            )

            if league_id is not None:
                query = query.filter(Team.league_id == league_id)

            matches = query.order_by(Match.match_date.desc()).limit(5000).all()

        if not matches:
            logger.warning("Eğitim için maç bulunamadı")
            return

        logger.info(f"{len(matches)} maç ile model eğitiliyor...")
        X = []
        y = []

        for match in matches:
            if (
                match.status != "Finished"
                or match.home_goals is None
                or match.away_goals is None
            ):
                continue

            # Prepare features
            try:
                features = self.prepare_match_data(
                    match.home_team_id, match.away_team_id, match.match_date
                )

                # Determine outcome (0: home win, 1: draw, 2: away win)
                if match.home_goals > match.away_goals:
                    outcome = 0
                elif match.home_goals == match.away_goals:
                    outcome = 1
                else:
                    outcome = 2

                X.append(features[0])  # Flatten the features
                y.append(outcome)

            except Exception as e:
                print(f"Error processing match {match.id}: {e}")

        if not X:
            logger.error("Eğitim için geçerli veri bulunamadı")
            return {
                "success": False,
                "message": "Eğitim için yeterli veri bulunamadı",
                "matches_used": 0,
            }

        try:
            # Veriyi numpy array'lerine dönüştür
            X = np.array(X)
            y = np.array(y)

            # Eğitim ve test verilerini ayır
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Veriyi ölçeklendir
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)

            # Modeli eğit
            logger.info("Model eğitimi başlıyor...")
            self.model.fit(X_train_scaled, y_train)

            # Modeli değerlendir
            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(X_test_scaled, y_test)

            # Tahminler
            y_pred = self.model.predict(X_test_scaled)

            # Hata metrikleri
            mae = np.mean(np.abs(y_test - y_pred))
            mse = np.mean((y_test - y_pred) ** 2)

            # Modeli kaydet
            self.save_model()

            logger.info(
                f"Model eğitimi tamamlandı. Eğitim skoru: {train_score:.4f}, Test skoru: {test_score:.4f}"
            )

            return {
                "success": True,
                "matches_used": len(X),
                "train_score": float(train_score),
                "test_score": float(test_score),
                "mae": float(mae),
                "mse": float(mse),
                "model_path": os.path.abspath(self.model_path),
                "league_id": self.league_id,
                "training_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

        except Exception as e:
            error_msg = f"Model eğitilirken hata oluştu: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"success": False, "message": error_msg, "error_details": str(e)}
