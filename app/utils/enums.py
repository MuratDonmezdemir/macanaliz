from enum import Enum, auto

class MatchStatus(Enum):
    SCHEDULED = 'SCHEDULED'
    LIVE = 'LIVE'
    IN_PLAY = 'IN_PLAY'
    PAUSED = 'PAUSED'
    FINISHED = 'FINISHED'
    POSTPONED = 'POSTPONED'
    SUSPENDED = 'SUSPENDED'
    CANCELED = 'CANCELED'
    AWARDED = 'AWARDED'

class MatchEventType(Enum):
    GOAL = 'GOAL'
    CARD = 'CARD'
    SUBSTITUTION = 'SUBSTITUTION'
    VAR = 'VAR'
    PENALTY_SHOOTOUT = 'PENALTY_SHOOTOUT'
    PENALTY_SHOOTOUT_MISS = 'PENALTY_SHOOTOUT_MISS'
    PENALTY_SHOOTOUT_GOAL = 'PENALTY_SHOOTOUT_GOAL'

class CardType(Enum):
    YELLOW = 'YELLOW'
    YELLOW_RED = 'YELLOW_RED'  # 2. sarı kart
    RED = 'RED'

class WeatherCondition(Enum):
    CLEAR = 'CLEAR'
    RAIN = 'RAIN'
    SNOW = 'SNOW'
    FOG = 'FOG'
    WINDY = 'WINDY'
    STORM = 'STORM'
    CLOUDY = 'CLOUDY'
    UNKNOWN = 'UNKNOWN'

class TeamFormation(Enum):
    FORMATION_442 = '4-4-2'
    FORMATION_433 = '4-3-3'
    FORMATION_352 = '3-5-2'
    FORMATION_343 = '3-4-3'
    FORMATION_4231 = '4-2-3-1'
    FORMATION_532 = '5-3-2'
    FORMATION_541 = '5-4-1'

class TeamStatus(Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    BANNED = 'BANNED'

class TeamType(Enum):
    CLUB = 'CLUB'
    NATIONAL = 'NATIONAL'

class TeamGender(Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    MIXED = 'MIXED'
