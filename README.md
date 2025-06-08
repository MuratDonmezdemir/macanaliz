# MacAnaliz

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Futbol maç analiz ve tahmin uygulaması. Bu uygulama, futbol maçları hakkında detaylı analizler sunar ve maç sonuçları için tahminlerde bulunur.

## Özellikler

- Kapsamlı futbol maç analizleri
- Tahmin motoru ile maç sonuçları tahmini
- Takım ve oyuncu istatistikleri
- Lige özel analizler
- API desteği

## Kurulum

1. Gereksinimler:
   - Python 3.8 veya üzeri
   - pip (Python paket yöneticisi)

2. Depoyu klonlayın:
   ```bash
   git clone https://github.com/kullaniciadi/macanaliz.git
   cd macanaliz
   ```

3. Sanal ortam oluşturma (önerilir):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

4. Gerekli paketlerin yüklenmesi:
   ```bash
   pip install -r requirements.txt
   ```

5. Geliştirme için ek paketler (isteğe bağlı):
   ```bash
   pip install -r requirements-dev.txt
   ```

6. Ortam değişkenlerinin ayarlanması:
   - `.env.example` dosyasını `.env` olarak kopyalayın
   - Gerekli değişkenleri düzenleyin

## Veritabanı

Uygulama SQLite kullanmaktadır (geliştirme ortamı için). Veritabanını başlatmak için:

```bash
flask db upgrade
```

## Çalıştırma

Geliştirme sunucusunu başlatmak için:

```bash
flask run
```

Veya production modunda çalıştırmak için:

```bash
gunicorn -w 4 'app:create_app()'
```

## API Dokümantasyonu

API dokümantasyonuna şu adresten ulaşabilirsiniz: `http://localhost:5000/api/docs`

## Proje Yapısı

```
.
├── app/                   # Ana uygulama klasörü
│   ├── __init__.py       # Uygulama fabrikası
│   ├── models/           # Veritabanı modelleri
│   ├── routes/           # Rotalar
│   ├── services/         # İş mantığı
│   ├── static/           # Statik dosyalar (CSS, JS, resimler)
│   └── templates/        # Şablonlar
├── migrations/           # Veritabanı migrasyonları
├── tests/               # Testler
├── .env                 # Ortam değişkenleri
├── .gitignore
├── config.py            # Yapılandırma ayarları
├── requirements.txt     # Bağımlılıklar
├── requirements-dev.txt # Geliştirme bağımlılıkları
└── README.md           # Bu dosya
```

## Test

Testleri çalıştırmak için:

```bash
pytest
```

## Makine Öğrenmesi Modelleri

Sistem farklı tahmin görevleri için çeşitli makine öğrenmesi modelleri kullanır:

1. **Maç Sonucu Tahmini**: XGBoost sınıflandırıcı
2. **İlk Yarı Sonucu**: LightGBM sınıflandırıcı
3. **Gol Sayısı Tahmini**: CatBoost regresyon
4. **İki Takım da Gol Atar Mı?**: Random Forest sınıflandırıcı
5. **Alt/Üst Tahmini**: Gradient Boosting sınıflandırıcı

## Katkıda Bulunma

1. Bu repoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/YeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inize push yapın (`git push origin feature/YeniOzellik`)
5. Bir Pull Request açın

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır - detaylar için `LICENSE` dosyasına bakınız.

## İletişim

Proje Yöneticisi: [İsminiz] - [email@example.com](mailto:email@example.com)

Proje Linki: [https://github.com/kullaniciadi/macanaliz](https://github.com/kullaniciadi/macanaliz)
5. Open a Pull Request

## Acknowledgments

- Thanks to all open-source projects that made this possible
- Data providers and football statistics APIs
- Machine learning community for their valuable resources