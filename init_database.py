#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Veritabanı başlatma ve örnek veri yükleme betiği.
"""
import os
import sys
from datetime import datetime, timedelta

# Proje kök dizinini Python yoluna ekle
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def init_database():
    from app import create_app, db
    from app.models import (
        User, Team, League, Season, Stadium, Player,
        Match, MatchEvent, MatchGoal, MatchCard, 
        MatchSubstitution, MatchLineup, MatchStatistics,
        TeamStatistics, PlayerStatistics, PlayerInjury, 
        PlayerTransfer, Standing, Referee, Race, Equipment
    )
    
    # Uygulama bağlamını oluştur
    app = create_app()
    
    with app.app_context():
        # Veritabanını oluştur
        print("Veritabanı tabloları oluşturuluyor...")
        db.create_all()
        
        # Örnek verileri yükle
        print("Örnek veriler yükleniyor...")
        load_sample_data()
        
        print("✅ Veritabanı başarıyla başlatıldı!")

def load_sample_data():
    from app.models import db, User, Team, League, Season, Stadium
    from app.models.enums import TeamStatus, TeamType, TeamGender
    
    # Örnek kullanıcı ekle
    if not User.query.first():
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True,
            is_active=True,
            email_verified=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin kullanıcısı oluşturuldu.")
    
    # Örnek sezon ekle
    current_year = datetime.now().year
    if not Season.query.first():
        season = Season(
            name=f'{current_year-1}-{current_year}',
            start_date=datetime(current_year-1, 8, 1),
            end_date=datetime(current_year, 5, 31),
            is_current=True
        )
        db.session.add(season)
        db.session.commit()
        print("✅ Örnek sezon eklendi.")
    
    # Örnek ligler ekle
    if not League.query.first():
        season = Season.query.first()
        
        premier_league = League(
            name='Premier League',
            country='İngiltere',
            code='PL',
            logo_url='https://example.com/pl.png',
            season_id=season.id
        )
        db.session.add(premier_league)
        
        super_lig = League(
            name='Süper Lig',
            country='Türkiye',
            code='SL',
            logo_url='https://example.com/sl.png',
            season_id=season.id
        )
        db.session.add(super_lig)
        db.session.commit()
        print("✅ Örnek ligler eklendi.")
    
    # Örnek stadyum ekle
    if not Stadium.query.first():
        stadiums = [
            {
                'name': 'Vodafone Park',
                'city': 'İstanbul',
                'country': 'Türkiye',
                'capacity': 41000,
                'built_year': 2016,
                'address': 'Dolmabahçe, Vişnezade, 34357 Beşiktaş/İstanbul'
            },
            {
                'name': 'Rams Park',
                'city': 'İstanbul',
                'country': 'Türkiye',
                'capacity': 52000,
                'built_year': 2011,
                'address': 'Huzur, Şişli/İstanbul'
            },
            {
                'name': 'Ülker Stadyumu',
                'city': 'İstanbul',
                'country': 'Türkiye',
                'capacity': 50000,
                'built_year': 1907,
                'address': 'Kızıltoprak, Fenerbahçe Şükrü Saracoğlu Stadyumu, 34724 Kadıköy/İstanbul'
            }
        ]
        
        for stadium_data in stadiums:
            stadium = Stadium(**stadium_data)
            db.session.add(stadium)
        
        db.session.commit()
        print("✅ Örnek stadyumlar eklendi.")
    
    # Örnek takımlar ekle
    if not Team.query.first():
        stadiums = Stadium.query.all()
        league = League.query.filter_by(code='SL').first()
        
        teams = [
            {
                'name': 'Beşiktaş JK', 
                'short_name': 'BJK', 
                'founded': 1903, 
                'stadium_id': stadiums[0].id if stadiums else None,
                'logo_url': 'https://example.com/bjk.png',
                'status': TeamStatus.ACTIVE.value,
                'type': TeamType.CLUB.value,
                'gender': TeamGender.MALE.value,
                'colors': ['black', 'white']
            },
            {
                'name': 'Galatasaray SK', 
                'short_name': 'GS', 
                'founded': 1905, 
                'stadium_id': stadiums[1].id if len(stadiums) > 1 else None,
                'logo_url': 'https://example.com/gs.png',
                'status': TeamStatus.ACTIVE.value,
                'type': TeamType.CLUB.value,
                'gender': TeamGender.MALE.value,
                'colors': ['red', 'yellow']
            },
            {
                'name': 'Fenerbahçe SK', 
                'short_name': 'FB', 
                'founded': 1907, 
                'stadium_id': stadiums[2].id if len(stadiums) > 2 else None,
                'logo_url': 'https://example.com/fb.png',
                'status': TeamStatus.ACTIVE.value,
                'type': TeamType.CLUB.value,
                'gender': TeamGender.MALE.value,
                'colors': ['blue', 'yellow']
            }
        ]
        
        for team_data in teams:
            team = Team(**team_data)
            if league:
                team.leagues.append(league)
            db.session.add(team)
        
        db.session.commit()
        print("✅ Örnek takımlar eklendi.")

if __name__ == '__main__':
    init_database()
