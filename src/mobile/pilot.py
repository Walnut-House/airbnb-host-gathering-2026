"""Pilot: 5 landscape slides of the 상세판 converted with lib_m (one landscape slide = one mobile slide).
Run: python3 src/pilot.py [names…]  → pilot/<name>.png|.tsrct"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from lib_m import *
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(os.path.dirname(BASE), "slides-detail")
K1 = "세션 1  ·  현황과 전망"; K1b = "세션 1  ·  운영 팁"; K3 = "세션 3  ·  매물 발굴부터 슈퍼호스트까지"


def cover(d):  # 0-01-cover — free layout, no header(); landscape has no page number → no footer
    y = tx(d, X, 100, CW, "2026. 11. 21  ·  스페이스쉐어 삼성역 센터", "body", size=34, style="Medium", c=SEC)
    y = tx(d, X, y + 28, CW, "호스트,\n우리가 만나다", "title", size=124, lead=140, balance=False)
    y = tx(d, X, y + 24, CW, "대한공유숙박호스트협회 연말 게더링 — 세션 3개 상세판", "sub", size=38, lead=56)
    y = rule(d, y + 44)
    y = tx(d, X, y + 36, CW, "늘어난 비율 · 서울, 2026년 1~9월", "head")
    y = stats(d, y + 16, [("+47%", "서울 도시민박 숙소", True), ("+22%", "서울 방문 외국인", False)], size=HERO)
    y = rule(d, y + 40)
    y = tx(d, X, y + 36, CW, "직접 예약 링크 수수료 · 시범", "head")
    y = bigstat(d, X, y + 16, CW, "10%", "15.5%에서 낮춤 · 시범, 일부 호스트만", size=HERO)
    numlist(d, y + 48, [
        ("공유숙박업 현황과 전망", ["에어비앤비 코리아 숙박창업팀", ("리스팅·가격·리뷰로 이기는 시장", "ink")]),
        ("호스트를 위한 보험 사례", ["김철기 지점장", ("업종을 숙박업으로, 사고 나면 보험사부터", "ink")]),
        ("매물 발굴부터 슈퍼호스트까지", ["김은비 슈퍼호스트", ("허가 가능성 확인이 계약보다 먼저", "ink")])], pad=18)


def supply(d):  # 1a-11-supply — bars
    y = header(d, K1, "외국인보다 숙소가 더 빨리 늘었다", "서울 숙소는 외국인 증가율의 두 배 넘게 늘었다")
    y = section(d, y, "늘어난 비율 · 서울, 2026년 1~9월", first=True)
    y = bars(d, y + 8, [("숙소", 47, "+47%"), ("외국인", 22, "+22%")], hi=0, maxv=47)
    y = section(d, y, "서울 도시민박업 숙소 수")
    y = bars(d, y + 8, [("2024년 말", 3217, "3,217"), ("2025년 말", 4970, "4,970"), ("2026년 9월", 7313, "7,313")])
    takeaway(d, y, "호스트가 할 일 — 숙소 수가 2년도 안 돼 2배 넘게 늘었으니, 위치만 믿지 말 것")


def desc_ai(d):  # 1b-11-desc-ai — top band (horizontal timeline, no head) → left column → right column
    y = header(d, K1b, "설명은 AI로 쓰고, 호스트는 검수만 한다", "형식을 손으로 하나하나 적을 필요 없이 금방 나온다")
    y = vtimeline(d, y + 8, [("레퍼런스 고르기", "주변에서 잘 쓴 숙소 설명을 찾는다"),
                             ("복사", "그 화면을 캡처하거나 글을 긁어 온다"),
                             ("AI에 학습", "GPT·Gemini 등에 보여 준다"),
                             ("내 정보 넣기", "내 숙소 정보와 함께 「비슷한 형식으로 정리해 줘」"),
                             ("검수 후 업로드", "마지막 검수만 하고 올린다")], hi=4)
    y = section(d, y, "레퍼런스 찾는 법", rule=True)
    y = numlist(d, y, ["에어비앤비에서 내 숙소 지역을 검색한다",
                       "잘하는 숙소를 눌러 본다 — 정보는 모두 공개",
                       "어떻게 쓰고 무엇을 잘하는지 본다"])
    y = section(d, y, "AI에게 이렇게 시킨다")
    quote(d, y + 8, "이 숙소 설명 형식으로, 아래 내 숙소 정보를 이모지·글머리 기호로 항목별 정리해 줘",
          "레퍼런스 설명과 내 숙소 정보를 함께 붙여 넣는다")


def refund(d):  # 1c-07-refund-by-date — table (with mini-bar column) → cards; right column → numlist
    y = header(d, K1b, "환불 정책과 최소 숙박일은 날짜별로 다르게 건다",
               "성수기·이벤트는 엄격하게, 비어 있는 임박 날짜는 유연하게")
    y = section(d, y, "날짜별 환불 정책", first=True)
    y = cards(d, y, [card("Flexible", "비어 있는 임박 날짜", value="24시간 전", bar=1 / 30),
                     card("Moderate", "비수기", value="5일 전", bar=5 / 30),
                     card("Limited", "수요 많은 날짜", value="14일 전", bar=14 / 30),
                     card("Firm", "성수기·대형 이벤트", value="30일 전", bar=1)],
              keys=("정책 · 전액 환불 마감 · 쓸 날짜",))
    y = note(d, y, "Limited는 7~14일 전, Firm은 7~30일 전이면 50% 환불")
    y = section(d, y, "비수기만 골라 풀기")
    y = numlist(d, y, [("날짜별로 따로 걸 수 있다", "환불 정책·최소 숙박일 모두 — 아직 모르는 호스트가 많다"),
                       ("달력에서 비수기만 쭉 선택", "고른 기간에만 따로 설정"),
                       ("그 기간만 최소 숙박일 줄이기", "노출을 늘리는 방법"),
                       ("환불도 더 유연하게", "비어 있는 임박 날짜는 Flexible")], hi=1)
    takeaway(d, y, "호스트가 할 일 — 달력에서 비수기만 골라 환불은 유연하게, 최소 숙박일은 줄이기")


def quick(d):  # 3b-13-quick-reply — two horizontal timelines → vertical; short bodies → inline
    y = header(d, K3, "빠른 답변으로 예약마다 메시지가 자동으로 나간다", "녹음에서 — 에어비앤비 빠른 답변(예약 메시지) 설정법")
    y = section(d, y, "설정 3단계", first=True)
    y = vtimeline(d, y + 8, [("메시지 만들기", "빠른 답변(예약 메시지)에서 새 메시지 만들기"),
                             ("세부 정보 추가", "+ 버튼으로 게스트 이름·체크인 날짜·체크아웃 시간 등을 넣으면 예약마다 자동으로 채워짐"),
                             ("시간 지정 발송", "체크인 당일·하루 전·이틀 전 등 날짜와 시각까지 맞춤 설정")])
    y = section(d, y, "언제 무엇을 보내나", rule=True)
    y = vtimeline(d, y + 8, [("예약 문의 직후", "인원·소음 동의받기"), ("예약 확정", "감사"),
                             ("체크인 전날", "리마인더"), ("체크인 당일", "길 안내·키패드 영상"),
                             ("체크인 다음 날", "\"불편한 거 없니?\""), ("체크아웃 전날", "리마인더"),
                             ("체크아웃 후", "리뷰 요청")], hi=6, gap=16, inline=340)
    takeaway(d, y, "호스트가 할 일 — 메시지 7개를 한 번 만들어 두면 예약마다 이름·날짜가 채워져 저절로 나간다")


if __name__ == "__main__":
    run([("0-01-cover", cover), ("1a-11-supply", supply), ("1b-11-desc-ai", desc_ai),
         ("1c-07-refund-by-date", refund), ("3b-13-quick-reply", quick)],
        outdir=os.path.join(BASE, "pilot"), src_dir=SRC)
