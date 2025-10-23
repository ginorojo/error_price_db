# scraper.py
from playwright.sync_api import sync_playwright
import re
import time

def parse_price_text(text):
    # extrae número con $ y convierte a float
    if not text:
        return None
    m = re.search(r'([\d\.\,]{1,20})', text.replace('\xa0',' '))
    if not m:
        return None
    s = m.group(1)
    # normalizar: "1.299.990" -> "1299990", "1,299.99" -> "1299.99"
    if s.count('.') > 1 and ',' not in s:
        s = s.replace('.', '')
    if ',' in s and s.count(',') == 1 and '.' not in s:
        s = s.replace(',', '.')
    s = s.replace(',', '').replace(' ', '')
    try:
        return float(s)
    except:
        return None

def get_price(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0")
        page = context.new_page()
        try:
            page.goto(url, timeout=20000, wait_until='networkidle')
        except Exception as e:
            # intentar sin networkidle
            try:
                page.goto(url, timeout=30000)
            except:
                browser.close()
                return None

        # Intentar selectores comunes
        selectors = [
            '[class*="price"]',
            '[id*="price"]',
            '[data-price]',
            '.precio',
            '.price',
            '.prices',
            '.product-price',
            '.product__price'
        ]
        for sel in selectors:
            try:
                el = page.query_selector(sel)
                if el:
                    text = el.inner_text().strip()
                    pval = parse_price_text(text)
                    if pval:
                        browser.close()
                        return pval
            except:
                continue

        # Si no lo encontramos por selectores, buscar en todo el HTML
        html = page.content()
        # buscar patrones de $nnn
        m = re.search(r'\$[\s]*([\d\.,]+)', html)
        if m:
            pval = parse_price_text(m.group(1))
            browser.close()
            return pval

        browser.close()
        return None
