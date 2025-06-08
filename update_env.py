import os
import secrets
from pathlib import Path


def update_env():
    # .env dosyasının yolunu belirle
    env_path = Path('.') / '.env'

    # .env dosyası yoksa oluştur
    if not env_path.exists():
        with open(env_path, 'w') as f:
            pass

    # .env dosyasını oku
    lines = []
    with open(env_path, 'r') as f:
        lines = f.readlines()

    # Yeni bir güvenli SECRET_KEY oluştur
    new_secret_key = secrets.token_hex(32)
    secret_key_line = f"SECRET_KEY={new_secret_key}\n"

    # SECRET_KEY satırını güncelle veya ekle
    key_updated = False
    for i, line in enumerate(lines):
        if line.startswith('SECRET_KEY='):
            lines[i] = secret_key_line
            key_updated = True
            break

    if not key_updated:
        lines.append(secret_key_line)

    # Değişiklikleri kaydet
    with open(env_path, 'w') as f:
        f.writelines(lines)

    print(f"✅ .env dosyası güncellendi. Yeni SECRET_KEY: {new_secret_key}")


if __name__ == "__main__":
    update_env()