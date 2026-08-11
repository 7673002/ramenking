import json
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time
import os

def parse_time(text):
    # 텍스트에서 'X분 Y초' 형태를 찾아 초 단위로 변환합니다.
    match = re.search(r'(\d+)\s*분(?:\s*(\d+)\s*초)?', text)
    if match:
        minutes = int(match.group(1))
        seconds = int(match.group(2)) if match.group(2) else 0
        return minutes * 60 + seconds
    return None

def main():
    # 1. 크롤링할 라면 목록 (ramen_sources.json) 불러오기
    source_path = 'data/ramen_sources.json'
    if not os.path.exists(source_path):
        print("소스 파일이 없습니다.")
        return

    with open(source_path, 'r', encoding='utf-8') as f:
        sources = json.load(f)

    # 봇 차단을 피하기 위해 일반 브라우저처럼 위장 (User-Agent)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    updated_ramen = []

    for item in sources['pages']:
        print(f"[{item['name']}] 정보 업데이트 중...")
        try:
            # 나무위키 페이지 접속
            response = requests.get(item['url'], headers=headers, timeout=10)
            cooking_time = 180 # 기본값 3분(180초)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text()
                
                # 조리시간 텍스트 추출 시도
                found_time = parse_time(text)
                if found_time:
                    cooking_time = found_time
                    print(f" -> 조리시간 찾음: {cooking_time}초")
                else:
                    print(" -> 조리시간을 찾지 못해 기본값(3분) 적용")
            
            item_data = {
                "name": item['name'],
                "type": item['type'],
                "brand": item['brand'],
                "cookingTime": cooking_time,
                "popular": item['popular'],
                "sourceUrl": item['url']
            }
            updated_ramen.append(item_data)
            
        except Exception as e:
            print(f"Error: {item['name']} 크롤링 실패 - {e}")
        
        # 서버에 무리를 주지 않기 위해 2초 대기
        time.sleep(2)

    # 2. 최신화된 정보로 ramen.json 업데이트
    result = {
        "updatedAt": datetime.now().strftime("%Y-%m-%d"),
        "source": "GitHub Actions + Namuwiki Crawling",
        "ramen": updated_ramen
    }

    with open('data/ramen.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
