# 11/17 서현: 1차·2차 나누지 말고 구매 우선순위 순 + 샀음 O/X. 완제품+프로파일 한 시트, 주문제작 따로 (CAP-AI-62)
import sys; sys.path.insert(0, ".")
from items import E1, H
from mech import M
from prints import P
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule
import build_vendor as BV
F = "Arial"
hdr_fill = PatternFill("solid", fgColor="1F4E78"); hdr_font = Font(name=F, bold=True, color="FFFFFF")
thin = Side(style="thin", color="BFBFBF"); bd = Border(left=thin, right=thin, top=thin, bottom=thin)
inp = Font(name=F, color="0000FF"); norm = Font(name=F); link = Font(name=F, color="0563C1", underline="single")
yel = PatternFill("solid", fgColor="FFFF00")
MONEY = '#,##0;(#,##0);"-"'
STAGE = {1: "① 오늘 바로 — 오래 걸리거나 값·납기 확인 필요 (시연에 꼭 필요)",
         2: "② 시연 핵심 — 문·마킹·카메라·전원 (국내 1~4일)",
         3: "③ 프레임·조립 나사 (국내, ②와 같이)",
         4: "④ 나중 — 급이·통로 (교수님 시연에 없어도 됨)",
         5: "⑤ 기타 — 서현 메모 (살거.txt)"}
ALL = list(E1) + list(H) + list(M)
def take(key):
    hit = [x for x in ALL if key in x[1]]
    assert len(hit) == 1, (key, len(hit))
    ALL.remove(hit[0]); return list(hit[0])
def merge(key_keep, key_add, memo):
    a = take(key_keep); b = take(key_add); a[6] = a[6] + b[6]; a[2] = a[2] + " · " + memo; return a
# (단계, 행, 왜 이 순서)
R = []
def add(st, row, why): R.append((st, row, why))
add(1, take("Adafruit 2167"), "입구·방생 문 감지 — 해외 7~10일, 가장 늦게 옴")
add(1, take("ARD200928"), "XY 모터 2개를 돌리는 판 — 해외 약 1주")
add(1, take("ETTINGER"), "캐리지 판 CP ↔ SP (펜이 붙는 곳) — 해외 7~10일 [추측]")
add(1, take("HellermannTyton P 클립"), "마커를 잡는 클립 — 해외 3~5일")
add(1, take("센서 쉴드 V5.0"), "서보·게이트·스위치를 꽂는 판 (납땜 없음) — 1주 이내")
add(1, take("LM-NK1134"), "마커 X·Y 모터 — 주문 제작 4~5일, 반품 불가")
add(1, take("PSFJ8-200"), "X 봉 — 미스미 값·납기 모름 → 품번 넣어 먼저 확인")
add(1, take("Ø8 × 114"), "Y 봉 맞춤 길이 — 미스미 견적 (X 봉과 같이)")
add(1, take("어깨 볼트 M3"), "펜 홀더가 미끄러지는 볼트 — 미스미 견적 (봉과 같이)")
add(1, take("mightyZAP D7-6PT-3"), "바닥을 올려 말벌을 격자에 붙임 (마킹 핵심) — 가장 비쌈")
add(1, take("IR-EW06"), "mightyZAP 선 — 같은 페이지 옵션")
for k, w in (("MG90S", "문 3개 (입구·격리·방생)"), ("카메라 모듈 3", "말벌 찾기·흉부 좌표"), ("FPC 카메라 케이블", "카메라 ↔ Pi"),
             ("DRV8825", "XY 모터 드라이버"), ("12 V 5 A 어댑터", "전원 하나 (비상 정지가 다 끊음)"), ("XL4015", "12 → 5 V · 7.4 V"),
             ("SZH-LC002", "어댑터 → 선"), ("FHAM1", "퓨즈"), ("AUTO-FUSE", "퓨즈"), ("비상 정지", "안전 — 시연 때도"),
             ("와고 221-415", "전원 나누기"), ("MOSFET 4채널", "조명·게이트 송신·펌프 켜고 끄기"), ("리미트 스위치", "X·Y 원점"),
             ("간판용 LED", "카메라 조명"), ("폼 양면테이프", "빛 게이트·와고 붙이기"),
             ("SK8", "X 봉 받침"), ("SC8UU", "빔 베어링"), ("LMK8UU", "Y 캐리지 베어링"), ("금속 M-15mm", "Y 모터판 기둥 (F-25와 이어 40)"), ("금속 F-25mm", "Y 모터판 기둥")):
    add(2, take(k), w)
add(3, take("2020 프로파일"), "프레임 — 맞춤 절단 3~4일 (모든 부품이 여기에 붙음)")
add(3, take("DCB 2025"), "프레임 모서리·이음")
add(3, merge("렌치볼트 M5 × 8", "X 원점 팔", "X 원점 팔 2 포함 (11/17 합침)"), "프레임 볼트")
s1 = take("스프링너트 M5\",") if False else None
sp = [x for x in ALL if x[1].startswith("20시리즈 스프링너트 M5")]
a = sp[0]; b = sp[1]; ALL.remove(a); ALL.remove(b); a = list(a) if a[6] > b[6] else list(b); a[6] = sp[0][6] + sp[1][6]; a[2] += " · 리프트 308s 2 포함 (11/17 합침)"
add(3, a, "프레임 볼트 짝")
m10 = [x for x in ALL if "M5×10" in x[1] or "M5 × 10 (블랙)" in x[1]]
a = list(m10[0]); a[6] = m10[0][6] + m10[1][6]; a[2] = "데크·위판 8 + SK8 8 + 리프트 308s 상자 혀 2 (11/17 합침)"; ALL.remove(m10[0]); ALL.remove(m10[1])
add(3, a, "데크·SK8 볼트")
for k, w in (("[A] 둥근머리", "M2·M3·M4 나사 대부분"), ("[B] 둥근 + 접시", "접시머리 (XY 판)"), ("[C] M3 황동 서포트", "M3 기둥"), ("[D] M2 황동 서포트", "M2 나사·너트"),
             ("M3 × 6 스텐", "짧은 M3"), ("M2.5 × 5", "모터 앞·Pi"), ("LS011", "M5 × 12 (리프트·빔 L)"), ("M3 × 8 둥근머리 태핑", "프린트 부품에 박는 나사"),
             ("M3 평와샤", "리프트 틈"), ("무두볼트", "리프트 로드 끝"), ("금속 M-30mm", "카메라 판 기둥"), ("2.5파이 F-6mm", "Pi 기둥"), ("케이블타이", "선 묶기")):
    add(3, take(k), w)
nut = [x for x in ALL if x[1].startswith("M3 너트")]
a = list(nut[0]); a[6] = nut[0][6] + nut[1][6]; a[2] = nut[1][2] + " · 리프트 304s·309s·홈 + 예비 (11/17 합침)" if nut[1][6] > nut[0][6] else nut[0][2]; ALL.remove(nut[0]); ALL.remove(nut[1])
add(3, a, "M3 너트")
add(4, take("연동 펌프"), "급이 — 트랩 옆 접시 (시연에 없어도 됨)")
add(4, take("실리콘 관"), "급이 관")
take("M3 × 20 둥근머리 볼트")          # 키트 A 안 (0원) — 줄 뺌
pipe = take("아크릴 파이프")           # 주문제작 시트로
assert not ALL, [x[1] for x in ALL]
add(5, ["기타", "알콜", "살거.txt (서현 메모) — 표본 다루기", "(아무 곳)", "", "", 1, 0, "—", "가능", "값 모름 — 넣을 것"], "서현 메모")
add(5, ["기타", "핀셋", "살거.txt (서현 메모) — 표본 집기. 공구라 정산 안 될 수 있음 [가능성 높음 — 정산규칙 '공구 불인정']", "(아무 곳)", "", "", 1, 0, "—", "자비", "값 모름 — 넣을 것"], "서현 메모")

wb = Workbook()
def head(ws, title, note, heads, widths):
    ws["A1"] = title; ws["A1"].font = Font(name=F, bold=True, size=14)
    ws["A2"] = note; ws["A2"].font = Font(name=F, italic=True, color="595959")
    for j, h in enumerate(heads, 1):
        c = ws.cell(4, j, h); c.fill = hdr_fill; c.font = hdr_font; c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True); c.border = bd
    for j, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = "D5"
def ox(ws, col, r1, r2, ncol):
    dv = DataValidation(type="list", formula1='"O,X"', allow_blank=True); dv.add("%s%d:%s%d" % (col, r1, col, r2)); ws.add_data_validation(dv)
    rng = "A%d:%s%d" % (r1, get_column_letter(ncol), r2)
    ws.conditional_formatting.add(rng, FormulaRule(formula=['$%s%d="O"' % (col, r1)], fill=PatternFill("solid", fgColor="C6EFCE"), font=Font(name=F, color="808080")))
def stage_band(ws, r, ncol, text):
    ws.cell(r, 1, text).font = Font(name=F, bold=True, color="1F4E78")
    for j in range(1, ncol + 1): ws.cell(r, j).fill = PatternFill("solid", fgColor="DDEBF7")

# ---------- 구매목록 ----------
ws = wb.active; ws.title = "구매목록"
H1 = ["순위", "샀음 (O/X)", "왜 이 순서", "구분", "품목", "규격·메모 (어디에)", "판매처", "상품번호", "링크", "개수", "단가 (원, 부가세 포함)", "금액 (원)", "준비 기간", "정산", "값 근거", "단계"]
head(ws, "구매목록 — 완제품 + 알루미늄 프로파일 (구매 우선순위 순, 11/17)",
     "B열에 O를 넣으면 산 것 (줄이 초록·회색). 순서 = 교수님 시연 (말벌 들어옴 → 문 닫힘 → 마킹 → 방생 문 열림) 에 필요한 것 + 늦게 오는 것 먼저. 파란 글씨 = 바꿔도 되는 값. 아이씨뱅큐 값은 부가세 별도 × 1.1.",
     H1, [6, 8, 26, 9, 34, 52, 13, 13, 30, 7, 12, 12, 13, 7, 26, 6])
r = 5; n = 0; first = r; stage_rows = {}
for st in sorted(set(s for s, _, _ in R)):
    stage_band(ws, r, len(H1), STAGE[st]); r += 1
    grp = [(row, why) for s, row, why in R if s == st]
    if st in (2, 3):   # 같은 단계 안은 판매처끼리 (장바구니 한 번에)
        order = {"디바이스마트": 0, "아이씨뱅큐": 1}
        grp.sort(key=lambda t: order.get(t[0][3], 2))
    for row, why in grp:
        n += 1
        g, item, memo, shop, no, url, q, u, lead, pay, basis = row[:11]
        vals = [n, "X", why, g, item, memo, shop, no, url, q, u, None, lead, pay, basis, st]
        for j, v in enumerate(vals, 1):
            c = ws.cell(r, j, v); c.font = norm; c.border = bd; c.alignment = Alignment(vertical="top", wrap_text=True)
        ws.cell(r, 2).fill = yel; ws.cell(r, 2).font = Font(name=F, bold=True); ws.cell(r, 2).alignment = Alignment(horizontal="center", vertical="top")
        if isinstance(url, str) and url.startswith("http"): ws.cell(r, 9).hyperlink = url; ws.cell(r, 9).font = link
        for j in (10, 11): ws.cell(r, j).font = inp
        ws.cell(r, 11).number_format = MONEY
        c = ws.cell(r, 12, "=J%d*K%d" % (r, r)); c.number_format = MONEY; c.border = bd; c.font = norm
        r += 1
last = r - 1
ox(ws, "B", first, last, len(H1))
L = "L%d:L%d" % (first, last); Bc = "B%d:B%d" % (first, last)
tot = [("전체 합계", "=SUM(%s)" % L), ("산 것 (O)", '=SUMIFS(%s,%s,"O")' % (L, Bc)), ("아직 안 산 것", "=L%d-L%d" % (r + 1, r + 2)),
       ("그중 자비 (해외 등 — 정산 안 됨)", '=SUMIFS(%s,N%d:N%d,"자비")' % (L, first, last)),
       ("디바이스마트 아직 안 산 것 (66,000원 넘으면 배송비 0)", '=SUMIFS(%s,G%d:G%d,"디바이스마트",%s,"<>O")' % (L, first, last, Bc)),
       ("아이씨뱅큐 아직 안 산 것", '=SUMIFS(%s,G%d:G%d,"아이씨뱅큐",%s,"<>O")' % (L, first, last, Bc))]
for i, (k, f) in enumerate(tot):
    ws.cell(r + 1 + i, 5, k).font = Font(name=F, bold=True)
    c = ws.cell(r + 1 + i, 12, f); c.number_format = "#,##0"; c.font = Font(name=F, bold=True)
BUY_DEMO = "SUMIFS('구매목록'!%s,'구매목록'!P%d:P%d,\"<=3\")" % (L, first, last)
BUY_TOT, BUY_DONE, BUY_SELF = "'구매목록'!L%d" % (r + 1), "'구매목록'!L%d" % (r + 2), "'구매목록'!L%d" % (r + 4)

# ---------- 주문제작 ----------
ws3 = wb.create_sheet("주문제작")
D = r"바탕화면 'capstone design\주문제작 파일\\"
vol = {p[0][:3]: p for p in P}
CR = [
(1, "수요일 견적 — 판 9장이 XY·펜 자리 전부", "금속 레이저 (알루미늄 3T)", "XY 판 9장", D + "레이저_XY판' DXF 9개: YA·YB (M4 접시 6씩) · XN (M2 탭 2) · YM (M3 접시 3) · SP (M3 탭 3) · HV (M3 접시 2) · CP · SV · 217. ⚠ 탭·접시 가공을 해 주는지 꼭 물음 (안 되면 그 6장 설계 바꿈) — 폴더 안 '읽어주세요_탭·접시.txt'", "미스미 meviy 또는 디바이스마트 메이커 견적", "https://kr.meviy.misumi-ec.com/", 1, 50000, "추측 — 견적 받아 바꿀 것"),
(1, "문 3개 판 — 시연 핵심", "금속 레이저 (알루미늄 1.5T)", "문판 3장 112f·170f·176f", D + "레이저_판' 112f_입구문판 · 170f_격리문판 · 176f_방생문판 (알루미늄 1.5T)", "위와 같은 곳 (한 번에)", "https://kr.meviy.misumi-ec.com/", 1, 15000, "추측"),
(1, "비상 정지·드라이버·Pi·X 원점 자리", "금속 레이저 (알루미늄 3·4T)", "기타 판 4장 194b·197·199a 벽·226p", D + "레이저_판' 194b_비상정지판 4T (Ø12·Ø8 구멍은 11/17부터 안 씀 — 그대로 뚫어도 됨) · 197_드라이버받침 3T · 199a_Pi선반벽 3T · 226p_X원점팔 3T", "위와 같은 곳 (한 번에)", "https://kr.meviy.misumi-ec.com/", 1, 15000, "추측"),
(1, "마킹실 — 학교 프린터 (시간 걸림)", "3D 프린트 (학교)", "300 마킹실 상자", D + "프린트_5개_최종\\300_마킹실상자.stl' — 윗면이 아래로 (뒤집어) 출력. 112·176 귀에 M3 × 8 태핑 4", "학교 3D 프린터", "", 1, 0, "학교"),
(1, "입구·격리 문 — 시연 핵심", "3D 프린트 (학교)", "112 입구·격리 문 하우징", D + "프린트_5개_최종\\112_입구격리문하우징.stl' — %g × %g × %g mm, %.1f cm³ · 빛 게이트 G2·G3b 붙는 곳" % (tuple(vol["112"][2]) + (vol["112"][3],)), "학교 3D 프린터", "", 1, 0, "학교"),
(1, "방생 문 — 시연 핵심", "3D 프린트 (학교)", "176 방생 문 하우징", D + "프린트_5개_최종\\176_방생문하우징.stl' — %g × %g × %g mm, %.1f cm³ · 빛 게이트 G5" % (tuple(vol["176"][2]) + (vol["176"][3],)), "학교 3D 프린터", "", 1, 0, "학교"),
(1, "격자판·바닥 원판 — 마킹 핵심", "아크릴 레이저 (투명 2T)", "300pf 묶음 (격자판 2 + 바닥 원판 2)", D + "300pf_아크릴_묶음_100x90_2T.dxf' — 판 100 × 90, 옵션 '도면전달' 고르고 메일로 DXF", "아크릴몰 자유재단", "https://www.acrylmall.com/goods/goods_view.php?goodsNo=25555", 1, 8000, "추측 — 구멍 37개 가공비는 문의"),
(1, "데크·위판 — 전장품·카메라가 붙음", "아크릴 레이저 (5T)", "데크 101 · 위판 105 · 컵받침 220", D + "레이저_데크위판' 101_deck (230 × 180) · 105_top_plate (140 × 180) + '레이저_판' 220_컵받침 (마커 쉬는 컵). 불투명 권장 (카메라 반사). 데크 DXF는 11/17 05시 새로 뽑은 것 (UNO 2 기둥 구멍 3 더) — 그 전 파일 쓰지 말 것", "아크릴몰 자유재단 (5 mm)", "https://www.acrylmall.com/goods/goods_view.php?goodsNo=25555", 1, 16000, "추측"),
(1, "카메라 판·Pi 선반 바닥", "아크릴 레이저 (3T)", "181 카메라판 · 199a Pi 선반 바닥", D + "레이저_판' 181_카메라판_아크릴3T · 199a_Pi선반바닥_아크릴3T", "아크릴몰 자유재단 (3 mm)", "https://www.acrylmall.com/goods/goods_view.php?goodsNo=25555", 1, 5000, "추측"),
(4, "통로 — 시연은 표본을 마킹실에 바로 넣어도 됨", "3D 프린트 (학교)", "111 입구 깔때기", D + "프린트_5개_최종\\111_입구깔때기.stl' — %g × %g × %g mm, %.1f cm³" % (tuple(vol["111"][2]) + (vol["111"][3],)), "학교 3D 프린터", "", 1, 0, "학교"),
(4, "통로 (격리 쪽)", "3D 프린트 (학교)", "173 격리 깔때기", D + "프린트_5개_최종\\173_격리깔때기.stl' — %g × %g × %g mm, %.1f cm³" % (tuple(vol["173"][2]) + (vol["173"][3],)), "학교 3D 프린터", "", 1, 0, "학교"),
(4, "통로 관 — 견적 24시간", "아크릴 관 맞춤 절단", "아크릴 파이프 바깥 18 · 안 14 — 115 · 195 · 49.5 mm", pipe[2], "DKD아크릴", "https://www.aquaself.net/", 1, 9000, "업체 확실, 값은 견적"),
(4, "상용 트랩에 잇는 판 — 표본 시연엔 없어도 됨", "아크릴 레이저 (5T)", "102 칼라 ×3 · 104 돔연결부 ×2", D + "레이저_판' 102_칼라_아크릴5T_x3 · 104_돔연결부_아크릴5T_x2 (데크와 같이 주문하면 배송 한 번)", "아크릴몰 자유재단 (5 mm)", "https://www.acrylmall.com/goods/goods_view.php?goodsNo=25555", 1, 6000, "추측"),
(4, "급이부 있는 판에서만", "3D 프린트 (학교)", "175 방생 T + 설탕물 그릇", D + "프린트_5개_최종\\175_방생T이음_설탕물그릇_급이부있는판만.stl' — 주 설계(D5g_full_no)에는 없음", "학교 3D 프린터", "", 1, 0, "학교"),
(4, "급이부 있는 판에서만", "금속 레이저 (알루미늄 4T)", "144b 펌프 걸이", D + "레이저_판' 144b_펌프걸이_알루미늄4T — 급이부를 트랩 옆에 따로 만들면 안 씀", "금속 레이저 업체", "https://kr.meviy.misumi-ec.com/", 1, 5000, "추측"),
]
H3 = ["순위", "샀음·출력함 (O/X)", "왜 이 순서", "종류", "무엇 (부품)", "파일·어떻게", "업체", "링크", "개수", "어림 (원)", "금액 (원)", "값 근거", "단계"]
head(ws3, "주문제작 — 레이저·3D 프린트·관 맞춤 (구매 우선순위 순, 11/17)",
     "B열에 O = 주문했거나 출력함. 어림값은 [추측] — 견적·자동계산 값으로 바꿀 것 (파란 글씨). 11/17 빛 게이트를 3쌍으로 줄여 199b·199c·199d·199e 받침은 주문 안 함 (폴더 '_옛것_주문안함'으로 옮김).",
     H3, [6, 9, 28, 20, 30, 66, 22, 30, 7, 11, 11, 20, 6])
r = 5; n = 0; first3 = r
for st in sorted(set(x[0] for x in CR)):
    stage_band(ws3, r, len(H3), STAGE[st] if st != 1 else "① 수요일 견적·주문 + 학교 출력 (시연 핵심)"); r += 1
    for x in [x for x in CR if x[0] == st]:
        n += 1
        vals = [n, "X"] + list(x[1:8]) + [x[8], None, x[9], st]
        for j, v in enumerate(vals, 1):
            c = ws3.cell(r, j, v); c.font = norm; c.border = bd; c.alignment = Alignment(vertical="top", wrap_text=True)
        ws3.cell(r, 2).fill = yel; ws3.cell(r, 2).font = Font(name=F, bold=True); ws3.cell(r, 2).alignment = Alignment(horizontal="center", vertical="top")
        if x[6].startswith("http"): ws3.cell(r, 8).hyperlink = x[6]; ws3.cell(r, 8).font = link
        for j in (9, 10): ws3.cell(r, j).font = inp; ws3.cell(r, j).number_format = MONEY
        c = ws3.cell(r, 11, "=I%d*J%d" % (r, r)); c.number_format = MONEY; c.border = bd
        r += 1
last3 = r - 1
ox(ws3, "B", first3, last3, len(H3))
for i, (k, f) in enumerate([("전체 어림", "=SUM(K%d:K%d)" % (first3, last3)), ("주문한 것 (O)", '=SUMIFS(K%d:K%d,B%d:B%d,"O")' % (first3, last3, first3, last3))]):
    ws3.cell(r + 1 + i, 5, k).font = Font(name=F, bold=True); c = ws3.cell(r + 1 + i, 11, f); c.number_format = "#,##0"; c.font = Font(name=F, bold=True)
CUS_DEMO = "SUMIFS('주문제작'!K%d:K%d,'주문제작'!M%d:M%d,1)" % (first3, last3, first3, last3)
CUS_TOT, CUS_DONE = "'주문제작'!K%d" % (r + 1), "'주문제작'!K%d" % (r + 2)

# ---------- 요약 ----------
w0 = wb.create_sheet("요약", 0)
w0["A1"] = "부품 정리 — 말벌 자동 마킹 트랩 (11/17, 구매 우선순위판)"; w0["A1"].font = Font(name=F, bold=True, size=14)
w0["A2"] = "목표: 교수님 시연 — 표본 말벌이 들어오면 입구 문 닫힘 → 마킹 → 방생 문 열림. 산 것은 '구매목록'·'주문제작' 시트 B열에 O."; w0["A2"].font = Font(name=F, italic=True, color="595959")
lines = [("예산 한도 (총, 지원 50만 + 자비)", 1000000, "서현 11/14 '100 안쪽으로'"), ("지원금 한도", 500000, "정산규칙"),
         ("이미 쓴 돈 (정산)", 130010, "purchase/구매장부.md (10/29까지)"),
         ("구매목록 (완제품 + 프로파일)", "=" + BUY_TOT, "시트 구매목록 — 단가 일부 [추측]"),
         ("주문제작 (어림)", "=" + CUS_TOT, "시트 주문제작 — [추측], 견적 받으면 바꿈")]
for j, h in enumerate(["항목", "원", "근거"], 1):
    c = w0.cell(4, j, h); c.fill = hdr_fill; c.font = hdr_font
for i, (k, v, nn) in enumerate(lines):
    rr = 5 + i; w0.cell(rr, 1, k).font = norm
    c = w0.cell(rr, 2, v); c.number_format = "#,##0"; c.font = inp if not str(v).startswith("=") else Font(name=F, color="008000")
    w0.cell(rr, 3, nn).font = Font(name=F, color="595959")
rr = 5 + len(lines)
summ = [("총 어림 (이미 쓴 돈 포함)", "=SUM(B7:B%d)" % (rr - 1)), ("남는 돈 (100만 원 기준)", "=B5-B%d" % rr), ("지원금 넘는 돈 (자비로 낼 돈)", "=MAX(0,B%d-B6)" % rr),
        ("그중 해외라 처음부터 자비인 것", "=" + BUY_SELF), ("지금까지 산 것 (O)", "=%s+%s" % (BUY_DONE, CUS_DONE)), ("아직 살 것", "=B%d-B7-B%d" % (rr, rr + 4)),
        ("시연에 필요한 것만 (구매 ①~③ + 주문제작 ①, 이미 쓴 돈 빼고)", "=%s+%s" % (BUY_DEMO, CUS_DEMO))]
for i, (k, f) in enumerate(summ):
    w0.cell(rr + i, 1, k).font = Font(name=F, bold=True); c = w0.cell(rr + i, 2, f); c.number_format = '#,##0;[Red](#,##0)'; c.font = Font(name=F, bold=True)
t = rr + len(summ) + 1
notes = ["단계 (구매목록·주문제작 공통)"] + [STAGE[k] for k in sorted(STAGE)] + [
 "",
 "할 일 (사람이)",
 "1. 11/18(수) ① 먼저 — 해외·미스미·주문 제작 모터 (늦게 옴). 미스미는 품번 넣어 값·납기 확인",
 "2. ②·③ 디바이스마트·아이씨뱅큐 장바구니 (같은 단계 안은 판매처끼리 모아 둠 — 디바이스마트 66,000원 넘으면 배송비 0)",
 "3. 수요일 레이저 견적: 알루미늄 판 — 탭·접시 가공 되는지 꼭 물음. 학교 프린터로 300·112·176 먼저 출력",
 "4. 받으면 제품 사진 (정산 필수), 영수증 '카드매출전표' 저장, 11/30 정산 서류",
 "5. 받고 확인: LED 모듈 크기·12 V, 리미트 스위치·드라이버 보드 구멍, 키트 안 나사 (M4 접시 12 · M5 × 12), 모터 앞 나사 M2.5, 센서 쉴드 외부 전원 단자·SEL 점퍼, FHAM1 선 달린 꼴",
 "",
 "이미 있어서 안 사는 것: 라즈베리파이 5 · 27 W USB-C 전원 · 아두이노 UNO 2 · 브레드보드·듀폰 점퍼선 · microSD (inventory/ 목록)",
 "11/17 바뀜: 빛 게이트 5 → 3쌍 (+예비 1), 어댑터 12 V 5 A 하나 (비상 정지가 전부 끊음), 강압 XL4015 2 (MT3608 납땜 대신), 퓨즈 FHAM1 + 잭 변환 (판 납땜 대신), 센서 쉴드 V5 2 (납땜 허브 대신), 해외 기둥·와고 받침 → 국내·테이프"]
for i, s in enumerate(notes):
    w0.cell(t + i, 1, s).font = Font(name=F, bold=(s in ("단계 (구매목록·주문제작 공통)", "할 일 (사람이)")))
w0.column_dimensions["A"].width = 60; w0.column_dimensions["B"].width = 14; w0.column_dimensions["C"].width = 50

BV.vendor_sheet(wb)
import sys as _s
out = _s.argv[1] if len(_s.argv) > 1 else "/mnt/user-data/outputs/부품정리_2026-11-17.xlsx"
wb.save(out); print("saved", out, "rows", len(R), len(CR))
