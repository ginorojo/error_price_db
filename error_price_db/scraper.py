import requests
from bs4 import BeautifulSoup

def get_price(url):
    """
    Obtiene el precio de un producto según la estructura del sitio.
    Devuelve None si no se puede detectar.
    """
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, "html.parser")

        # Falabella
        if "falabella.com" in url:
            price_tag = soup.find("span", {"class": "fb-product-price__final"})
            if price_tag:
                price_str = price_tag.text.strip().replace("$","").replace(".","")
                return float(price_str)

        # Sodimac
        elif "sodimac.cl" in url:
            price_tag = soup.find("span", {"class": "product-price__price"})
            if price_tag:
                price_str = price_tag.text.strip().replace("$","").replace(".","")
                return float(price_str)

        # Lider
        elif "lider.cl" in url:
            price_tag = soup.find("span", {"class": "price"})
            if price_tag:
                price_str = price_tag.text.strip().replace("$","").replace(".","")
                return float(price_str)

        return None
    except Exception as e:
        print("❌ Error al obtener precio:", url, e)
        return None
