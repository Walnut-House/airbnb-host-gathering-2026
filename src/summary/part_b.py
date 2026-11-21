import sys; sys.path.insert(0,"src"); from lib import *
import datetime
PAGE0=9
K="세션 1  ·  운영 팁"

def lines(n,size): return int(n*size*1.45)+4

def rows(d,x,w,y,pitch,items,size=24,nums=True,start=1,hi=None,bold=()):
    """numlist-style ruled rows. items: str, or (label,text,label_w). Number gap 40. bold = indices with SemiBold label."""
    for i,it in enumerate(items):
        d.rect(x,y,w,2,LINE)
        ty=y+(pitch-size*1.5)/2
        tx=x
        if nums:
            d.text(x,ty,40,size*1.5,str(start+i),size,"SemiBold",ACC if i==hi else SEC); tx=x+40
        if isinstance(it,tuple):
            lab,txt,lw=it
            d.text(tx,ty,lw,size*1.5,lab,size,"SemiBold" if (i in bold or not bold) else "Regular",INK)
            d.text(tx+lw,ty,w-(tx-x)-lw,size*1.5,txt,size,"Regular",INK)
        else:
            d.text(tx,ty,w-(tx-x),size*1.5,it,size,"Regular",INK)
        y+=pitch
    d.rect(x,y,w,2,LINE)
    return y

# 09 algorithm axes + guest favorites
def p09(d):
    header(d,K,"알고리즘은 세 축을 본다 — 빈칸 없이 채울 것","돈 내는 광고가 없다 — 5점 리뷰와 프로모션이 곧 광고",page=PAGE0+0)
    col_head(d,120,780,"알고리즘에 영향을 주는 「변하지 않는」 항목")
    col_head(d,1000,800,"게스트 선호 숙소 vs 일반 숙소")
    divider(d,y1=870)
    groups=[("기본 정보","제목 · 숙소 설명 · 사진+캡션\n편의시설 · 각종 기타 설명",200),
            ("가격 & 예약","비슷한 숙소 대비 가격 경쟁력 · 각종 프로모션\n즉시예약 · 달력 미리 열기",200),
            ("고객 응대","리뷰 · 게스트 선호 · 슈퍼호스트\n자동 메시지",200)]
    y=420
    for t,b,lw in groups:
        d.rect(120,y,780,2,LINE)
        d.text(120,y+14,lw,36,t,24,"SemiBold",INK)
        d.text(120+lw,y+14,780-lw,72,b,24,"Regular",INK)
        y+=96
    d.rect(120,y,780,2,LINE)
    note(d,120,y+24,780,"직원도 알고리즘을 100% 모른다(요소가 수천 개) — 실험을 반복해 자기 공식을 만들 것",lines=2)
    st=[("1.4배","설명 글이 더 길다"),("1.4배","사진이 더 많다"),
        ("+4% 이상","사진이 고화질일 가능성"),("1.5배 이상","편의시설이 더 많다")]
    for i,(big,lab) in enumerate(st):
        x=1000+(i%2)*420; y=[420,612][i//2]
        d.rect(x,y,380,2,LINE)
        bigstat(d,x,y+24,380,big,lab,hero=False,acc=(i==3))
    takeaway(d,"호스트가 할 일 — 빈칸은 다 채우기, 빈 정보는 게스트 불안으로 쌓여 예약이 안 들어온다")

# 10 setting tips
def p10(d):
    header(d,K,"즉시예약을 켜고, 달력은 길게 열어 둔다","녹음에서 나온 설정 팁 일곱 가지 — 부담되는 설정은 비수기에 먼저 실험",page=PAGE0+1)
    items=[("즉시예약","다른 플랫폼과 겹치지 않으면 켜기 — 켠 숙소가 노출·예약률이 훨씬 높다"),
           ("달력","최소 1박, 최대 730박, 예약 가능 기간 최대로"),
           ("설명","「더보기」 전 위 6줄에 가장 강한 정보, 아래는 길게 — 분쟁 때 근거(흡연 금지 등)"),
           ("사진","커버·첫 5장이 핵심, 캡션은 알고리즘용 — 같은 공간도 좌우·낮밤 다양하게 50장+"),
           ("편의시설","있는데 체크 안 한 게 제일 아깝다 — 서양 게스트용으로 수건을 얼굴·몸 용도별로"),
           ("메시지","응답 횟수·속도도 알고리즘 요소 — 「시간 지정 발송」을 세팅하면 응대 시간이 1/3로 준다"),
           ("언어별 제목","나라마다 어필 포인트가 달라 영어·일본어 따로 — 한국어만 두면 자동 번역돼 어색")]
    rows(d,120,W-240,370,64,[(k,v,300) for k,v in items],size=26,hi=0)
    takeaway(d,"호스트가 할 일 — 다른 플랫폼과 겹치지 않으면 즉시예약부터 켜기")

# 11 title + description
def p11(d):
    header(d,K,"제목은 키워드 명사로, 설명은 중요한 것부터","상호명 대신 강점 키워드 — 게스트는 이름이 아니라 정보로 고른다",page=PAGE0+2)
    col_head(d,120,780,"숙소 이름(제목) 짓기")
    col_head(d,1000,800,"숙소 설명 쓰기 · 원칙")
    divider(d)
    steps=["숙소 강점 5~7가지를 적는다","키워드 명사 중심으로, 잘 보이게","애매한 형용사·외국인이 모를 명사는 삭제",
           "같은 말 반복보다 새 정보를 자세히","상호명 금지 — 「스테이 OO」, 「OO 하우스」"]
    pr=["간결하게","가장 중요한 정보는 맨 위","숙소 모습·경험을 이야기로","숙소만의 특별한 점 강조","현실적으로 소개"]
    rows(d,120,780,420,64,steps,hi=1)
    rows(d,1000,800,420,64,pr)
    y=768
    d.text(120,y,780,36,"영문·한글 제목 따로 세팅",24,"SemiBold",INK)
    d.text(120,y+44,780,36,"리스팅 에디터 → 톱니바퀴(설정) → 언어 → 언어 추가",22,"Regular",INK)
    d.text(120,y+84,780,lines(2,22),"Quiet 2BR house with movie room and home cafe\n영화와 홈카페로 편안히 쉬어가는 조용한 2룸 스테이",22,"Regular",SEC)
    d.text(1000,y,800,36,"AI로 쓰는 법",24,"SemiBold",INK)
    d.text(1000,y+44,800,lines(3,22),"잘 쓴 다른 숙소 설명을 찾아 복사 → GPT·Gemini 등에 예시로 보여 주기 →\n내 숙소 정보를 넣고 「비슷한 형식으로 정리해 줘」 → 마지막 검수 후 업로드",22,"Regular",INK)

# 12 promotion stacking + pricing
def p12(d):
    header(d,K,"같은 날짜엔 할인 하나만, 가격은 주변 평균 요금이 기준","1박마다 우선순위가 가장 높은 할인 하나만 적용된다",page=PAGE0+3)
    col_head(d,120,780,"할인 겹치기 · 우선순위")
    col_head(d,1000,800,"가격은 어떻게")
    divider(d,y1=870)
    pr=["신규 숙소 프로모션","맞춤 할인","숙박 기간별 할인(주간·월간·특정 기간)","조기 예약 할인","막바지 예약 할인"]
    y=rows(d,120,780,420,64,pr)
    note(d,120,y+24,780,"항상 겹쳐 적용 — 시즌별 요금 조정(규칙 조합) · 환불 불가 정책")
    note(d,120,y+64,780,"프로모션이 10% 이상이면 취소선 노출")
    pts=["기준은 비슷한 숙소 가격과 「주변 평균 요금」","\"월세 계산대로 이만큼 받겠다\"는 안 통한다",
         "외국인 지출 중 숙박은 약 10% — 크게 올리기 어렵다","프로모션을 하나도 안 켜면 맨손 전쟁",
         "신규 숙소 프로모션은 리뷰 0개여도 최상위 노출"]
    y=rows(d,1000,800,420,64,pts,hi=0)
    note(d,1000,y+24,800,"비슷한 숙소 = 위치·유형·침대·욕실·후기가 비슷한 곳")
    takeaway(d,"호스트가 할 일 — 주변 평균 요금을 기준으로 잡고, 프로모션은 하나라도 켜기")

# 13 guest contact timeline + reviews
def p13(d):
    header(d,K,"메시지는 여섯 번, 애매한 게스트면 리뷰는 기다렸다가","예약 전 세팅은 미리 끝내고, 메시지는 「시간 지정 발송」으로 — 애매한 게스트면 리뷰는 나중에",page=PAGE0+4)
    steps=[("예약 확정","직후 감사 메시지"),
           ("체크인 1~3일 전","리마인더 · 연락처\n세부 체크인 가이드"),
           ("체크인 당일","오전 환영 메시지\n체크인 방법 재안내\n도움 필요한지 확인"),
           ("체크인 후","첫날 팔로업\n장기 투숙이면 중간 팔로업"),
           ("체크아웃 당일","오전 감사 메시지\n체크아웃 안내"),
           ("체크아웃 1~2일 후","감사 메시지 · 리뷰 요청\n호스트 리뷰 작성")]
    timeline(d,120,360,steps,282)
    col_head(d,120,1680,"리뷰 규칙과 습관",y=620)
    L=["양쪽이 쓰면 즉시, 한쪽만 쓰면 14일 뒤 공개","애매한 게스트면 먼저 쓰지 말고 기다리기","슈퍼호스트는 3개월마다, 게스트 선호는 매일 판정"]
    R=["예약금의 3~5%는 게스트에게(웰컴 간식 등)","짐 보관·얼리 체크인은 들어주며 \"5점 리뷰 부탁드려요\"","약점(반지하·언덕·먼 역)은 예약 때 미리 알리기"]
    rows(d,120,780,690,64,L,hi=1)
    rows(d,1000,800,690,64,R,start=4)
    divider(d,y0=690,y1=882)
    note(d,120,906,1680,"리뷰는 게스트의 권리이지 의무가 아니다 — 5점 리뷰 키워드는 친절·빠른 응답·청결·위치·셀프 체크인")

# 14 checklist
def p14(d):
    header(d,K,"조회수가 떨어지면 14개 영역을 다시 본다","원본 체크리스트 14개 영역 — 굵은 글씨는 체크리스트가 핵심으로 표시한 항목",page=PAGE0+5)
    divider(d,y0=350,y1=808)
    items=[("제목 & 설명","언어 세팅, 키워드 제목, 설명은 AI로",0),
           ("숙소 사진","첫 5장에 강점, 50장 이상, 사진마다 캡션",0),
           ("숙소 유형","숙소 유형, 침대·침구 유형 세팅",0),
           ("편의시설 & 호스트","편의시설 빠짐없이, 호스트 소개",0),
           ("달력","최소 6개월~1년 열기, 최소 숙박 1박",0),
           ("요금","경쟁 숙소 5개와 총액 비교, 플랫폼 간 가격 차 줄이기",1),
           ("프로모션","10% 이상이면 취소선 노출",0),
           ("취소 정책",f"유연한 정책이 유리 — 성수기는 예외 · {PAGE0+6}쪽",1),
           ("리뷰 & 배지","첫 리뷰 3개 빨리, 「게스트 선호」 배지",1),
           ("예약 설정 & 규칙","즉시예약 켜기, 이용 규칙, 예약 전 안내",1),
           ("체크인 가이드","체크인·아웃 시간, 찾아오는 법, 매뉴얼 링크",0),
           ("검색 노출","맞춤 링크, 외부 검색 노출 허용",0),
           ("계정 & 인사이트","전문 호스팅 도구 켜기, 조회수·위시리스트",0),
           ("메시지 & 응답","자동 메시지, 응답 속도, 에어비앤비 메시지로만",1)]
    for i,(t,b,core) in enumerate(items):
        col=i//7; r=i%7
        x=120 if col==0 else 1000; w=780 if col==0 else 800; y=360+r*64
        d.rect(x,y,w,2,LINE)
        d.text(x,y+15,40,34,str(i+1),22,"SemiBold",ACC if i==5 else SEC)
        d.text(x+40,y+15,230,34,t,22,"SemiBold" if core else "Regular",INK)
        d.text(x+270,y+15,w-270,34,b,22,"Regular",INK)
    for x,w in [(120,780),(1000,800)]: d.rect(x,360+7*64,w,2,LINE)
    takeaway(d,"호스트가 할 일 — 조회수가 떨어지면 실적 허브부터 보고 가격·제목·설명·사진을 손본다")

# 15 refund policy + direct link + tools
def p15(d):
    header(d,K,"환불은 날짜별로 걸고, 직접 예약 링크는 시범 중","성수기·이벤트는 엄격하게, 비어 있는 임박 날짜는 유연하게 — 도구는 PC 설정에서 켠다",page=PAGE0+6)
    col_head(d,120,780,"날짜별 환불 정책")
    col_head(d,1000,800,"직접 예약 링크 · 시범")
    divider(d)
    table_head(d,120,420,780,[(0,"정책"),(160,"전액 환불 마감"),(520,"쓸 날짜")])
    pol=[("Flexible",1,"24시간 전","비어 있는 임박 날짜"),("Moderate",5,"5일 전","비수기"),
         ("Limited",14,"14일 전","수요 많은 날짜"),("Firm",30,"30일 전","성수기·대형 이벤트")]
    y=462
    for i,(n,v,vt,use) in enumerate(pol):
        if i: d.rect(120,y,780,2,LINE)
        d.text(120,y+28,150,36,n,24,"Regular",INK)
        bw=max(6,int(180*v/30))
        d.rect(280,y+24,bw,48,GREY_BAR)
        d.text(280+bw+16,y+26,200,40,vt,28,"Bold",INK)
        d.text(640,y+28,260,36,use,22,"Regular",INK)
        y+=96
    d.rect(120,y,780,2,LINE)
    note(d,120,y+24,780,"Limited는 7~14일 전, Firm은 7~30일 전이면 50% 환불")
    bigstat(d,1000,420,800,"15.5% → 10%","호스트가 데려온 게스트의 예약 수수료",hero=False,acc=True)
    note(d,1000,556,800,"에어커버·결제·고객지원 그대로 · 리스팅 에디터에 칸이 보이는 호스트만(대부분 아직 없음)",lines=2)
    tools=[("전문 호스팅 도구","PC 홈페이지 설정 맨 아래에서 켜기"),
           ("실적 허브","주 1회 — 조회수 떨어지면 제목·사진 순서·프로모션"),
           ("날짜별 최소 숙박","비수기만 줄여 노출 늘리기")]
    y=654
    for k,v in tools:
        d.rect(1000,y,800,2,LINE)
        d.text(1000,y+14,800,36,k,24,"SemiBold",INK)
        d.text(1000,y+52,800,34,v,22,"Regular",SEC)
        y+=96
    d.rect(1000,y,800,2,LINE)

# 16 2027 demand calendar
def doy(m,dd): return (datetime.date(2027,m,dd)-datetime.date(2027,1,1)).days
def p16(d):
    header(d,K,"5월 1~5일, 다섯 나라 연휴가 겹친다","2027 수요 달력 — 요금·환불은 이런 날부터 미리 세팅",page=PAGE0+7)
    X0=420; X1=1800; pd=(X1-X0)/365
    xs=lambda m,dd: X0+doy(m,dd)*pd
    top=350; rh=56
    rws=[("1/1",(1,1),(1,1),"한국·미국·중국·일본·대만·홍콩 전부"),
         ("2월 초(4~13일)",(2,4),(2,13),"설 — 한국·중국·대만·홍콩"),
         ("4/3~4/6",(4,3),(4,6),"청명 — 중국·대만·홍콩"),
         ("5/1~5/5",(5,1),(5,5),"노동절·골든위크·어린이날 — 다섯 나라"),
         ("9/14~9/16",(9,14),(9,16),"추석 — 한국·중국·대만"),
         ("10/1~10/11",(10,1),(10,11),"국경절+한글날 — 중국·홍콩·한국·대만"),
         ("12/24~12/31",(12,24),(12,31),"성탄·연말 — 미국·대만·한국 등")]
    g0=top+40; bottom=g0+(len(rws)+1)*rh
    for m in range(1,13):
        x=int(xs(m,1))
        d.rect(x,g0,1,bottom-g0,LINE)
        d.text(x+8,top,90,32,f"{m}월",22,"Regular",MUT)
    for i,(lab,a,b,c) in enumerate(rws):
        y=g0+i*rh; acc=(i==3)
        d.rect(120,y,X1-120,2,INK if i==0 else LINE)
        d.text(120,y+14,290,34,lab,22,"SemiBold" if acc else "Regular",INK)
        x0=xs(*a); bw=max(10,int(xs(*b)+pd-x0))
        d.rect(int(x0),y+14,bw,28,ACC if acc else INK)
        if i in (5,6): d.text(int(x0)-520,y+14,504,34,c,22,"Regular",SEC,just="right")
        else: d.text(int(x0)+bw+12,y+14,640,34,c,22,"Regular",ACC if acc else SEC)
    y=g0+len(rws)*rh
    d.rect(120,y,X1-120,2,LINE)
    d.text(120,y+14,290,34,"대형 공연(1만 석+)",22,"SemiBold",INK)
    for a,b in [((1,9),(1,9)),((1,14),(1,17)),((1,22),(1,24)),((1,27),(1,27)),((2,4),(2,4)),
                ((2,20),(2,21)),((2,26),(2,27)),((5,21),(5,30)),((8,3),(8,8)),((12,2),(12,12))]:
        x0=xs(*a); d.rect(int(x0),y+14,max(5,int(xs(*b)+pd-x0)),28,GREY_BAR)
    for (m,dd),t,right in [((3,3),"1~2월 9건",True),((6,2),"Bruno Mars",True),((8,10),"WYD",True),((12,1),"FANOMENON",False)]:
        x=int(xs(m,dd))
        if right: d.text(x+4,y+14,200,34,t,22,"Regular",SEC)
        else: d.text(x-216,y+14,200,34,t,22,"Regular",SEC,just="right")
    d.rect(120,bottom,X1-120,2,LINE)
    by=bottom+28
    d.text(120,by,780,36,"1월 6건 · 2월 3건",24,"SemiBold",INK)
    note(d,120,by+40,780,"Fujii Kaze · Kenshi Yonezu · NCT WISH · EPIK HIGH · ATEEZ\nMaroon 5 · KATSEYE · CNBLUE · MBN K-POP Music Awards",lines=2)
    d.text(1000,by,800,36,"5월 · 8월 · 12월",24,"SemiBold",INK)
    note(d,1000,by+40,800,"Bruno Mars 5/21~30 중 6일 · 세계청년대회(WYD) 8/3~8\nFANOMENON 2027 12/2~12 주말 6일 · 2026-11-15 기준",lines=2)

run([("09-algorithm",p09),("10-settings",p10),("11-title-desc",p11),("12-promotion",p12),
     ("13-guest-timeline",p13),("14-checklist",p14),("15-hosting-tools",p15),("16-calendar-2027",p16)])
