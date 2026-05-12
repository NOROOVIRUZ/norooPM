import time
import random
from core.models import Product

try:
    from DrissionPage import ChromiumPage, ChromiumOptions
    DRISSION_AVAILABLE = True
except ImportError:
    DRISSION_AVAILABLE = False
    print("[JD] DrissionPage 미설치 — JD 스크래핑 건너뜀")


def scrape(category: str, max_items: int = 20) -> list[Product]:
    if not DRISSION_AVAILABLE:
        return []

    query = category
    url = f"https://search.jd.com/Search?keyword={query}&enc=utf-8&wq={query}"

    try:
        options = ChromiumOptions().headless()
        page = ChromiumPage(addr_or_opts=options)
        page.get(url)
        time.sleep(random.uniform(2.0, 3.5))
    except Exception as e:
        print(f"[JD] 브라우저 실행 실패: {e}")
        return []

    products = []
    try:
        items = page.eles(".gl-item")
        for i, item in enumerate(items[:max_items]):
            try:
                name_el = item.ele(".p-name em", timeout=1)
                price_el = item.ele(".p-price strong i", timeout=1)
                img_el = item.ele(".p-img img", timeout=1)
                link_el = item.ele(".p-img a", timeout=1)
                commit_el = item.ele(".p-commit a", timeout=1)

                name = name_el.text.strip() if name_el else ""
                price_str = f"¥{price_el.text.strip()}" if price_el else ""
                price_usd = _cny_to_usd(price_el.text.strip() if price_el else "0")
                src = img_el.attr("src") or img_el.attr("data-lazy-img") if img_el else ""
                thumbnail = f"https:{src}" if src.startswith("//") else src
                href = link_el.attr("href") if link_el else ""
                product_url = f"https:{href}" if href.startswith("//") else href
                sales = commit_el.text.strip() if commit_el else None

                if name:
                    products.append(Product(
                        rank=i + 1,
                        name=name,
                        price=price_str,
                        price_usd=price_usd,
                        thumbnail=thumbnail,
                        product_url=product_url,
                        platform="jd",
                        sales=sales,
                    ))
            except Exception:
                continue
    finally:
        page.quit()

    return products


def _cny_to_usd(cny_str: str) -> float:
    # 고정 환율 근사값 (1 CNY ≈ 0.138 USD)
    try:
        return round(float(cny_str.replace(",", "").strip()) * 0.138, 2)
    except ValueError:
        return 0.0
