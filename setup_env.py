# .env dosyasını oluşturan script
import os


def create_env_file():
    env_content = """# RapidAPI Ayarları
RAPIDAPI_KEY=ef1e9c7fc7mshb709e907a28f815p104103jsn59c8416e3231
RAPIDAPI_HOST=api-football-v1.p.rapidapi.com
RAPIDAPI_BASE_URL=https://api-football-v1.p.rapidapi.com/v3
"""
    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        print(".env dosyası başarıyla oluşturuldu!")
        return True
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
        return False


if __name__ == "__main__":
    if os.path.exists(".env"):
        print(".env dosyası zaten mevcut.")
        user_input = input("Üzerine yazılsın mı? (e/h): ")
        if user_input.lower() == "e":
            create_env_file()
    else:
        create_env_file()

    # Test çalıştır
    if os.path.exists("test_connection.py"):
        print("\nTest çalıştırılıyor...")
        os.system("python test_connection.py")
