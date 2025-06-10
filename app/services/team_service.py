"""Takım işlemleri için servis katmanı."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.team import Team, TeamStatus
from app.models.league import League
from app.models.stadium import Stadium


class TeamService:
    """Takımla ilgili iş mantığını yöneten servis sınıfı."""
    
    def __init__(self, db_session: Session):
        """Yeni bir TeamService örneği oluşturur.
        
        Args:
            db_session: Veritabanı oturumu
        """
        self.db = db_session
    
    def create_team(self, team_data: Dict[str, Any]) -> Team:
        """Yeni bir takım oluşturur.
        
        Args:
            team_data: Takım bilgilerini içeren sözlük
            
        Returns:
            Oluşturulan takım nesnesi
            
        Raises:
            ValueError: Zorunlu alanlar eksikse veya geçersizse
        """
        # Zorunlu alanları kontrol et
        required_fields = ['name', 'short_name', 'code', 'country', 'city']
        for field in required_fields:
            if field not in team_data or not team_data[field]:
                raise ValueError(f"{field} alanı zorunludur")
        
        # Yeni takım oluştur
        team = Team(
            name=team_data['name'],
            short_name=team_data['short_name'],
            code=team_data['code'],
            country=team_data['country'],
            city=team_data['city'],
            founded=team_data.get('founded'),
            logo=team_data.get('logo'),
            status=TeamStatus.ACTIVE,
            team_type=team_data.get('team_type', 'CLUB'),
            gender=team_data.get('gender', 'MALE'),
            website=team_data.get('website'),
            email=team_data.get('email'),
            phone=team_data.get('phone')
        )
        
        # İlişkileri ayarla
        if 'league_id' in team_data:
            league = self.db.query(League).get(team_data['league_id'])
            if league:
                team.league = league
        
        if 'stadium_id' in team_data:
            stadium = self.db.query(Stadium).get(team_data['stadium_id'])
            if stadium:
                team.stadium = stadium
        
        # Veritabanına kaydet
        self.db.add(team)
        self.db.commit()
        
        return team
    
    def update_team(self, team_id: int, update_data: Dict[str, Any]) -> Optional[Team]:
        """Mevcut bir takımı günceller.
        
        Args:
            team_id: Güncellenecek takım ID'si
            update_data: Güncelleme verilerini içeren sözlük
            
        Returns:
            Güncellenmiş takım nesnesi veya None (bulunamazsa)
        """
        team = self.db.query(Team).get(team_id)
        if not team:
            return None
            
        # Temel alanları güncelle
        for key, value in update_data.items():
            if hasattr(team, key) and key != 'id':
                setattr(team, key, value)
                
        team.updated_at = datetime.utcnow()
        self.db.commit()
        
        return team
    
    def get_team_by_id(self, team_id: int) -> Optional[Team]:
        """ID'ye göre takım bilgilerini getirir.
        
        Args:
            team_id: Aranacak takım ID'si
            
        Returns:
            Takım nesnesi veya None (bulunamazsa)
        """
        return self.db.query(Team).get(team_id)
    
    def get_teams_by_country(self, country: str) -> List[Team]:
        """Ülkeye göre takımları listeler.
        
        Args:
            country: Ülke adı
            
        Returns:
            İlgili ülkedeki takımların listesi
        """
        return self.db.query(Team).filter(
            Team.country == country,
            Team.status == TeamStatus.ACTIVE
        ).order_by(Team.name).all()
    
    def delete_team(self, team_id: int) -> bool:
        """Bir takımı siler (soft delete).
        
        Args:
            team_id: Silinecek takım ID'si
            
        Returns:
            Başarılıysa True, aksi halde False
        """
        team = self.db.query(Team).get(team_id)
        if not team:
            return False
            
        team.status = TeamStatus.DELETED
        team.deleted_at = datetime.utcnow()
        self.db.commit()
        return True
