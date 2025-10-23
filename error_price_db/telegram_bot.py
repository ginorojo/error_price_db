# telegram_bot.py
import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def send_message(text):
    if TELEGRAM_TOKEN.startswith("TU_"):
        print("No configuraste TELEGRAM_TOKEN en config.py o en env vars")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        r = requests.post(url, data=data, timeout=10)
        if r.status_code != 200:
            print("Error al enviar Telegram:", r.text)
    except Exception as e:
        print("Error enviando Telegram:", e)
