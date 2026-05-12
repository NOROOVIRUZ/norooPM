#!/usr/bin/env python3
"""norooPM scraper entry point — GitHub Actions에서 실행"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from scrapers import amazon, aliexpress, jd
from core.storage import save_result

DEFAULT_CATEGORIES = [
    "전동칫솔",
    "마사지기",
    "이어폰",
    "블루투스스피커",
    "공기청정기",
]

PLATFORM_MAP = {
    "amazon": amazon,
    "aliexpress": aliexpress,
    "jd": jd,
}


def run(categories: list[str], platforms: list[str]):
    for category in categories:
        print(f"\n▶ [{category}] 수집 시작")
        results = {}

        for platform_name in platforms:
            mod = PLATFORM_MAP.get(platform_name)
            if not mod:
                continue
            print(f"  └─ {platform_name} 스크래핑 중...")
            try:
                products = mod.scrape(category)
                results[platform_name] = products
                print(f"     ✅ {len(products)}개 수집")
            except Exception as e:
                print(f"     ❌ 실패: {e}")
                results[platform_name] = []

        out = save_result(category, results)
        print(f"  💾 저장 완료: {out}")


def main():
    parser = argparse.ArgumentParser(description="norooPM market scraper")
    parser.add_argument(
        "--categories", nargs="+", default=DEFAULT_CATEGORIES,
        help="수집할 카테고리 (예: 전동칫솔 마사지기)"
    )
    parser.add_argument(
        "--platforms", nargs="+", default=["amazon", "aliexpress", "jd"],
        choices=["amazon", "aliexpress", "jd"],
        help="수집할 플랫폼"
    )
    args = parser.parse_args()
    run(args.categories, args.platforms)


if __name__ == "__main__":
    main()
