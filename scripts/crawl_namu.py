"""
나무위키 라면 정보 업데이트 스크립트.

주의:
- 사이트의 이용약관/robots.txt 및 자동화 접근 정책을 먼저 확인하세요.
- 나무위키 HTML 구조가 변경되면 파서 수정이 필요합니다.
- 조리시간은 자동 추출 성공 시에만 갱신하고, 실패하면 기존 값을 유지합니다.
"""

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
SOURCES_FILE = DATA_DIR / "ramen_sources.json"
OUTPUT_FILE = DATA_DIR / "ramen.json"

HEADERS = {
    "User-Agent": "RamenTimer/1.0 (GitHub Actions; data maintenance)"
}

def fetch_text(url):
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser").get_text(" ", strip=True)

def parse_seconds(text):
    patterns = [
        r"(\d+)\s*분\s*(\d+)\s*초",
        r"(\d+)\s*분",
        r"(\d+)\s*초",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if not match:
            continue
        if len(match.groups()) == 2:
            return int(match.group(1)) * 60 + int(match.group(2))
        value = int(match.group(1))
        return value * 60 if "분" in match.group(0) else value
    return None

def find_cooking_time(text):
    # 조리시간/끓이는 시간 주변의 숫자를 우선 탐색
    anchors = ["조리 시간", "조리시간", "끓이는 시간", "끓이는시간", "조리 방법"]
    for anchor in anchors:
        idx = text.find(anchor)
        if idx >= 0:
            chunk = text[idx:idx + 500]
            seconds = parse_seconds(chunk)
            if seconds:
                return seconds
    return None

def main():
    sources = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    old = json.loads(OUTPUT_FILE.read_text(encoding="utf-8")) if OUTPUT_FILE.exists() else {}
    old_map = {item["name"]: item for item in old.get("ramen", [])}

    results = []

    for source in sources.get("pages", []):
        item = old_map.get(source["name"], {
            "name": source["name"],
            "type": source.get("type", "기타"),
            "brand": source.get("brand", ""),
            "cookingTime": 180,
            "popular": source.get("popular", False),
            "sourceUrl": source["url"],
        })

        item["type"] = source.get("type", item.get("type", "기타"))
        item["brand"] = source.get("brand", item.get("brand", ""))
        item["popular"] = source.get("popular", item.get("popular", False))
        item["sourceUrl"] = source["url"]

        try:
            text = fetch_text(source["url"])
            seconds = find_cooking_time(text)
            if seconds and 30 <= seconds <= 1800:
                item["cookingTime"] = seconds
            print(f"[OK] {source['name']}: {item['cookingTime']} sec")
        except Exception as exc:
            print(f"[WARN] {source['name']}: {exc}")

        results.append(item)
        time.sleep(1.5)

    output = {
        "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "source": "NamuWiki pages listed in data/ramen_sources.json",
        "ramen": results,
    }
    OUTPUT_FILE.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

if __name__ == "__main__":
    main()
