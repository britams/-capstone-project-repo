# 아직 안 온 부품 (배송 기다리는 것) HTML — 승준 11/23 21시. 부품분류표_gen.py의 표·상자 나눔을 그대로 씀.
# 실행: python3 purchase/tools/배송대기_gen.py → 같은 폴더 wait.html → Chromium A4 인쇄로 PDF
# 엑셀 '받음 (날짜)' (구매목록 Q · 주문제작 U)이 비어 있고 취소가 아닌 줄만. ★ = 급함 '지금' (12/2 시연에 꼭)
import runpy, pathlib, html
HERE = pathlib.Path(__file__).resolve().parent
g = runpy.run_path(str(HERE / '부품분류표_gen.py'))
B, M, BN, MN, BOX, E = g['B'], g['M'], g['BN'], g['MN'], g['BOX'], html.escape
mstat, bstat, mname, SHORT_SELLER, REC, PETG = g['mstat'], g['bstat'], g['mname'], g['SHORT_SELLER'], g['REC'], g['PETG']
SN = {'1': '액추부', '2-①': '말벌 길', '2-②': 'XY·펜', '3': '카메라부', '4': '급이부', '5-①': '프레임', '5-②': '전원', '5-③': '나사'}
where = {}
for no, nm, ds, c, bl, ml, ow, col in BOX:
    for i in bl: where[('b', i)] = no
    for i in ml: where[('m', i)] = no
NOTE = {
 '내써팝 (네이버 스마트스토어)': '결제 전 — 오늘출발이면 약 2일. 옵션 23mm + TM200 · 듀폰 1M · 스크류 절단 (메모 X 155 · Y 132)',
 '모터뱅크 (11/20 주문)': '12/4 또는 12/11 도착 → 시연 못 맞춤, NEMA17로 대체 — 취소 여부 확인',
 '학교 3D 프린트 PETG — XY 판 5장 (11/23)': 'PETG · 채움 100 % — cad/print/2026-11-23_XY판_프린트_아크릴/',
 '아크릴몰 — CP 추가 주문 (11/23)': '3T 2장 묶음 62 × 105 DXF — 자유재단 페이지 도면전달 (약 5일)',
 '미스미 meviy 알루미늄 판 (영수증11 10장)': '11/25 도착 예정',
 '학교 Craft-Lab 3D 프린트 (출력 요청 11/19)': '11/19 출력 요청 (영어 이름 zip)',
 '엘레파츠 (영수증10)': '주문 상품 — 12/01쯤 발송 (늦으면 예비 300 mm 케이블)',
}
groups = {}
for i in B:
    r = B[i]
    if r[1] in ('취소', '대체') or r[16] or i in (10, 2, 57, 58): continue   # 2는 NEMA17로 대체
    s = r[7]; key = f'{SHORT_SELLER.get(s, s)} ({REC.get(s, "—")})' if s in REC else s
    if i == 62: key = '내써팝 (네이버 스마트스토어)'
    groups.setdefault(key, []).append(('b', i))
for i in M:
    r = M[i]; how = r[5] or ''
    if r[1] == '취소' or (r[20] and r[20] != '미확인'): continue
    if i in PETG: key = '학교 3D 프린트 PETG — XY 판 5장 (11/23)'
    elif i == 44: key = '아크릴몰 — CP 추가 주문 (11/23)'
    elif 'meviy' in how: key = '미스미 meviy 알루미늄 판 (영수증11 10장)' if r[1] == 'O' else '나중 — meviy (주문 전)'
    elif i in g['PRINT3D']: key = '학교 Craft-Lab 3D 프린트 (출력 요청 11/19)'
    elif '아크릴몰' in (r[6] or ''): key = '아크릴몰 (영수증9)'
    else: key = '나중 — 아크릴 관 맞춤 (주문 전)'
    groups.setdefault(key, []).append(('m', i))
first = ['내써팝 (네이버 스마트스토어)', '학교 3D 프린트 PETG — XY 판 5장 (11/23)', '아크릴몰 — CP 추가 주문 (11/23)', '미스미 meviy 알루미늄 판 (영수증11 10장)', '학교 Craft-Lab 3D 프린트 (출력 요청 11/19)']
keys = [k for k in first if k in groups] + [k for k in groups if k not in first and not k.startswith('나중')] + [k for k in groups if k.startswith('나중')]
nb = sum(1 for k in groups for t, _ in groups[k] if t == 'b'); nm_ = sum(1 for k in groups for t, _ in groups[k] if t == 'm')
H = ['''<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><style>
body{font-family:"Noto Sans CJK KR","Noto Sans KR",sans-serif;font-size:9.2pt;color:#1a202c;line-height:1.3;margin:0}
h1{font-size:18pt;margin:0 0 1.5mm} h3{font-size:10.5pt;margin:3mm 0 0.5mm;break-after:avoid} .sub{color:#4a5568;margin:0 0 3mm}
table{border-collapse:collapse;width:100%;margin-bottom:1.5mm} tr{break-inside:avoid} .grp{break-inside:avoid}
th,td{border:0.6pt solid #cbd5e0;padding:0.7mm 1.4mm;vertical-align:top;text-align:left} th{background:#edf2f7;font-size:8.8pt}
td.ck{width:5mm;text-align:center;font-size:12pt;line-height:1} td.n{text-align:right;font-weight:700;white-space:nowrap} td.code{white-space:nowrap;font-weight:700}
.star{color:#c53030;font-weight:900} .nt{color:#4a5568;font-size:8.8pt;margin:0 0 1mm}
</style></head><body>''',
 f'<h1>아직 안 온 것 — 배송 · 출력 기다리는 부품</h1><p class="sub">말벌 자동 마킹 트랩 · 승준 · 2026-11-23 21시 기준 (엑셀 \'받음\' 빈 줄, 취소 뺌) · 사는 것 {nb}줄 + 주문·출력 {nm_}줄 · <span class="star">★</span> = 12/2 시연에 꼭 필요. 11/23 바뀜: XY 모터 → NEMA17 (내써팝), meviy 담당자 견적 6장 취소 → PETG 프린트 5 + 아크릴 CP 1</p>',
 '<table><tr><th style="width:42%">택배 · 주문</th><th style="width:7%">줄 수</th><th>언제 · 할 일</th></tr>']
for k in keys: H.append(f'<tr><td><b>{E(k)}</b></td><td class="n">{len(groups[k])}</td><td>{E(NOTE.get(k, ""))}</td></tr>')
H.append('</table>')
for k in keys:
    H.append(f'<div class="grp"><h3>{E(k)}</h3>' + (f'<p class="nt">{E(NOTE[k])}</p>' if k in NOTE else '') +
             '<table><tr><th></th><th style="width:7%">줄·부호</th><th style="width:40%">품목</th><th style="width:6%">개수</th><th>어디에</th><th style="width:13%">상자</th></tr>')
    for t, i in groups[k]:
        if t == 'b':
            r = B[i]; star = '<span class="star">★</span> ' if r[2] == '지금' else ''
            H.append(f'<tr><td class="ck">☐</td><td class="code">{i}</td><td>{star}{E(BN[i][0])}</td><td class="n">{r[10]}</td><td>{E(BN[i][1])}</td><td>{where[("b", i)]} {SN[where[("b", i)]]}</td></tr>')
        else:
            r = M[i]; star = '<span class="star">★</span> ' if r[2] == '지금' else ''
            nm = mname(i); code = nm.split(' ')[0]
            H.append(f'<tr><td class="ck">☐</td><td class="code">{E(code)}</td><td>{star}{E(" ".join(nm.split(" ")[1:]))}</td><td class="n">{r[9]}</td><td>{E(MN[i])}</td><td>{where[("m", i)]} {SN[where[("m", i)]]}</td></tr>')
    H.append('</table></div>')
H.append('</body></html>')
open(HERE / 'wait.html', 'w').write('\n'.join(H)); print('ok', nb, nm_)
