from flask import Flask, request, render_template_string
from crawler import crawl_site
from scraper import get_price
from db import init_db, get_product, upsert_price, add_link, get_all_links, log_scrape, get_scrape_history
from telegram_bot import send_message
from config import ANOMALY_FACTOR, RATE_LIMIT_SECONDS
import time
import threading
import os

app = Flask(__name__)

def is_anomaly(url, price):
    row = get_product(url)
    if not row:
        return False
    count = row['count_seen'] or 0
    sum_prices = float(row['sum_prices'] or 0)
    if count == 0:
        return False
    avg = sum_prices / count
    return price <= avg * ANOMALY_FACTOR, avg

def process_link(url):
    print("Crawling:", url)
    product_urls = crawl_site(url)
    print(f"Productos encontrados: {len(product_urls)}")
    for i, p_url in enumerate(product_urls):
        try:
            price = get_price(p_url)
        except:
            continue
        if price is None:
            continue
        anomaly, avg = is_anomaly(p_url, price)
        if anomaly:
            msg = f"⚠️ Error de precio\n{p_url}\nPrecio actual: {price}\nPromedio: {avg:.2f}"
            print(msg)
            send_message(msg)
        upsert_price(p_url, price)
        time.sleep(RATE_LIMIT_SECONDS)
    # Registrar historial
    log_scrape(url, len(product_urls))

def run_scraping_loop():
    while True:
        all_links = get_all_links()
        for link in all_links:
            process_link(link)
        time.sleep(300)  # revisar cada 5 minutos

# Hilo de scraping
threading.Thread(target=run_scraping_loop, daemon=True).start()

# Rutas web
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        new_link = request.form.get("url")
        if new_link:
            add_link(new_link)
    links = get_all_links()
    history = get_scrape_history()
    return render_template_string("""
    <h1>Scraping de Precios</h1>
    <form method="post">
        <input type="text" name="url" placeholder="Agregar link a revisar">
        <button type="submit">Agregar</button>
    </form>
    <h2>Links actuales</h2>
    <ul>
        {% for l in links %}
            <li>{{ l }}</li>
        {% endfor %}
    </ul>
    <h2>Historial reciente</h2>
    <table border="1">
        <tr><th>Link</th><th>Productos revisados</th><th>Fecha</th></tr>
        {% for h in history %}
            <tr><td>{{ h.url }}</td><td>{{ h.product_count }}</td><td>{{ h.checked_at }}</td></tr>
        {% endfor %}
    </table>
    """, links=links, history=history)

if __name__ == "__main__":
    init_db()
    send_message("🚀 Scraping iniciado en Render")
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
