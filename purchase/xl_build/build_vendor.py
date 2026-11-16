import sys; sys.path.insert(0, ".")
from items import E1, H, C
from prints import P
from mech import M, X
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
CHK = "열림 확인 11/15 00시 (페이지 제목 일치)"
F = "Arial"
hdr_fill = PatternFill("solid", fgColor="1F4E78"); hdr_font = Font(name=F, bold=True, color="FFFFFF")
thin = Side(style="thin", color="BFBFBF"); bd = Border(left=thin, right=thin, top=thin, bottom=thin)
inp = Font(name=F, color="0000FF"); norm = Font(name=F); link = Font(name=F, color="0563C1", underline="single")

def table(ws, title, note, heads, rows, widths, link_col, money_cols=(), qty_col=None, unit_col=None, sum_col=None):
    ws["A1"] = title; ws["A1"].font = Font(name=F, bold=True, size=14)
    ws["A2"] = note; ws["A2"].font = Font(name=F, italic=True, color="595959")
    r0 = 4
    for j, h in enumerate(heads, 1):
        c = ws.cell(r0, j, h); c.fill = hdr_fill; c.font = hdr_font; c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True); c.border = bd
    for i, row in enumerate(rows):
        r = r0 + 1 + i
        for j, v in enumerate(row, 1):
            c = ws.cell(r, j, v); c.font = norm; c.border = bd; c.alignment = Alignment(vertical="top", wrap_text=True)
            if j == link_col and isinstance(v, str) and v.startswith("http"):
                c.hyperlink = v; c.font = link
            if j in money_cols: c.number_format = '#,##0;(#,##0);"-"'
            if j in (qty_col, unit_col): c.font = inp
        if sum_col:
            c = ws.cell(r, sum_col, "=%s%d*%s%d" % (get_column_letter(qty_col), r, get_column_letter(unit_col), r))
            c.number_format = '#,##0;(#,##0);"-"'; c.font = norm; c.border = bd
    last = r0 + len(rows)
    for j, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = ws.cell(r0 + 1, 1)
    return r0 + 1, last


def vendor_sheet(wb):
    V = [
    ("레이저 — 알루미늄 판 (추천 1)","미스미 meviy (한국미스미)","https://kr.meviy.misumi-ec.com/","3D CAD(STEP)를 올리면 바로 견적·주문. 판금(레이저 절단·굽힘) · 절삭 플레이트 · 샤프트. 미스미코리아 배송이라 Y 봉 맞춤과 같이 받기 좋음","XY·스탬핑 알루미늄 3 mm 판 13장 (print/xy) + 레이저_판 알루미늄 판들 (217·226p·197 등)","가능성 높음 — 한국미스미 공지 11/16 확인, 알루미늄 두께·최소 금액은 견적 화면에서"),
    ("레이저 — 알루미늄·아크릴 (추천 2)","디바이스마트 메이커 견적 (엔티렉스)","https://www.devicemart.co.kr/","DXF를 보내 견적 받는 주문 제작 (기존 엑셀 '주문제작' 시트). 다른 부품과 같은 곳이라 배송 한 번","알루미늄 판 + 아크릴 판 (300pf 아크릴 묶음, 181·199 등)","가능성 높음 — 11/15 엑셀 줄 그대로, 값은 견적"),
    ("레이저 — 금속 판","메이크잇 MakeIT","https://makeit.ai.kr/guide/laser-cutting","도면(STEP·DWG) 올리면 AI 자동 견적 → 제작. 재질 SS400·SUS304·알루미늄. 값은 두께·구멍 수·자재 로스로","알루미늄 판 (meviy·디바이스마트 견적이 비쌀 때 비교)","가능성 높음 — 업체 안내 페이지 11/16 (DXF 업로드·최소 수량은 견적 화면에서)"),
    ("레이저 — 아크릴","올댓프린팅","https://allthatprinting.co.kr/product/%EC%95%84%ED%81%AC%EB%A6%B4-%EB%8B%A8%EC%88%9C-%EC%9E%AC%EB%8B%A8%EC%86%8C-%EA%B9%94%EB%81%94-%EC%BB%A4%ED%8C%85-%EB%A7%88%EA%B0%90/64/category/50/display/1/","아크릴 단순 형태 레이저 재단, 같은 자재 10개부터, PDF 업로드 (DXF는 PDF로 바꿔 올림), 후기에 15일+","아크릴 판 (예비 — 최소 10개라 우리한테는 덜 맞음)","확실 — 상품 페이지 11/16"),
    ("판재 재단 — 사각만","디바이스마트 알루미늄 3T 판재 재단 (가로 × 세로 선택)","https://www.devicemart.co.kr/goods/view?no=14946758","구멍 없는 사각 알루미늄 판을 원하는 크기로 잘라 팜","구멍 없는 판이 생기면 (지금은 해당 없음 — 우리 판은 다 구멍 있음)","가능성 높음 — 검색 결과 제목 11/16"),
    ("3D 프린트 (기본)","학교 3D 프린터","—","서현 11/16: 학교에서 출력. STL 5개 = 바탕화면 '주문제작 파일\\프린트_5개_최종' (300 상자 · 112 · 176 · 111 · 173 깔때기)","출력 5개 전부","확실 — 서현 결정 11/16"),
    ("3D 프린트 출력 대행 (학교 안 될 때)","와이하우스 3DFARM 출력소","https://3dfarm.co.kr/","FDM. PLA·PETG·ABS·TPU 등 60여 종. STL·3MF·OBJ 올리면 가입 없이 자동 견적, 결제 뒤 24시간 안에 출력 시작, 최대 325 × 320 × 325, 전국 택배 (김포)","남은 출력 3개: 300 마킹실 상자 · 112 입구·격리 문 하우징 · 176 방생 문 하우징 → PETG 권장 (물·열)","확실 — 업체 페이지 11/16"),
    ("3D 프린트 출력 대행","부엉이공장 OWL FACTORY","https://owlfactory.co.kr/FDM_auto","FDM 자동 견적 계산기 (STL 20개까지), 흰 PLA 기준, 수원","출력 3개 비교 견적용","확실 — 업체 페이지 11/16"),
    ("3D 프린트 (고급·정밀)","더블에이엠 AAM","https://www.aamkorea.co.kr/3Dprinting","FDM·SLA·SLS·MJF·PolyJet·금속. STEP·STL 보내면 무료 견적. 단품·소량은 어려울 수 있다고 안내 (가산디지털단지)","정밀 표면이 꼭 필요할 때만 (기본은 3DFARM)","확실 — 업체 페이지 11/16"),
    ("PVC 관 맞춤 길이","11번가 수도용 PVC 관 (판매자 재단)","https://www.11st.co.kr/products/7167194115","13A 관을 길이 맞춰 파는 판매자 — 115 · 195 · 49.5 · 40 mm 4토막","통로 관 110·172·174·175s","추측 — 검색 결과만, 상품 페이지 확인 안 함 (주문 때 '맞춤 절단' 옵션 확인)"),
    ("가공 견적 비교 플랫폼","플틱 PLTIK","https://www.pltik.com/","CNC·레이저·워터젯·판금·용접 견적을 여러 업체에 무료로 요청해 비교. 플라스틱·철·스테인리스·알루미늄·황동·목재","알루미늄 판 견적이 한 곳에서 비쌀 때 비교용","가능성 높음 — 업체 첫 화면 11/16 (소량·납기는 견적에서)"),
    ("아크릴 판·관 가공","DKD아크릴 (고양)","https://www.aquaself.net/","아크릴 판·파이프 주문 제작, 레이저 커팅. 도면·손그림·치수만 보내면 24시간 안에 견적. 학교·기관 거래 많음","아크릴 판 (300pf·181·199·220 등) 아크릴몰이 안 될 때","확실 — 업체 첫 화면 11/16"),
    ("아크릴 레이저 (서울, 소량)","홍레이저 (노원 공릉)","https://www.honglaser.co.kr/","아크릴·목재 레이저 커팅·각인, 소량 가능, 카톡·메일 (hong-laser@naver.com) 문의","급할 때 직접 찾아가 받기 (금속은 안 함)","확실 — 업체 첫 화면 11/16"),
    ]
    ws7 = wb.create_sheet("가공업체")
    a7, b7 = table(ws7, "가공 업체 — 레이저·판재·3D 프린트·관 맞춤 (11/16 정리)", "우리 원칙: 서현은 자르기·인두·탭 안 함 → 판·출력은 업체에 맡김. 파일 위치: 바탕화면 '주문제작 파일' (레이저_XY판 · 레이저_판 · 아크릴 DXF · 300 상자 STEP/STL). 값은 모두 업체 견적으로 정함.",
        ["가공 종류", "업체", "링크", "짧은 요약", "우리 부품 (무엇을 맡기나)", "근거 (확인한 날)"], V, [24, 30, 40, 60, 46, 36], 3)
    
    
