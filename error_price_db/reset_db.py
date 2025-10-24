import psycopg2
from config import DATABASE_URL

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Eliminar tabla antigua
cur.execute("DROP TABLE IF EXISTS scrape_history;")
conn.commit()

cur.close()
conn.close()

print("Tabla scrape_history eliminada. Ahora inicia tu app y se creará automáticamente con init_db().")
