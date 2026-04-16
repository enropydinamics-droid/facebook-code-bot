import os
print("--- Environment variables debug ---")
# Проверяем наличие только самых важных переменных
print(f"TELEGRAM_TOKEN exists: {bool(os.getenv('TELEGRAM_TOKEN'))}")
print(f"RAPIDAPI_KEY exists: {bool(os.getenv('RAPIDAPI_KEY'))}")
print(f"RAPIDAPI_HOST exists: {bool(os.getenv('RAPIDAPI_HOST'))}")
print("-----------------------------------")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")

# Настройки проверки
CHECK_ATTEMPTS = 2
CHECK_INTERVAL_FIRST = 7
CHECK_INTERVAL_SECOND = 8