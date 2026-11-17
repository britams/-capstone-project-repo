# -*- coding: utf-8 -*-
"""부품정리 엑셀 갈아엎기 (서현 11/18 01시, CAP-AI-62)
 - 1차·2차·단계 띠 없음 → 구매 우선순위 한 줄 (교수님 시연: 표본 말벌 들어옴 → 입구 문 닫힘 → 마킹 → 방생 문 열림). 바뀔 수 있는 것·급하지 않은 것 (급이·통로)은 아래.
 - B열 O/X = 샀음 (O면 줄이 초록·회색).
 - 시트: 읽는 법 · 구매목록 (완제품 + 알루미늄 프로파일) · 주문제작 (부품 파일 하나하나: 재질·두께·크기·파일 이름·레포 위치·바탕화면 위치) · 가공업체
python3 build3.py <out.xlsx>"""
import sys; sys.path.insert(0, ".")
from items import E1, H
from mech import M
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
URG = {"지금": "FCE4D6", "확인 후": "FFF2CC", "나중": "E2EFDA", "메모": "EDEDED"}

ALL = list(E1) + list(H) + list(M)
def take(key):
    hit = [x for x in ALL if key in x[1]]
    assert len(hit) == 1, (key, len(hit))
    ALL.remove(hit[0]); return list(hit[0])
def merge(key_keep, key_add, memo):
    a = take(key_keep); b = take(key_add); a[6] = a[6] + b[6]; a[2] = a[2] + " · " + memo; return a

# ---------- 구매 우선순위 (위에서부터 삼) ----------
R = []          # (급함, 시연에서 하는 일, 행)
def add(u, why, row): R.append((u, why, row))
# 1) 시연에 꼭 필요한데 늦게 오거나 값·납기를 먼저 알아야 하는 것
for k, w in (("Adafruit 2167", "문 앞뒤 말벌 감지 (빛 게이트) — 해외 7~10일, 가장 늦게 옴"),
             ("LM-NK1134", "마커 X·Y 모터 — 주문 제작 4~5일, 반품 불가"),
             ("mightyZAP D7-6PT-3", "바닥을 올려 말벌을 격자에 붙임 (마킹 핵심) — 가장 비쌈"),
             ("IR-EW06", "mightyZAP 선 — 같은 페이지 옵션"),
             ("PSFJ8-200", "X 봉 — 미스미 (봉·볼트·브래킷 한 번에 견적)"),
             ("Ø8 × 114", "Y 봉 맞춤 길이 — 미스미"),
             ("어깨 볼트 M3", "펜 홀더가 미끄러지는 볼트 — 미스미"),
             ("FALCS", "캐리지·Pi 선반 ㄱ자 4 — 미스미 치수 지정"),
             ("ARD200928", "XY 모터 드라이버를 꽂는 판 — 해외 약 1주"),
             ("HellermannTyton P 클립", "마커를 잡는 클립 — 해외 3~5일"),
             ("센서 쉴드 V5.0", "서보·게이트·스위치를 꽂는 판 (납땜 없음) — 1주 이내"),
             ("FPC 카메라 케이블", "카메라 ↔ Pi 500 mm — 엘레파츠 주문상품, 12/01쯤 발송")):
    add("지금", w, take(k))
# 2) 시연 핵심 — 국내 1~4일 (문 → 카메라 → 마킹 XY → 전원)
for k, w in (("MG90S", "문 3개 (입구·격리·방생) 서보"), ("카메라 모듈 3", "말벌 찾기·흉부 좌표"), ("간판용 LED", "카메라 조명"),
             ("MOSFET 4채널", "조명·빛 게이트 송신 켜고 끄기"), ("DRV8825", "XY 모터 드라이버"), ("리미트 스위치", "X·Y 원점"),
             ("SK8", "X 봉 받침"), ("SC8UU", "빔 베어링"), ("LMK8UU", "Y 캐리지 베어링"), ("금속 M-15mm", "Y 모터판 기둥 (F-25와 이어 40)"), ("금속 F-25mm", "Y 모터판 기둥"),
             ("12 V 5 A 어댑터", "전원 하나 (비상 정지가 다 끊음)"), ("XL4015", "12 → 5 V · 7.4 V"), ("SZH-LC002", "어댑터 → 선"), ("FHAM1", "퓨즈 홀더"), ("AUTO-FUSE", "퓨즈"),
             ("비상 정지", "안전 — 시연 때도"), ("와고 221-415", "전원 나누기"), ("UL1007 AWG22 빨강", "전원 줄 (와고·단자, 11/17 배선표)"), ("UL1007 AWG22 검정", "GND 줄"),
             ("폼 양면테이프", "빛 게이트·와고 붙이기")):
    add("지금", w, take(k))
# 3) 프레임·조립 나사 (모든 부품이 여기에 붙음)
add("지금", "프레임 — 맞춤 절단 3~4일", take("2020 프로파일"))
add("지금", "프레임 모서리·이음", take("DCB 2025"))
add("지금", "프레임 볼트", merge("렌치볼트 M5 × 8", "X 원점 팔", "X 원점 팔 2 포함 (11/17 합침)"))
sp = [x for x in ALL if x[1].startswith("20시리즈 스프링너트 M5")]
a = list(sp[0]) if sp[0][6] > sp[1][6] else list(sp[1]); a[6] = sp[0][6] + sp[1][6]; a[2] += " · 리프트 308s 2 포함 (11/17 합침)"; ALL.remove(sp[0]); ALL.remove(sp[1])
add("지금", "프레임 볼트 짝", a)
m10 = [x for x in ALL if "M5×10" in x[1] or "M5 × 10 (블랙)" in x[1]]
a = list(m10[0]); a[6] = m10[0][6] + m10[1][6]; a[2] = "데크·위판 8 + SK8 8 + 리프트 308s 상자 혀 2 (11/17 합침)"; ALL.remove(m10[0]); ALL.remove(m10[1])
add("지금", "데크·SK8 볼트", a)
for k, w in (("[A] 둥근머리", "M2·M3·M4 나사 대부분"), ("[B] 둥근 + 접시", "접시머리 (XY 판)"), ("[C] M3 황동 서포트", "M3 기둥"), ("[D] M2 황동 서포트", "M2 나사·너트"),
             ("M3 × 6 스텐", "짧은 M3"), ("M2.5 × 5", "모터 앞·Pi"), ("LS011", "M5 × 12 (리프트·빔 L)"), ("M3 × 8 둥근머리 태핑", "프린트 부품에 박는 나사"),
             ("M3 평와샤", "리프트 틈"), ("무두볼트", "리프트 로드 끝"), ("금속 M-30mm", "카메라 판 기둥"), ("2.5파이 F-6mm", "Pi 기둥"), ("케이블타이", "선 묶기")):
    add("지금", w, take(k))
nut = [x for x in ALL if x[1].startswith("M3 너트")]
a = list(nut[0]); a[6] = nut[0][6] + nut[1][6]; a[2] = nut[1][2] + " · 리프트 304s·309s·홈 + 예비 (11/17 합침)" if nut[1][6] > nut[0][6] else nut[0][2]; ALL.remove(nut[0]); ALL.remove(nut[1])
add("지금", "M3 너트", a)
# 4) 바뀔 수 있음 — 받은 보드를 보고
add("확인 후", "DRV 전원 안정 — DRV8825 보드에 이미 있으면 안 삼", take("100 µF"))
# 5) 나중 — 급이·통로 (표본 시연엔 없어도 됨)
add("나중", "급이 — 트랩 옆 접시 (표본 시연엔 없어도 됨)", take("연동 펌프"))
add("나중", "급이 관", take("실리콘 관"))
add("나중", "펌프 끌 때 전압 튐 막기 (펌프와 같이)", take("1N5819"))
take("M3 × 20 둥근머리 볼트")              # 키트 A 안 (0원) — 줄 뺌
pipe = take("아크릴 파이프")               # 주문제작 시트로 (관 3개 따로)
assert not ALL, [x[1] for x in ALL]
add("메모", "서현 메모 (살거.txt) — 표본 다루기", ["기타", "알콜", "표본 다루기", "(아무 곳)", "", "", 1, 0, "—", "가능", "값 모름 — 넣을 것"])
add("메모", "서현 메모 (살거.txt) — 표본 집기", ["기타", "핀셋", "표본 집기. 공구라 정산 안 될 수 있음 [가능성 높음 — 정산규칙 '공구 불인정']", "(아무 곳)", "", "", 1, 0, "—", "자비", "값 모름 — 넣을 것"])

# ---------- 주문제작: 부품 파일 하나하나 ----------
DK = "바탕화면 capstone design\\주문제작 파일\\"
MV, MVD = "cad/print/meviy/", DK + "meviy_알루미늄_STEP\\"
AC, ACD = "cad/print/acryl/", DK + "아크릴몰_아크릴_DXF\\"
P3, P3D = "cad/print/3d/", DK + "프린트_5개_최종\\"
MEVIY = "https://kr.meviy.misumi-ec.com/"; ACRYL = "https://www.acrylmall.com/goods/goods_view.php?goodsNo=25555"
# (급함, 시연에서 하는 일, 부품, 가공, 재질·색, 두께, 크기, 개수, 탭·접시·메모, 파일 이름, 레포 위치, 바탕화면 위치, DXF (다른 업체), 업체, 링크, 단가 어림, 값 근거)
def al(u, why, part, t, size, q, extra, fn, dxf, unit):
    return (u, why, part, "레이저 + 판금 (meviy)", "알루미늄 A5052 (표면 처리 없음)", t, size, q, extra, fn, MV + fn, MVD + fn, dxf, "미스미 meviy", MEVIY, unit, "추측 — STEP 올려 견적")
def ac(u, why, part, mat, t, size, q, extra, fn, unit):
    return (u, why, part, "레이저 절단", mat, t, size, q, extra, fn, AC + fn, ACD + fn, "—", "아크릴몰 자유재단", ACRYL, unit, "추측 — 도면전달 견적")
def pr(u, why, part, size, q, extra, fn):
    return (u, why, part, "3D 프린트 (학교)", "PLA (학교 프린터 기본)", "—", size, q, extra, fn, P3 + fn, P3D + fn, "—", "학교 3D 프린터", "", 0, "학교")
X = "cad/print/xy/"; LS = "cad/print/laser/"
CR = [
 al("지금", "X 빔 −y 끝 (SC8UU·Y 봉 끝)", "YA 빔판 A", 3, "30 × 110.5", 1, "M4 접시 6 (구멍표)", "YA_빔판A_A5052_3T.step", X + "YA_빔판A_알루미늄3T_M4접시6_30x110.5.dxf", 5500),
 al("지금", "X 빔 +y 끝", "YB 빔판 B", 3, "30 × 73.5", 1, "M4 접시 6", "YB_빔판B_A5052_3T.step", X + "YB_빔판B_알루미늄3T_M4접시6_30x73.5.dxf", 5500),
 al("지금", "X 리드 너트", "XN X너트판", 3, "28 × 68", 1, "M2 탭 2 — 올린 뒤 '탭' 지정", "XN_X너트판_A5052_3T.step", X + "XN_X너트판_알루미늄3T_M2탭2_28x68.dxf", 5500),
 al("지금", "Y 모터", "YM Y모터판", 3, "43 × 86.5", 1, "M3 접시 3", "YM_Y모터판_A5052_3T.step", X + "YM_Y모터판_알루미늄3T_M3접시3_43x86.5.dxf", 5500),
 al("지금", "X 모터", "217 X모터판", 3, "44 × 59", 1, "", "217_X모터판_A5052_3T.step", X + "217_X모터판_알루미늄3T_44x59.dxf", 5500),
 al("지금", "Y 캐리지 (LMK8UU 2)", "CP 캐리지판", 3, "25 × 99", 1, "", "CP_캐리지판_A5052_3T.step", X + "CP_캐리지판_알루미늄3T_25x99.dxf", 5500),
 al("지금", "펜 홀더 안내", "SP 안내판", 3, "41 × 99", 1, "M3 탭 3 — '탭' 지정 · M3 접시 1 (−x 면)", "SP_안내판_A5052_3T.step", X + "SP_안내판_알루미늄3T_M3탭3_M3접시1_41x99.dxf", 5500),
 al("지금", "펜 서보 SG90", "SV 서보판", 3, "30 × 32.1", 1, "", "SV_서보판_A5052_3T.step", X + "SV_서보판_알루미늄3T_30x32.1.dxf", 5500),
 al("지금", "펜 홀더 (P 클립)", "HV 홀더판", 3, "46 × 52.5", 1, "M3 접시 2", "HV_홀더판_A5052_3T.step", X + "HV_홀더판_알루미늄3T_M3접시2_46x52.5.dxf", 5500),
 al("지금", "비상 정지 스위치", "194b 비상정지판", 4, "94 × 70", 1, "Ø25.5 + 나사 구멍 (Ø12·Ø8은 11/17부터 안 씀 — 그대로 뚫어도 됨)", "194b_비상정지판_A5052_4T.step", LS + "194b_비상정지판_알루미늄4T.dxf", 5000),
 al("지금", "DRV8825 드라이버 보드", "197 드라이버받침", 3, "56 × 68", 1, "", "197_드라이버받침_A5052_3T.step", LS + "197_드라이버받침_알루미늄3T_56x68.dxf", 3500),
 al("지금", "Pi 선반 벽 (FALCS 2)", "199a Pi선반벽", 3, "89 × 63", 1, "", "199a_Pi선반벽_A5052_3T.step", LS + "199a_Pi선반벽_알루미늄3T.dxf", 3500),
 al("지금", "X 원점 스위치", "226p X원점팔", 3, "24 × 108", 1, "", "226p_X원점팔_A5052_3T.step", LS + "226p_X원점팔_알루미늄3T.dxf", 3500),
 pr("지금", "마킹실 (바닥 리프트·격자판이 들어감)", "300 마킹실 상자", "42.3 × 48 × 46", 1, "윗면이 아래로 (뒤집어) 출력. 112·176 귀에 M3 × 8 태핑 4", "300_마킹실상자.stl"),
 pr("지금", "입구·격리 문 (빛 게이트 G2·G3b)", "112 입구·격리 문 하우징", "53.5 × 106.7 × 50", 1, "빔 구멍 Ø3.2, 게이트는 폼 테이프", "112_입구격리문하우징.stl"),
 pr("지금", "방생 문 (빛 게이트 G5)", "176 방생 문 하우징", "30.5 × 68.3 × 25", 1, "출구 소켓 Ø18.3", "176_방생문하우징.stl"),
 ac("지금", "마킹 격자 (카메라가 비쳐 봄)", "300p 격자판", "아크릴 투명", 2, "38 × 38", 2, "네모 구멍 37 — 묶음 파일도 있음 (cad/print/lift/300p2…100x50)", "300p_격자판_투명2T_x2.dxf", 3000),
 ac("지금", "말벌 뒤 흰 배경 (리프트 위)", "300f 바닥 원판", "아크릴 백색 불투명 (무광 있으면 무광)", 2, "Ø32", 2, "Ø3.4 구멍 — 격자판과 한 주문", "300f_바닥원판_백색2T_x2.dxf", 1500),
 ac("지금", "데크 (전장품·트랩이 붙음)", "101 데크", "아크릴 불투명 (색 아무거나)", 5, "230 × 180", 1, "11/17 11시 파일 (그 전 것 쓰지 말 것)", "101_데크_불투명5T_x1.dxf", 7000),
 ac("지금", "위판 (카메라 기둥)", "105 위판", "아크릴 불투명", 5, "140 × 180", 1, "11/17 11시 파일", "105_위판_불투명5T_x1.dxf", 6000),
 ac("지금", "카메라 판 + LED 2", "181 카메라판", "아크릴 불투명", 3, "58 × 80", 1, "11/17 16시 넓힌 것", "181_카메라판_불투명3T_x1.dxf", 2500),
 ac("지금", "Pi 선반 바닥", "199a Pi선반바닥", "아크릴 불투명", 3, "89 × 64", 1, "", "199a_Pi선반바닥_불투명3T_x1.dxf", 2500),
 al("확인 후", "입구 문 판 (서보 혼)", "112f 입구문판", 1.5, "26.7 × 19.3", 1, "⚠ 서보 혼에 붙일 구멍이 도면에 없음 — 붙이는 법 정한 뒤 주문", "112f_입구문판_A5052_1.5T.step", LS + "112f_입구문판_알루미늄1.5T.dxf", 5000),
 al("확인 후", "격리 문 판 (서보 혼)", "170f 격리문판", 1.5, "26.7 × 19.3", 1, "⚠ 위와 같음", "170f_격리문판_A5052_1.5T.step", LS + "170f_격리문판_알루미늄1.5T.dxf", 5000),
 al("확인 후", "방생 문 판 (서보 혼)", "176f 방생문판", 1.5, "26.7 × 19.3", 1, "⚠ 위와 같음", "176f_방생문판_A5052_1.5T.step", LS + "176f_방생문판_알루미늄1.5T.dxf", 5000),
 ac("확인 후", "마커 뚜껑 쉬는 컵 받침", "220 컵받침", "아크릴 불투명", 5, "7.5 × 37.8", 1, "⚠ 하우징에 붙일 M2 구멍이 도면에 없음", "220_컵받침_불투명5T_x1.dxf", 3000),
 pr("나중", "통로 입구 (표본 시연엔 없어도 됨)", "111 입구 깔때기", "61 × 61 × 54", 1, "넓은 끝을 바닥에, 위 소켓에 관 110", "111_입구깔때기.stl"),
 pr("나중", "통로 격리 쪽", "173 격리 깔때기", "51.8 × 51.8 × 44.5", 1, "뒤집어 넓은 끝을 바닥에, 소켓에 관 172", "173_격리깔때기.stl"),
 ("나중", "통로 관 (입구)", "110 입구 관", "아크릴 관 맞춤 절단", "아크릴 투명 관 바깥 18 · 안 14", 2, "길이 115", 1, "파일 없음 — 길이만", "—", "—", "—", "—", "DKD아크릴", "https://www.aquaself.net/", 3000, "업체 확실, 값은 견적"),
 ("나중", "통로 관 (격리)", "172 격리 관", "아크릴 관 맞춤 절단", "아크릴 투명 관 바깥 18 · 안 14", 2, "길이 195", 1, "파일 없음 — 길이만", "—", "—", "—", "—", "DKD아크릴", "https://www.aquaself.net/", 3000, "업체 확실, 값은 견적"),
 ("나중", "통로 관 (방생 — 급이실 177 쓰면 안 삼)", "174 방생 관", "아크릴 관 맞춤 절단", "아크릴 투명 관 바깥 18 · 안 14", 2, "길이 49.5", 1, "파일 없음 — 길이만", "—", "—", "—", "—", "DKD아크릴", "https://www.aquaself.net/", 3000, "업체 확실, 값은 견적"),
 ac("나중", "상용 트랩에 잇는 칼라", "102 칼라", "아크릴 불투명", 5, "Ø100", 3, "3장 겹쳐 M3", "102_칼라_불투명5T_x3.dxf", 1200),
 ac("나중", "상용 트랩 돔 연결", "104 돔연결부", "아크릴 불투명", 5, "Ø90", 2, "2장 겹쳐 M3", "104_돔연결부_불투명5T_x2.dxf", 1200),
 pr("나중", "급이실 (176 출구에 끼움)", "177 급이실", "69 × 30 × 29", 1, "호스 구멍 Ø5.2", "177_급이실.stl"),
 pr("나중", "급이 접시 (씻을 수 있게 서랍)", "177d 접시 서랍", "19.6 × 32.3 × 7.3", 1, "접시 Ø12 × 3", "177d_접시서랍.stl"),
 al("나중", "급이 펌프 걸이", "144b 펌프걸이", 4, "148 × 108", 1, "", "144b_펌프걸이_A5052_4T.step", LS + "144b_펌프걸이_알루미늄4T.dxf", 5000),
]

wb = Workbook()
def head(ws, title, note, heads, widths):
    ws["A1"] = title; ws["A1"].font = Font(name=F, bold=True, size=14)
    ws["A2"] = note; ws["A2"].font = Font(name=F, italic=True, color="595959")
    for j, h in enumerate(heads, 1):
        c = ws.cell(4, j, h); c.fill = hdr_fill; c.font = hdr_font; c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True); c.border = bd
    for j, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = "E5"; ws.auto_filter.ref = "A4:%s4" % get_column_letter(len(heads))
def ox(ws, r1, r2, ncol):
    dv = DataValidation(type="list", formula1='"O,X"', allow_blank=True); dv.add("B%d:B%d" % (r1, r2)); ws.add_data_validation(dv)
    ws.conditional_formatting.add("A%d:%s%d" % (r1, get_column_letter(ncol), r2),
                                  FormulaRule(formula=['$B%d="O"' % r1], fill=PatternFill("solid", fgColor="C6EFCE"), font=Font(name=F, color="808080")))
def put(ws, r, vals):
    for j, v in enumerate(vals, 1):
        c = ws.cell(r, j, v); c.font = norm; c.border = bd; c.alignment = Alignment(vertical="top", wrap_text=True)
    ws.cell(r, 2).fill = yel; ws.cell(r, 2).font = Font(name=F, bold=True); ws.cell(r, 2).alignment = Alignment(horizontal="center", vertical="top")
    ws.cell(r, 3).fill = PatternFill("solid", fgColor=URG[vals[2]]); ws.cell(r, 3).alignment = Alignment(horizontal="center", vertical="top")

# ---------- 구매목록 ----------
ws = wb.active; ws.title = "구매목록"
H1 = ["순위", "샀음 (O/X)", "급함", "시연에서 하는 일 (왜 이 순서)", "구분", "품목", "규격·메모 (어디에)", "판매처", "상품번호", "링크", "개수", "단가 (원, 부가세 포함)", "금액 (원)", "준비 기간", "정산", "값 근거"]
head(ws, "구매목록 — 완제품 + 알루미늄 프로파일 (위에서부터 사는 순서, 11/18)",
     "B열 O = 샀음 (줄이 초록·회색). 급함: 지금 = 교수님 시연 (표본 말벌 들어옴 → 입구 문 닫힘 → 마킹 → 방생 문 열림) / 확인 후 = 받은 부품 보고 / 나중 = 급이·통로 / 메모. 파란 글씨 = 바꿔도 되는 값. 위쪽 = 늦게 오거나 값을 먼저 알아야 하는 것.",
     H1, [6, 8, 8, 30, 9, 34, 50, 13, 13, 28, 7, 12, 12, 13, 7, 26])
r = 5
for n, (u, why, row) in enumerate(R, 1):
    g, item, memo, shop, no, url, q, unit, lead, pay, basis = row[:11]
    put(ws, r, [n, "X", u, why, g, item, memo, shop, no, url, q, unit, None, lead, pay, basis])
    if isinstance(url, str) and url.startswith("http"): ws.cell(r, 10).hyperlink = url; ws.cell(r, 10).font = link
    for j in (11, 12): ws.cell(r, j).font = inp
    ws.cell(r, 12).number_format = MONEY
    c = ws.cell(r, 13, "=K%d*L%d" % (r, r)); c.number_format = MONEY; c.border = bd; c.font = norm
    r += 1
f1, l1 = 5, r - 1
ox(ws, f1, l1, len(H1))
Mc, Bc, Cc = "M%d:M%d" % (f1, l1), "B%d:B%d" % (f1, l1), "C%d:C%d" % (f1, l1)
tot = [("전체 합계", "=SUM(%s)" % Mc), ("산 것 (O)", '=SUMIFS(%s,%s,"O")' % (Mc, Bc)), ("아직 안 산 것", "=M%d-M%d" % (r + 1, r + 2)),
       ("급함 '지금' 중 아직 안 산 것", '=SUMIFS(%s,%s,"지금",%s,"<>O")' % (Mc, Cc, Bc)),
       ("그중 자비 (해외 등 — 정산 안 됨)", '=SUMIFS(%s,O%d:O%d,"자비")' % (Mc, f1, l1)),
       ("디바이스마트 아직 안 산 것 (66,000원 넘으면 배송비 0)", '=SUMIFS(%s,H%d:H%d,"디바이스마트",%s,"<>O")' % (Mc, f1, l1, Bc)),
       ("아이씨뱅큐 아직 안 산 것", '=SUMIFS(%s,H%d:H%d,"아이씨뱅큐",%s,"<>O")' % (Mc, f1, l1, Bc)),
       ("미스미코리아 아직 안 산 것 (견적)", '=SUMIFS(%s,H%d:H%d,"미스미코리아",%s,"<>O")' % (Mc, f1, l1, Bc))]
for i, (k, f) in enumerate(tot):
    ws.cell(r + 1 + i, 6, k).font = Font(name=F, bold=True)
    c = ws.cell(r + 1 + i, 13, f); c.number_format = "#,##0"; c.font = Font(name=F, bold=True)
BUY = dict(tot="'구매목록'!M%d" % (r + 1), done="'구매목록'!M%d" % (r + 2), now="'구매목록'!M%d" % (r + 4), self="'구매목록'!M%d" % (r + 5))

# ---------- 주문제작 ----------
w3 = wb.create_sheet("주문제작")
H3 = ["순위", "주문·출력함 (O/X)", "급함", "시연에서 하는 일", "부품", "가공", "재질·색", "두께 (mm)", "크기 (mm)", "개수", "탭·접시·메모",
      "파일 이름", "파일 위치 — 레포 (GitHub)", "파일 위치 — 바탕화면 (주문할 때)", "DXF (다른 레이저 업체에 맡길 때)", "업체", "링크", "단가 어림 (원)", "금액 (원)", "값 근거"]
head(w3, "주문제작 — 부품 파일 하나하나 (위에서부터 맡기는 순서, 11/18)",
     "B열 O = 주문했거나 출력함. 업체별로 바탕화면 폴더 하나씩: meviy_알루미늄_STEP (STEP 17 + 구멍표_meviy.md) · 아크릴몰_아크릴_DXF (DXF 9) · 프린트_5개_최종 (STL 7) — 폴더마다 읽어주세요.txt. "
     "알루미늄은 meviy에 STEP을 올리고 '탭' 구멍만 지정. 값은 [추측] (파란 글씨) — 견적 받으면 바꿈. ⚠ = 주문 전에 정할 것.",
     H3, [6, 9, 8, 26, 20, 18, 24, 8, 16, 6, 34, 34, 36, 50, 50, 16, 26, 10, 11, 20])
r = 5
for n, x in enumerate(CR, 1):
    (u, why, part, proc, mat, t, size, q, extra, fn, repo, desk, dxf, shop, url, unit, basis) = x
    put(w3, r, [n, "X", u, why, part, proc, mat, t, size, q, extra, fn, repo, desk, dxf, shop, url, unit, None, basis])
    if url.startswith("http"): w3.cell(r, 17).hyperlink = url; w3.cell(r, 17).font = link
    for j in (10, 18): w3.cell(r, j).font = inp
    w3.cell(r, 18).number_format = MONEY
    c = w3.cell(r, 19, "=J%d*R%d" % (r, r)); c.number_format = MONEY; c.border = bd; c.font = norm
    if "⚠" in extra: w3.cell(r, 11).font = Font(name=F, bold=True, color="C00000")
    r += 1
f3, l3 = 5, r - 1
ox(w3, f3, l3, len(H3))
S3, B3, C3 = "S%d:S%d" % (f3, l3), "B%d:B%d" % (f3, l3), "C%d:C%d" % (f3, l3)
t3 = [("전체 어림", "=SUM(%s)" % S3), ("주문한 것 (O)", '=SUMIFS(%s,%s,"O")' % (S3, B3)), ("급함 '지금' 어림", '=SUMIFS(%s,%s,"지금")' % (S3, C3)),
      ("meviy (알루미늄) 어림", '=SUMIFS(%s,P%d:P%d,"미스미 meviy")' % (S3, f3, l3)), ("아크릴몰 어림", '=SUMIFS(%s,P%d:P%d,"아크릴몰 자유재단")' % (S3, f3, l3))]
for i, (k, f) in enumerate(t3):
    w3.cell(r + 1 + i, 5, k).font = Font(name=F, bold=True)
    c = w3.cell(r + 1 + i, 19, f); c.number_format = "#,##0"; c.font = Font(name=F, bold=True)
CUS = dict(tot="'주문제작'!S%d" % (r + 1), done="'주문제작'!S%d" % (r + 2), now="'주문제작'!S%d" % (r + 3))

# ---------- 읽는 법 ----------
w0 = wb.create_sheet("읽는 법", 0)
w0["A1"] = "부품 정리 — 말벌 자동 마킹 트랩 (11/18 새로 짠 판)"; w0["A1"].font = Font(name=F, bold=True, size=14)
w0["A2"] = "목표: 교수님 시연 — 표본 말벌이 들어오면 입구 문 닫힘 → 마킹 → 방생 문 열림 (살아 있는 벌은 안 씀). 위에서부터 사고, 산 것은 B열에 O."
w0["A2"].font = Font(name=F, italic=True, color="595959")
for j, h in enumerate(["항목", "원", "근거"], 1):
    c = w0.cell(4, j, h); c.fill = hdr_fill; c.font = hdr_font
lines = [("예산 한도 (총, 지원 50만 + 자비)", 1000000, "서현 11/14 '100 안쪽으로'"), ("지원금 한도", 500000, "정산규칙"),
         ("이미 쓴 돈 (정산)", 130010, "purchase/구매장부.md (10/29까지)"),
         ("구매목록 (완제품 + 프로파일)", "=" + BUY["tot"], "시트 구매목록 — 단가 일부 [추측]"),
         ("주문제작 (어림)", "=" + CUS["tot"], "시트 주문제작 — [추측], 견적 받으면 바꿈")]
for i, (k, v, nn) in enumerate(lines):
    rr = 5 + i; w0.cell(rr, 1, k).font = norm
    c = w0.cell(rr, 2, v); c.number_format = "#,##0"; c.font = inp if not str(v).startswith("=") else Font(name=F, color="008000")
    w0.cell(rr, 3, nn).font = Font(name=F, color="595959")
rr = 5 + len(lines)
summ = [("총 어림 (이미 쓴 돈 포함)", "=SUM(B7:B%d)" % (rr - 1)), ("남는 돈 (100만 원 기준)", "=B5-B%d" % rr), ("지원금 넘는 돈 (자비로 낼 돈)", "=MAX(0,B%d-B6)" % rr),
        ("그중 해외라 처음부터 자비인 것", "=" + BUY["self"]), ("지금까지 산 것 (O)", "=%s+%s" % (BUY["done"], CUS["done"])),
        ("급함 '지금' 중 아직 안 산 것 (구매목록)", "=" + BUY["now"]), ("급함 '지금' 주문제작 어림", "=" + CUS["now"])]
for i, (k, f) in enumerate(summ):
    w0.cell(rr + i, 1, k).font = Font(name=F, bold=True); c = w0.cell(rr + i, 2, f); c.number_format = '#,##0;[Red](#,##0)'; c.font = Font(name=F, bold=True)
t = rr + len(summ) + 1
notes = ["시트", "· 구매목록 — 완제품 + 알루미늄 프로파일. 위에서부터 사는 순서 (단계 나눔 없음).",
         "· 주문제작 — 업체에 맡기거나 학교에서 출력하는 부품을 파일 하나씩: 재질·두께·크기·개수·탭·접시·파일 이름·레포 위치·바탕화면 위치.",
         "· 가공업체 — 레이저·판재·3D 프린트·관 맞춤 업체 비교.", "",
         "급함 (C열)", "· 지금 — 교수님 시연에 필요. 위쪽일수록 늦게 오거나 값·납기를 먼저 알아야 하는 것 (해외·주문 제작·미스미 견적).",
         "· 확인 후 — 받은 부품을 보고 정함, 또는 도면에 ⚠ (주문 전에 정할 것).", "· 나중 — 급이·통로 (표본 시연엔 없어도 됨).", "· 메모 — 서현 메모 (살거.txt).", "",
         "주문제작 파일 (바탕화면 '주문제작 파일' — 업체별 폴더 하나씩, 레포 cad/print/ 와 같음)",
         "· meviy_알루미늄_STEP — 알루미늄 판 17 STEP + 구멍표_meviy.md (탭·접시·끝단). meviy에 올리고 '탭' 구멍만 지정. (레포 cad/print/meviy)",
         "· 아크릴몰_아크릴_DXF — 아크릴 9 DXF, 파일 이름 = 번호_이름_색두께_x개수. (레포 cad/print/acryl)",
         "· 프린트_5개_최종 — STL 7 (학교 프린터). (레포 cad/print/3d)",
         "· 다른 레이저 업체에 알루미늄을 맡길 때는 DXF (레포 cad/print/xy·laser, 바탕화면 레이저_XY판·레이저_판).", "",
         "할 일 (승준)", "1. 구매목록 위에서부터 — 같은 판매처는 한 장바구니 (디바이스마트 66,000원 넘으면 배송비 0).",
         "2. 미스미코리아 한 번에: X 봉 PSFJ8-200 · Y 봉 Ø8 × 114 · 어깨 볼트 · FALCS 브래킷 (구멍 자리는 품목 칸, 구성 화면 그림 보고 넣음).",
         "3. meviy: STEP 올려 견적 — 주문제작 '확인 후' (문판 3장)은 빼고.", "4. 학교 프린터: 300 → 112 → 176 먼저.",
         "5. 받으면 제품 사진 (정산 필수), 영수증 '카드매출전표' 저장, 11/30 정산 서류.", "",
         "이미 있어서 안 사는 것: 라즈베리파이 5 · 27 W USB-C 전원 · 아두이노 UNO 2 · 브레드보드·듀폰 점퍼선 · microSD · AI 카메라 동봉 케이블 200 mm 2 (짧아서 책상 시험용) (inventory/ 목록)"]
for i, s in enumerate(notes):
    w0.cell(t + i, 1, s).font = Font(name=F, bold=(s in ("시트", "급함 (C열)", "할 일 (승준)") or s.startswith("주문제작 파일")))
w0.column_dimensions["A"].width = 100; w0.column_dimensions["B"].width = 14; w0.column_dimensions["C"].width = 46

BV.vendor_sheet(wb)
out = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/outputs/부품정리_2026-11-18.xlsx"
wb.save(out); print("saved", out, "rows", len(R), len(CR))
