import csv
import json
import urllib.request
from datetime import datetime

# 구글 시트 CSV 게시 링크 적용
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vST5MajC3yBxjqxfz6uNk4OBvs39hkKUqbZ2Nai_40WZ7aNgTEiYx6u7rSLYgwHEuT897gb6pS65W1U/pub?output=csv"

def main():
    try:
        req = urllib.request.urlopen(SHEET_CSV_URL)
        lines = [line.decode('utf-8') for line in req.readlines()]
        reader = csv.DictReader(lines)

        ramen_list = []
        for row in reader:
            name = row.get('name', '').strip()
            if not name:
                continue

            # 조리시간 숫자로 변환 (입력이 안 되어있거나 오류 시 기본 240초)
            raw_time = row.get('cookingTime', '').strip()
            try:
                cooking_time = int(raw_time)
            except ValueError:
                cooking_time = 240

            # 비고 칸에 '인기' 문구가 있거나, NO 번호가 1~8번이면 인기 라면 지정
            note = row.get('비고', '').strip()
            no_str = row.get('NO', '').strip()
            
            is_popular = '인기' in note or (no_str.isdigit() and int(no_str) <= 8)

            ramen_list.append({
                "name": name,
                "type": row.get('type', '봉지라면').strip(),
                "brand": row.get('brand', '').strip(),
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

        print(f"성공! 구글 시트에서 총 {len(ramen_list)}개의 라면 데이터를 가져왔습니다.")

    except Exception as e:
        print(f"구글 시트 읽기 실패: {e}")

if __name__ == "__main__":
    main()
