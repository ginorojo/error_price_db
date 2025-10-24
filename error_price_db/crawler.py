import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from config import RATE_LIMIT_SECONDS, MAX_PRODUCTS
import time

def crawl_site(start_url, pattern_contains="/product/"):
    """
    Crawl avanzado: recorre enlaces internos y devuelve URLs que contienen pattern_contains.
    Soporta páginas de categoría para obtener todos los productos.
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
            full_url = urljoin(start_url, href)

            if not full_url.startswith(start_url):
                continue

            # URLs de producto
            if pattern_contains in full_url:
                url_clean = full_url.split('?')[0]
                if url_clean not in product_urls:
                    product_urls.add(url_clean)
                    print("Producto encontrado:", url_clean)
            else:
                if full_url not in visited and full_url not in to_visit:
                    to_visit.append(full_url)

        if len(visited) > 3000:
            print("Máximo de páginas visitadas alcanzado, deteniendo crawl.")
            break

    print(f"Crawl terminado. Se encontraron {len(product_urls)} productos en {start_url}")
    return list(product_urls)
