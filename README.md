# 🍜 라면 타이머

라면을 선택하면 해당 라면의 조리시간으로 타이머가 시작되는 정적 웹사이트입니다.

## 기능

- 인기 라면 바로 선택
- 봉지라면 / 컵라면 필터
- 라면 검색
- 라면별 조리시간 타이머
- 시작 / 일시정지 / 초기화
- 완료 알림음
- GitHub Pages에서 무료 운영
- GitHub Actions를 통한 라면 데이터 정기 업데이트

## GitHub Pages 배포

1. 이 저장소에 파일을 그대로 업로드합니다.
2. GitHub 저장소의 `Settings → Pages`로 이동합니다.
3. `Build and deployment`에서 `Deploy from a branch`를 선택합니다.
4. Branch는 `main`, Folder는 `/ (root)`로 선택합니다.
5. 저장하면 GitHub Pages 주소가 생성됩니다.

## 라면 데이터

`data/ramen.json`이 실제 사이트에서 읽는 데이터입니다.

`data/ramen_sources.json`에 자동 업데이트할 나무위키 페이지를 등록합니다.

```json
{
  "name": "신라면",
  "type": "봉지라면",
  "brand": "농심",
  "url": "https://namu.wiki/w/신라면",
  "popular": true
}
```

## 자동 업데이트

`.github/workflows/update-ramen.yml`이 하루 한 번 실행되어
`scripts/crawl_namu.py`를 실행합니다.

중요: 자동 크롤링을 사용하기 전에 대상 사이트의 이용약관과 robots.txt,
자동화 접근 정책을 확인하세요. 사이트 구조가 변경되면 크롤러도 수정해야 합니다.

또한 자동으로 추출된 조리시간이 실제 제품 포장지 표기와 다를 수 있으므로
사용자에게는 제품 포장지 안내를 우선하도록 표시합니다.
