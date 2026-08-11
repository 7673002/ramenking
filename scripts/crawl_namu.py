import json
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time
from urllib.parse import unquote

def extract_cooking_time(soup):
    # 1. 문서 내 모든 표(tr)를 돌며 '조리' 또는 '끓' 키워드가 있는 행 탐색
    for tr in soup.find_all('tr'):
        text = tr.get_text()
        if any(k in text for k in ['조리', '끓', '조리법', '시간']):
            # 'N분 N초' 또는 'N분' 형태 정밀 추출
            match = re.search(r'(\d+)\s*분(?:\s*(\d+)\s*초)?', text)
            if match:
                minutes = int(match.group(1))
                seconds = int(match.group(2)) if match.group(2) else 0
                # 정상적인 라면 조리시간 범위(1분~10분) 체크
                if 1 <= minutes <= 10:
                    return minutes * 60 + seconds

    # 2. 표에서 못 찾은 경우 본문 문맥('조리... X분') 탐색
    full_text = soup.get_text()
    matches = re.findall(r'(?:조리|끓)[^\n]{0,30}?(\d+)\s*분(?:\s*(\d+)\s*초)?', full_text)
    for m in matches:
        minutes = int(m[0])
        seconds = int(m[1]) if m[1] else 0
        if 1 <= minutes <= 10:
            return minutes * 60 + seconds

    return None

def main():
    index_url = "https://namu.wiki/w/%EB%9D%BC%EB%A9%B4/%EC%A2%85%EB%A5%98"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    print("나무위키 라면 목록 수집 시작...")
    try:
        res = requests.get(index_url, headers=headers, timeout=10)
        if res.status_code != 200:
            print(f"목록 접속 실패: {res.status_code}")
            return
    except Exception as e:
        print(f"오류 발생: {e}")
        return

    soup = BeautifulSoup(res.text, 'html.parser')
    discovered_ramen = {}

    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text().strip()
        if href.startswith('/w/') and text and 1 < len(text) < 25:
            decoded = unquote(href)
            if not any(k in decoded for k in ['상위문서', '분류:', '나무위키:', '파일:', '틀:', '토론:']):
                if text not in discovered_ramen:
                    discovered_ramen[text] = f"https://namu.wiki{href}"

    ramen_list = []
    MAX_CRAWL_COUNT = 60

    for count, (name, url) in enumerate(discovered_ramen.items()):
        if count >= MAX_CRAWL_COUNT:
            break

        ramen_type = "컵라면" if any(k in name for k in ["컵", "사발", "용기", "큰컵", "소컵"]) else "봉지라면"
        # 기본 디폴트값 (실패 시 기본 4분 / 컵라면 3분)
        cooking_time = 180 if ramen_type == "컵라면" else 240

        try:
            sub_res = requests.get(url, headers=headers, timeout=4)
            if sub_res.status_code == 200:
                sub_soup = BeautifulSoup(sub_res.text, 'html.parser')
                parsed_time = extract_cooking_time(sub_soup)
                if parsed_time:
                    cooking_time = parsed_time
        except Exception:
            pass

        ramen_list.append({
            "name": name,
            "type": ramen_type,
            "brand": "나무위키 수집",
            "cookingTime": cooking_time,
            "popular": count < 8,
            "sourceUrl": url
        })
        
        mins, secs = cooking_time // 60, cooking_time % 60
        print(f"[{count+1}/{MAX_CRAWL_COUNT}] {name} ({ramen_type}) - {mins}분 {secs}초")
        time.sleep(0.5)

    result = {
        "updatedAt": datetime.now().strftime("%Y-%m-%d"),
        "source": f"Namuwiki Auto Crawling ({len(ramen_list)}종)",
        "ramen": ramen_list
    }

    with open('data/ramen.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"완료! {len(ramen_list)}개 라면 수집 완료.")

if __name__ == "__main__":
    main()
