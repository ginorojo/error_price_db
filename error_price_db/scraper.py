from playwright.sync_api import sync_playwright
import re
import time

def parse_price_text(text):
    if not text:
        return None
    m = re.search(r'([\d\.\,]{1,20})', text.replace('\xa0',' '))
    if not m:
        return None
    s = m.group(1)
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
        except:
            try:
                page.goto(url, timeout=30000)
            except:
                browser.close()
                return None

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
                    val = parse_price_text(text)
                    if val:
                        browser.close()
                        return val
            except:
                continue

        html = page.content()
        m = re.search(r'\$[\s]*([\d\.,]+)', html)
        if m:
            val = parse_price_text(m.group(1))
            browser.close()
            return val

        browser.close()
        return None
