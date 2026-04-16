import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")

# Настройки проверки
CHECK_ATTEMPTS = 2
CHECK_INTERVAL_FIRST = 7
CHECK_INTERVAL_SECOND = 8