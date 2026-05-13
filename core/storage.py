import json
import os
from datetime import datetime, timezone
from dataclasses import asdict
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data"


def save_result(category: str, platforms: dict) -> Path:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    category_dir = DATA_DIR / category
    category_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "category": category,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "platforms": {
            k: [asdict(p) for p in v] for k, v in platforms.items()
        },
    }

    out_path = category_dir / f"{today}.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    (category_dir / "latest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    _update_manifest(category, today)
    return out_path


def _update_manifest(category: str, date: str):
    manifest_path = DATA_DIR / "manifest.json"
    manifest = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())

    manifest[category] = {"last_updated": date}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
