# main.py adaptado para Render Free con Flask y mensaje de inicio
from flask import Flask
from crawler import crawl_site, SITES
from scraper import get_price
from db import init_db, get_product, upsert_price
from telegram_bot import send_message
from config import ANOMALY_FACTOR, RATE_LIMIT_SECONDS
import time
import threading
import os

app = Flask(__name__)

def is_anomaly(url, price):
    row = get_product(url)
    if not row:
        return False  # sin histórico no se detecta
    count = row['count_seen'] or 0
    sum_prices = float(row['sum_prices'] or 0)
    if count == 0:
        return False
    avg = sum_prices / count
    return price <= avg * ANOMALY_FACTOR, avg

def process_site(start_url):
    print("Crawling:", start_url)
    urls = crawl_site(start_url)
    print("Encontrados productos:", len(urls))
    for i, url in enumerate(urls):
        print(f"[{i+1}/{len(urls)}] Scraping:", url)
        try:
            price = get_price(url)
        except Exception as e:
            print(f"Error al acceder a {url}: {e}")
            continue
        if price is None:
            print("No se pudo leer precio")
            continue
        anomaly, avg = is_anomaly(url, price)
        if anomaly:
            msg = f"⚠️ Posible error de precio\n{url}\nPrecio actual: {price}\nPrecio promedio: {avg:.2f}"
            print("ALERTA:", msg)
            send_message(msg)
        upsert_price(url, price)
        time.sleep(RATE_LIMIT_SECONDS)

def run_script():
    init_db()
    # Mensaje que se envía cada vez que se inicia todo
    send_message("🚀 El scraping de precios se ha iniciado en Render!")
    
    for site in SITES:
        process_site(site)

# Ejecutar el script en un hilo separado para que Flask pueda iniciar
threading.Thread(target=run_script).start()

@app.route("/")
def home():
    return "Script ejecutándose en Render!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render asigna el puerto dinámicamente
    app.run(host="0.0.0.0", port=port)
