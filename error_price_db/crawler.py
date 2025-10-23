# crawler.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from config import RATE_LIMIT_SECONDS, MAX_PRODUCTS
import time

# Lista de dominios objetivo (ejemplos)
SITES = [
    "https://www.falabella.com/falabella-cl/",
    "https://www.sodimac.cl/sodimac-cl/",
    "https://www.lider.cl/",
    "https://simple.ripley.cl/",
    "https://www.paris.cl/"
]

def crawl_site(start_url, pattern_contains="/product/"):
    """
    Crawl simple: recorre enlaces internos y devuelve URLs que contienen pattern_contains.
    NOTA: no es un crawler perfecto (no sigue robots.txt) — úsalo con moderación.
    """
    visited = set()
    to_visit = [start_url]
    product_urls = set()

    while to_visit and len(product_urls) < MAX_PRODUCTS:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)
        try:
            resp = requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
            time.sleep(RATE_LIMIT_SECONDS)
        except Exception as e:
            print("Error al acceder a:", url, e)
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a['href']
            full = urljoin(start_url, href)

            # filtrar urls internas
            if not full.startswith(start_url):
                continue

            # si parece url de producto, guardarla
            if pattern_contains in full:
                url_clean = full.split('?')[0]  # quitar query params
                product_urls.add(url_clean)
                print("Producto encontrado:", url_clean)  # <-- depuración
            else:
                if full not in visited:
                    to_visit.append(full)

        # seguridad: no sobre-explorar
        if len(visited) > 2000:
            print("Máximo de páginas visitadas alcanzado, deteniendo crawl.")
            break

    print(f"Crawl terminado. Se encontraron {len(product_urls)} productos en {start_url}")
    return list(product_urls)
