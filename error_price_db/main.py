# main.py
from crawler import crawl_site, SITES
from scraper import get_price
from db import init_db, get_product, upsert_price
from telegram_bot import send_message
from config import ANOMALY_FACTOR, RATE_LIMIT_SECONDS
import time

def is_anomaly(url, price):
    row = get_product(url)
    if not row:
        return False  # sin histórico no se detecta
    count = row['count_seen'] or 0
    sum_prices = float(row['sum_prices'] or 0)
    if count == 0:
        return False
    avg = sum_prices / count
    # si price <= avg * ANOMALY_FACTOR => caída mayor al (1-ANOMALY_FACTOR)*100%
    return price <= avg * ANOMALY_FACTOR, avg

def process_site(start_url):
    print("Crawling:", start_url)
    urls = crawl_site(start_url)
    print("Encontrados productos:", len(urls))
    for i, url in enumerate(urls):
        print(f"[{i+1}/{len(urls)}] Scraping:", url)
        price = get_price(url)
        if price is None:
            print("No se pudo leer precio")
            continue
        anomaly, avg = is_anomaly(url, price)
        if anomaly:
            msg = f"⚠️ Posible error de precio\n{url}\nPrecio actual: {price}\nPrecio promedio: {avg:.2f}"
            print("ALERTA:", msg)
            send_message(msg)
        # actualizar DB
        upsert_price(url, price)
        time.sleep(RATE_LIMIT_SECONDS)

def main():
    init_db()
    for site in SITES:
        process_site(site)

if __name__ == "__main__":
    main()
