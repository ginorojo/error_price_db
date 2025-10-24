import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from config import RATE_LIMIT_SECONDS, MAX_PRODUCTS
import time

def detect_pattern(url):
    """
    Detecta automáticamente el patrón de URL de producto
    según el dominio del sitio.
    """
    if "sodimac.cl" in url:
        return "/product/"
    elif "falabella.com" in url:
        return "/product/"
    elif "lider.cl" in url:
        return "/producto/"
    else:
        return "/product/"

def crawl_site(start_url):
    """
    Recorre la categoría agregada y devuelve URLs de productos
    detectando automáticamente el patrón según el dominio.
    """
    pattern_contains = detect_pattern(start_url)
    visited = set()
    to_visit = [start_url]
    product_urls = set()

    print(f"🕷️ Iniciando crawl en: {start_url}")
    print(f"🔎 Buscando URLs que contengan: '{pattern_contains}'")

    while to_visit and len(product_urls) < MAX_PRODUCTS:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code != 200:
                print(f"⚠️ Error {resp.status_code} al acceder a {url}")
                continue
            time.sleep(RATE_LIMIT_SECONDS)
        except Exception as e:
            print("❌ Error al acceder a:", url, e)
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a['href']
            full_url = urljoin(start_url, href)

            # Mantenerse dentro del mismo dominio
            if not full_url.startswith(start_url.split('/')[0] + '//' + start_url.split('/')[2]):
                continue

            # Detectar productos
            if pattern_contains in full_url:
                url_clean = full_url.split('?')[0]
                if url_clean not in product_urls:
                    product_urls.add(url_clean)
                    print("🛒 Producto detectado:", url_clean)
            else:
                if full_url not in visited and full_url not in to_visit:
                    to_visit.append(full_url)

        if len(visited) > 3000:
            print("⛔ Máximo de páginas visitadas alcanzado, deteniendo crawl.")
            break

    print(f"✅ Crawl terminado. Se detectaron {len(product_urls)} productos en {start_url}")
    return list(product_urls)
