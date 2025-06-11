import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import logging
from functools import wraps

# Loglama ayarı
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_errors(func):
    """Hata yönetimi için dekoratör."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"{func.__name__} fonksiyonunda hata oluştu: {str(e)}")
            if func.__name__ == 'preprocess_matches':
                return pd.DataFrame()
            elif func.__name__ == 'calculate_team_form':
                return {'form': 0.0, 'goals_scored': 0.0, 'goals_conceded': 0.0, 'clean_sheets': 0.0}
            else:
                return {}
    return wrapper

class DataProcessor:
    """
    Futbol maç verilerini işleyerek makine öğrenmesi modelleri için uygun hale getirir.
    
    Bu sınıf, ham maç verilerini alıp işleyerek, tahmin modellerinde kullanılabilecek
    özelliklerin çıkarılmasını sağlar. Ayrıca takım formu hesaplama ve maç analizi
    gibi işlemleri gerçekleştirir.
    """

    @staticmethod
    @handle_errors
    def preprocess_matches(matches: List[Dict]) -> pd.DataFrame:
        """Ham maç verilerini ön işlemeden geçirir.
        
        Args:
            matches (List[Dict]): İşlenecek maç verileri listesi. Her sözlük bir maçı temsil eder.
                Örnek: [{'home_team': 'Takım A', 'away_team': 'Takım B', 'home_goals': 2, ...}]
                
        Returns:
            pd.DataFrame: İşlenmiş veri çerçevesi. Aşağıdaki sütunları içerir:
                - match_date: Maç tarihi (datetime)
                - home_win: Ev sahibi kazanırsa 1, değilse 0
                - draw: Beraberlikse 1, değilse 0
                - away_win: Deplasman kazanırsa 1, değilse 0
                - goal_difference: Gol farkı (ev - deplasman)
                - total_goals: Toplam gol sayısı
                - day_of_week: Haftanın günü (0: Pazartesi, 6: Pazar)
                - month: Ay (1-12)
        """
        if not matches:
            logger.warning("Boş maç listesi alındı.")
            return pd.DataFrame()
            
        try:
            df = pd.DataFrame(matches)
            
            # Zorunlu sütunları kontrol et
            required_columns = ['date', 'home_team', 'away_team', 'home_goals', 'away_goals']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"Gerekli sütun eksik: {col}")
            
            # Temel özellikler
            df['match_date'] = pd.to_datetime(df['date'], errors='coerce')
            df['home_win'] = (df['home_goals'] > df['away_goals']).astype(int)
            df['draw'] = (df['home_goals'] == df['away_goals']).astype(int)
            df['away_win'] = (df['home_goals'] < df['away_goals']).astype(int)
            
            # Gol farkı ve toplam gol
            df['goal_difference'] = df['home_goals'] - df['away_goals']
            df['total_goals'] = df['home_goals'] + df['away_goals']
            
            # Zaman bazlı özellikler
            df['day_of_week'] = df['match_date'].dt.dayofweek
            df['month'] = df['match_date'].dt.month
            
            # Eksik değer kontrolü
            if df.isnull().values.any():
                logger.warning("Eksik değerler tespit edildi. Dolduruluyor...")
                df = df.fillna(0)
                
            logger.info(f"{len(df)} maç başarıyla işlendi.")
            return df
            
        except Exception as e:
            logger.error(f"Maç verileri işlenirken hata oluştu: {str(e)}")
            return pd.DataFrame()
        if not matches:
            return pd.DataFrame()
            
        df = pd.DataFrame(matches)
        
        # Temel özellikler
        df['match_date'] = pd.to_datetime(df['date'])
        df['home_win'] = (df['home_goals'] > df['away_goals']).astype(int)
        df['draw'] = (df['home_goals'] == df['away_goals']).astype(int)
        df['away_win'] = (df['home_goals'] < df['away_goals']).astype(int)
        
        # Gol farkı ve toplam gol
        df['goal_difference'] = df['home_goals'] - df['away_goals']
        df['total_goals'] = df['home_goals'] + df['away_goals']
        
        # Zaman bazlı özellikler
        df['day_of_week'] = df['match_date'].dt.dayofweek
        df['month'] = df['match_date'].dt.month
        
        return df

    @staticmethod
    @handle_errors
    def calculate_team_form(team_matches: pd.DataFrame, num_matches: int = 5) -> Dict[str, float]:
        """Takımın son maçlardaki formunu ve performans istatistiklerini hesaplar.
        
        Args:
            team_matches (pd.DataFrame): Takımın maç verilerini içeren DataFrame.
                Gerekli sütunlar: 'match_date', 'home_team', 'away_team', 'home_goals', 'away_goals'
            num_matches (int, optional): Değerlendirilecek son maç sayısı. Varsayılan: 5
                
        Returns:
            Dict[str, float]: Takımın form ve performans istatistikleri:
                - form: Ortalama puan (Maks 3.0)
                - goals_scored: Maç başına atılan ortalama gol
                - goals_conceded: Maç başına yenen ortalama gol
                - clean_sheets: Temiz kale yüzdesi
                - win_rate: Kazanma yüzdesi
                - draw_rate: Beraberlik yüzdesi
                - loss_rate: Mağlubiyet yüzdesi
        """
        default_stats = {
            'form': 0.0,
            'goals_scored': 0.0,
            'goals_conceded': 0.0,
            'clean_sheets': 0.0,
            'win_rate': 0.0,
            'draw_rate': 0.0,
            'loss_rate': 0.0
        }
        
        try:
            # Giriş doğrulama
            if team_matches is None or team_matches.empty:
                logger.warning("Boş veya geçersiz takım maç verisi alındı.")
                return default_stats
                
            # Gerekli sütunları kontrol et
            required_columns = ['match_date', 'home_team', 'away_team', 'home_goals', 'away_goals']
            if not all(col in team_matches.columns for col in required_columns):
                raise ValueError("Eksik sütunlar var. Gerekli sütunlar: " + ", ".join(required_columns))
            
            # Son maçları al ve sırala
            team_matches = team_matches.sort_values('match_date', ascending=False)
            last_matches = team_matches.head(num_matches)
            
            if last_matches.empty:
                return default_stats
                
            # İstatistikleri hesapla
            form_points = []
            goals_scored = []
            goals_conceded = []
            clean_sheets = []
            results = []  # 0: mağlubiyet, 1: beraberlik, 2: galibiyet
            
            for _, match in last_matches.iterrows():
                is_home = match['home_team'] == match.get('team_name', '')
                
                if is_home:
                    team_goals = match['home_goals']
                    opponent_goals = match['away_goals']
                else:
                    team_goals = match['away_goals']
                    opponent_goals = match['home_goals']
                
                # Skor durumuna göre puan ve sonuç
                if team_goals > opponent_goals:
                    form_points.append(3)  # Galibiyet
                    results.append(2)
                elif team_goals == opponent_goals:
                    form_points.append(1)  # Beraberlik
                    results.append(1)
                else:
                    form_points.append(0)  # Mağlubiyet
                    results.append(0)
                
                # İstatistikler
                goals_scored.append(team_goals)
                goals_conceded.append(opponent_goals)
                clean_sheets.append(1 if opponent_goals == 0 else 0)
            
            # Sonuçları hesapla
            total_matches = len(last_matches)
            if total_matches == 0:
                return default_stats
                
            # Form ve istatistikler
            avg_form = sum(form_points) / total_matches
            avg_goals_scored = sum(goals_scored) / total_matches
            avg_goals_conceded = sum(goals_conceded) / total_matches
            clean_sheet_ratio = sum(clean_sheets) / total_matches
            
            # Sonuç yüzdeleri
            win_rate = results.count(2) / total_matches
            draw_rate = results.count(1) / total_matches
            loss_rate = results.count(0) / total_matches
            
            logger.info(f"Takım formu hesaplandı: {avg_form:.2f} puan (Son {total_matches} maç)")
            
            return {
                'form': round(avg_form, 2),
                'goals_scored': round(avg_goals_scored, 2),
                'goals_conceded': round(avg_goals_conceded, 2),
                'clean_sheets': round(clean_sheet_ratio, 2),
                'win_rate': round(win_rate, 2),
                'draw_rate': round(draw_rate, 2),
                'loss_rate': round(loss_rate, 2)
            }
            
        except Exception as e:
            logger.error(f"Takım formu hesaplanırken hata oluştu: {str(e)}")
            return default_stats

    @staticmethod
    @handle_errors
    def prepare_prediction_data(home_team_stats: Dict, away_team_stats: Dict, 
                              home_team_id: Optional[str] = None, 
                              away_team_id: Optional[str] = None) -> Dict[str, Any]:
        """Tahmin modelleri için gerekli özellikleri hazırlar.
        
        Bu fonksiyon, ev sahibi ve deplasman takımlarının istatistiklerini alarak
        makine öğrenmesi modellerinde kullanılabilecek özellikler oluşturur.
        
        Args:
            home_team_stats (Dict): Ev sahibi takımın istatistikleri
            away_team_stats (Dict): Deplasman takımının istatistikleri
            home_team_id (str, optional): Ev sahibi takım ID'si
            away_team_id (str, optional): Deplasman takım ID'si
                
        Returns:
            Dict[str, Any]: Tahmin için hazırlanmış özellikler sözlüğü
                
        Örnek Çıktı:
            {
                'home_form': 2.1,
                'home_goals_scored_avg': 1.8,
                'home_goals_conceded_avg': 0.7,
                'home_clean_sheets': 0.6,
                'home_win_rate': 0.7,
                'home_draw_rate': 0.2,
                'home_loss_rate': 0.1,
                'away_form': 1.4,
                'away_goals_scored_avg': 1.2,
                'away_goals_conceded_avg': 1.1,
                'away_clean_sheets': 0.3,
                'away_win_rate': 0.4,
                'away_draw_rate': 0.3,
                'away_loss_rate': 0.3,
                'form_difference': 0.7,
                'goal_difference': 0.8,
                'attack_strength': 0.4,
                'defense_strength': -0.2,
                'home_team_id': '123',
                'away_team_id': '456'
            }
        """
        try:
            # Varsayılan değerler
            default_stats = {
                'form': 0.0,
                'goals_scored': 0.0,
                'goals_conceded': 0.0,
                'clean_sheets': 0.0,
                'win_rate': 0.0,
                'draw_rate': 0.0,
                'loss_rate': 0.0
            }
            
            # None kontrolü
            home_team_stats = home_team_stats or default_stats
            away_team_stats = away_team_stats or default_stats
            
            # Temel özellikler
            features = {
                # Ev sahibi takım istatistikleri
                'home_form': home_team_stats.get('form', 0.0),
                'home_goals_scored_avg': home_team_stats.get('goals_scored', 0.0),
                'home_goals_conceded_avg': home_team_stats.get('goals_conceded', 0.0),
                'home_clean_sheets': home_team_stats.get('clean_sheets', 0.0),
                'home_win_rate': home_team_stats.get('win_rate', 0.0),
                'home_draw_rate': home_team_stats.get('draw_rate', 0.0),
                'home_loss_rate': home_team_stats.get('loss_rate', 0.0),
                
                # Deplasman takımı istatistikleri
                'away_form': away_team_stats.get('form', 0.0),
                'away_goals_scored_avg': away_team_stats.get('goals_scored', 0.0),
                'away_goals_conceded_avg': away_team_stats.get('goals_conceded', 0.0),
                'away_clean_sheets': away_team_stats.get('clean_sheets', 0.0),
                'away_win_rate': away_team_stats.get('win_rate', 0.0),
                'away_draw_rate': away_team_stats.get('draw_rate', 0.0),
                'away_loss_rate': away_team_stats.get('loss_rate', 0.0),
            }
            
            # Karşılaştırmalı istatistikler
            features.update({
                'form_difference': features['home_form'] - features['away_form'],
                'goal_difference': (features['home_goals_scored_avg'] - features['home_goals_conceded_avg']) - \
                                 (features['away_goals_scored_avg'] - features['away_goals_conceded_avg']),
                'attack_strength': features['home_goals_scored_avg'] - features['away_goals_conceded_avg'],
                'defense_strength': features['home_goals_conceded_avg'] - features['away_goals_scored_avg']
            })
            
            # Takım ID'lerini ekle
            if home_team_id:
                features['home_team_id'] = home_team_id
            if away_team_id:
                features['away_team_id'] = away_team_id
            
            # Değerleri yuvarla
            features = {k: round(float(v), 4) for k, v in features.items()}
            
            logger.info("Tahmin için özellikler başarıyla oluşturuldu.")
            return features
            
        except Exception as e:
            logger.error(f"Tahmin verileri hazırlanırken hata oluştu: {str(e)}")
            return {}
            
    @staticmethod
    def get_team_form(team_id: str, matches: List[Dict], is_home: bool = True, 
                     num_matches: int = 5) -> Dict[str, float]:
        """Belirtilen takımın formunu hesaplar.
        
        Args:
            team_id (str): Takım ID'si
            matches (List[Dict]): Tüm maçların listesi
            is_home (bool, optional): Ev sahibi mi yoksa deplasman mı? Varsayılan: True (Ev sahibi)
            num_matches (int, optional): Değerlendirilecek maç sayısı. Varsayılan: 5
            
        Returns:
            Dict[str, float]: Takım form istatistikleri
        """
        try:
            if not matches:
                logger.warning("Maç listesi boş.")
                return {}
                
            # Takımın maçlarını filtrele
            team_matches = []
            for match in matches:
                if is_home and match.get('home_team_id') == team_id:
                    team_matches.append({
                        'match_date': match.get('date'),
                        'home_team': match.get('home_team'),
                        'away_team': match.get('away_team'),
                        'home_goals': match.get('home_goals', 0),
                        'away_goals': match.get('away_goals', 0),
                        'team_name': match.get('home_team')
                    })
                elif not is_home and match.get('away_team_id') == team_id:
                    team_matches.append({
                        'match_date': match.get('date'),
                        'home_team': match.get('home_team'),
                        'away_team': match.get('away_team'),
                        'home_goals': match.get('home_goals', 0),
                        'away_goals': match.get('away_goals', 0),
                        'team_name': match.get('away_team')
                    })
            
            df = pd.DataFrame(team_matches)
            if df.empty:
                logger.warning(f"{team_id} ID'li takım için maç bulunamadı.")
                return {}
                
            # Form hesapla
            return DataProcessor.calculate_team_form(df, num_matches)
            
        except Exception as e:
            logger.error(f"Takım formu hesaplanırken hata oluştu: {str(e)}")
            return {}
