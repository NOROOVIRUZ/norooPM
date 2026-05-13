import re
import time
import random
import xml.etree.ElementTree as ET
from scrapling.fetchers import Fetcher
from core.models import Product

CATEGORY_NODES = {
    "전동칫솔": "1232614011",
    "마사지기": "3760911",
    "이어폰": "2102313011",
    "블루투스스피커": "2975312011",
    "공기청정기": "2102148011",
    "안마기": "3760911",
    "드라이어": "11036781",
    "로봇청소기": "2492080011",
}


def scrape(category: str, max_items: int = 20) -> list[Product]:
    node_id = CATEGORY_NODES.get(category)
    if not node_id:
        return []

    url = f"https://www.amazon.com/rss/bestsellers/hpc/{node_id}"
    try:
        page = Fetcher.get(url, stealthy_headers=True)
        print(f"[Amazon] 상태:{page.status} 길이:{len(page.html_content)}")
        return _parse_rss(page.html_content, max_items)
    except Exception as e:
        print(f"[Amazon] 실패: {e}")
        return []


def _parse_rss(xml_text: str, max_items: int) -> list[Product]:
    products = []
    try:
        root = ET.fromstring(xml_text)
        for i, item in enumerate(root.findall(".//item")[:max_items]):
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            desc = item.findtext("description", "")

            price_str, price_usd = "", 0.0
            m = re.search(r'\$[\d,]+\.?\d*', desc)
            if m:
                price_str = m.group()
                price_usd = float(price_str.replace("$", "").replace(",", ""))

            thumbnail = ""
            m2 = re.search(r'src=["\']([^"\']+)["\']', desc)
            if m2:
                thumbnail = m2.group(1)

            if title:
                products.append(Product(
                    rank=i + 1, name=title, price=price_str, price_usd=price_usd,
                    thumbnail=thumbnail, product_url=link, platform="amazon",
                ))
    except ET.ParseError as e:
        print(f"[Amazon] XML 파싱 실패: {e}")
    return products
