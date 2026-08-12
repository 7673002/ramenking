import csv
import json
import urllib.request
from datetime import datetime
import re

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vST5MajC3yBxjqxfz6uNk4OBvs39hkKUqbZ2Nai_40WZ7aNgTEiYx6u7rSLYgwHEuT897gb6pS65W1U/pub?output=csv"

def get_val(row, keys, default=""):
    for k in keys:
        if k in row and row[k]:
            return str(row[k]).strip()
    return default

def main():
    try:
        req = urllib.request.Request(
            SHEET_CSV_URL, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8-sig')

        lines = content.splitlines()
        reader = csv.DictReader(lines)
        ramen_list = []

        for raw_row in reader:
            # 헤더 공백 제거 및 소문자 변환
            row = {str(k).strip().lower(): v for k, v in raw_row.items() if k is not None}
            
            # 영문/한글 헤더 모두 지원
            name = get_val(row, ['name', '이름', '라면이름', '라면'])
            if not name:
                continue

            ramen_type = get_val(row, ['type', '종류', '구분'], '봉지라면')
            brand = get_val(row, ['brand', '브랜드', '제조사'], '')
            
            # 조리시간 숫자 정밀 파싱 (숫자 외 문자가 섞여 있어도 숫자만 추출)
            raw_time = get_val(row, ['cookingtime', 'cooking_time', '조리시간', '시간'], '240')
            num_match = re.search(r'\d+', raw_time)
            cooking_time = int(num_match.group()) if num_match else 240

            note = get_val(row, ['비고', 'note', 'popular', '인기'])
            no_str = get_val(row, ['no', '번호'])
            
            is_popular = '인기' in note or note.lower() == 'true' or (no_str.isdigit() and int(no_str) <= 8)

            ramen_list.append({
                "name": name,
                "type": ramen_type,
                "brand": brand,
                "cookingTime": cooking_time,
                "popular": is_popular
            })

        result = {
            "updatedAt": datetime.now().strftime("%Y-%m-%d"),
            "source": "Google Sheets Database",
            "ramen": ramen_list
        }

        with open('data/ramen.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"✅ 성공! 총 {len(ramen_list)}개의 라면 데이터를 정상 변환했습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
