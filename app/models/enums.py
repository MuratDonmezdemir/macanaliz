"""Uygulama genelinde kullanılan enum'ların tanımlandığı modül."""
from enum import Enum

class PlayerPosition(str, Enum):
    """Oyuncu mevki enum'ları"""
    GOALKEEPER = 'GK'  # Kaleci
    DEFENDER = 'DEF'   # Defans
    MIDFIELDER = 'MID' # Orta saha
    FORWARD = 'FWD'    # Forvet

class PlayerStatus(str, Enum):
    """Oyuncu durum enum'ları"""
    ACTIVE = 'active'      # Aktif
    INJURED = 'injured'    # Sakat
    SUSPENDED = 'suspended' # Cezalı
    LOANED = 'loaned'      # Kiralık
    TRANSFERRED = 'transferred' # Transfer oldu
    RETIRED = 'retired'    # Emekli

class PlayerFoot(str, Enum):
    """Oyuncu ayak tercihi enum'ları"""
    RIGHT = 'right'  # Sağ ayak
    LEFT = 'left'    # Sol ayak
    BOTH = 'both'    # İki ayaklı

class CardType(str, Enum):
    """Kart türleri"""
    YELLOW = 'yellow'      # Sarı kart
    RED = 'red'           # Kırmızı kart
    YELLOW_RED = 'yellow_red' # İkinci sarıdan kırmızı

class MatchStatus(str, Enum):
    """Maç durumları"""
    SCHEDULED = 'scheduled'  # Planlandı
    TIMED = 'timed'          # Zamanı belli
    IN_PLAY = 'in_play'      # Oynanıyor
    PAUSED = 'paused'        # Devre arası
    FINISHED = 'finished'    # Tamamlandı
    SUSPENDED = 'suspended'  # Durduruldu
    POSTPONED = 'postponed'  # Ertelendi
    CANCELLED = 'cancelled'  # İptal edildi
    AWARDED = 'awarded'      # Hükmen

class InjuryStatus(str, Enum):
    """Sakatlık durumları"""
    ACTIVE = 'active'          # Aktif sakatlık
    RECOVERED = 'recovered'    # İyileşti
    RECOVERING = 'recovering'  # İyileşiyor
    RELAPSE = 'relapse'        # Tekrarlama
    CHRONIC = 'chronic'        # Kronik

class InjuryType(str, Enum):
    """Sakatlık türleri"""
    MUSCLE = 'muscle'              # Kas sakatlığı
    LIGAMENT = 'ligament'          # Bağ sakatlığı
    FRACTURE = 'fracture'          # Kırık
    DISLOCATION = 'dislocation'    # Çıkık
    CONTUSION = 'contusion'        # Ezilme
    TENDON = 'tendon'              # Tendon
    KNEE = 'knee'                  # Diz
    ANKLE = 'ankle'                # Ayak bileği
    HAMSTRING = 'hamstring'        # Arka uyluk
    GROIN = 'groin'                # Kasık
    BACK = 'back'                  # Sırt
    CONCUSSION = 'concussion'      # Sarsıntı
    ILLNESS = 'illness'            # Hastalık
    OTHER = 'other'                # Diğer

class TransferType(str, Enum):
    """Transfer türleri"""
    PERMANENT = 'permanent'    # Kalıcı transfer
    LOAN = 'loan'              # Kiralık
    LOAN_WITH_OPTION = 'loan_with_option'  # Satın alma opsiyonlu kiralık
    LOAN_WITH_OBLIGATION = 'loan_with_obligation'  # Zorunlu satın alma şartlı kiralık
    FREE = 'free'               # Bedelsiz
    END_OF_LOAN = 'end_of_loan' # Kiralık süresi bitimi
    END_OF_CONTRACT = 'end_of_contract'  # Sözleşme bitimi
    RETIREMENT = 'retirement'   # Futbolu bırakma

class TransferStatus(str, Enum):
    """Transfer durumları"""
    RUMOR = 'rumor'             # Söylenti
    CONFIRMED = 'confirmed'      # Onaylandı
    COMPLETED = 'completed'      # Tamamlandı
    FAILED = 'failed'           # Başarısız oldu
    LOAN_END = 'loan_end'       # Kiralık süresi bitti
    LOAN_RETURN = 'loan_return' # Kiralık dönüşü
