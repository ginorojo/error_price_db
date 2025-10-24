import psycopg2
from psycopg2.extras import RealDictCursor
from config import DATABASE_URL

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    # Tabla de precios históricos
    cur.execute("""
    CREATE TABLE IF NOT EXISTS product_prices (
        url TEXT PRIMARY KEY,
        last_price NUMERIC,
        count_seen INTEGER DEFAULT 0,
        sum_prices NUMERIC DEFAULT 0
    );
    """)
    # Tabla de links a revisar
    cur.execute("""
    CREATE TABLE IF NOT EXISTS links (
        url TEXT PRIMARY KEY
    );
    """)
    # Historial de scraping (con product_count)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS scrape_history (
        id SERIAL PRIMARY KEY,
        url TEXT,
        product_count INTEGER DEFAULT 0,
        anomaly BOOLEAN DEFAULT FALSE,
        scraped_at TIMESTAMP DEFAULT NOW()
    );
    """)
    conn.commit()
    cur.close()
    conn.close()

def get_product(url):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM product_prices WHERE url=%s", (url,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def upsert_price(url, price):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO product_prices (url, last_price, count_seen, sum_prices)
    VALUES (%s, %s, 1, %s)
    ON CONFLICT (url) DO UPDATE
      SET last_price = EXCLUDED.last_price,
          count_seen = product_prices.count_seen + 1,
          sum_prices = product_prices.sum_prices + EXCLUDED.sum_prices;
    """, (url, price, price))
    conn.commit()
    cur.close()
    conn.close()

# Funciones para la web
def add_link(url):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO links (url) VALUES (%s) ON CONFLICT DO NOTHING", (url,))
    conn.commit()
    cur.close()
    conn.close()

def get_all_links():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT url FROM links")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [r['url'] for r in rows]

def log_scrape(url, product_count, anomaly=False):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO scrape_history (url, product_count, anomaly) VALUES (%s, %s, %s)",
        (url, product_count, anomaly)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_scrape_history(limit=50):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT url, product_count, anomaly, scraped_at FROM scrape_history ORDER BY scraped_at DESC LIMIT %s",
        (limit,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
