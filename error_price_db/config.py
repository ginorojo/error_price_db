import os

# Variables de entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8314097677:AAEX_60gGK2AlMtzw-O8rvhl8oaaqQT7gdw")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5232906997")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://error_price_db:JtWumFYsVgD21U8AAADST3y2jrReSY3q@dpg-d3sn1ce3jp1c739tgqi0-a.oregon-postgres.render.com/error_price_db"
)

# Parámetros de control
RATE_LIMIT_SECONDS = 2
MAX_PRODUCTS = 3000
ANOMALY_FACTOR = 0.2
