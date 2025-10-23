# db.py
import psycopg2
from psycopg2.extras import RealDictCursor
from config import DATABASE_URL

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    # Tabla que almacena precios históricos (guardamos último precio y un promedio simple)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS product_prices (
        url TEXT PRIMARY KEY,
        last_price NUMERIC,
        count_seen INTEGER DEFAULT 0,
        sum_prices NUMERIC DEFAULT 0  -- para calcular promedio simple: sum_prices / count_seen
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
    """
    Inserta o actualiza el registro: actualiza last_price, count_seen, sum_prices
    """
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
