# 에어비앤비 호스트 게더링 2026 — 「호스트, 우리가 만나다」

2026년 11월 21일 대한공유숙박호스트협회 연말 게더링(스페이스쉐어 삼성역 센터)의 세 세션을 녹음 내용까지 담아 슬라이드 100장(상세판)으로 정리했다. 예전 28장 요약판도 함께 있다. 참석자가 만든 비공식 정리이고, 숫자는 그날 발표 기준이라 대략값이 있을 수 있다.

**상세판 100장: https://walnut-house.github.io/airbnb-host-gathering-2026/**  
요약판 28장: https://walnut-house.github.io/airbnb-host-gathering-2026/summary/

| 세션 | 연사 | 상세판 쪽 |
|---|---|---|
| 여는 말 | | 3~5 |
| 1 공유숙박업 현황과 전망 | 에어비앤비 코리아 숙박창업팀 | 6~51 |
| 2 호스트를 위한 보험 사례 | 김철기 지점장 | 52~68 |
| 3 매물 발굴부터 슈퍼호스트까지 | 김은비 슈퍼호스트 | 69~99 |
| 세 세션 핵심 10줄 | | 100 |

## 만든 방법

모든 슬라이드는 Tesseract(Mirage) 컴포지션으로 만들고 `tsrct preview`로 렌더했다. `src/`의 파이썬 스크립트가 글자·선·막대를 Tesseract 레이어로 만든다(`lib.py`가 공통 부품, `part_*.py`가 쪽별 내용).

- 렌더 결과: 상세판 `docs/slides/*.png`, 요약판 `docs/summary/slides/*.png` (1920×1080)
- 스크립트: 상세판 `src/`, 요약판 `src/summary/`
- 페이지: `docs/index.html` (GitHub Pages, `docs/` 폴더)
- 편집용 `.tsrct` 원본은 올리지 않았다. 안에 Apple SD Gothic Neo 글꼴 파일이 통째로 들어 있어서다. 스크립트를 macOS에서 돌리면 같은 원본이 다시 만들어진다.
