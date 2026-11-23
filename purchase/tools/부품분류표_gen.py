# 부품 분류표 (조립 파트별) HTML 생성 — 승준 11/22. 실행: python3 purchase/tools/부품분류표_gen.py → 같은 폴더 sort.html → 브라우저(Chromium) A4 인쇄로 PDF
import openpyxl, html, pathlib
HERE=pathlib.Path(__file__).resolve().parent
E=html.escape
X=HERE.parent/'부품정리_2026-11-18.xlsx'
wb=openpyxl.load_workbook(X)
B={}
for r in wb['구매목록'].iter_rows(min_row=5,values_only=True):
    if isinstance(r[0],int): B[r[0]]=r
M={}
for r in wb['주문제작'].iter_rows(min_row=5,values_only=True):
    if isinstance(r[0],int): M[r[0]]=r

REC={'아이씨뱅큐':'영수증7','미스미코리아':'영수증8','디바이스마트':'영수증12','엘레파츠':'영수증10',
     'G마켓 (주식회사아리)':'영수증15','SSG':'영수증14','네이버 (이노공구)':'영수증13','삼원자동화':'영수증16',
     '모터뱅크':'11/20 주문','컴퓨존 (네이버페이)':'11/20 주문'}
SHORT_SELLER={'G마켓 (주식회사아리)':'G마켓 아리조명','네이버 (이노공구)':'네이버 이노공구','컴퓨존 (네이버페이)':'컴퓨존','미스미코리아':'미스미'}
# 짧은 이름 + 어디에 (구매목록 순위)
BN={
1:('빛 게이트 Adafruit 2167 (송·수신 한 쌍)','문 앞뒤 말벌 감지 G2·G3b·G5 + 예비 1'),
2:('리니어 스텝모터 LM-NK1134 (스크류 132)','마커 X 215 · Y 209 모터'),
3:('mightyZAP D7-6PT-3 리니어 서보','리프트 301 — 바닥을 올려 말벌을 격자에 붙임'),
4:('mightyZAP 선 IR-EW06 200 mm','mightyZAP 신호·전원 선'),
5:('리니어 샤프트 Ø8 × 200 (PSFJ8-200)','X 봉 213'),
6:('리니어 샤프트 Ø8 × 114 (양 끝 M4 암나사)','Y 봉 207'),
7:('어깨 볼트 SHMSB4-10 (Ø4 × 10, M2.5)','펜 홀더가 미끄러지는 볼트 (SP ↔ HV)'),
8:('L형 판금 브래킷 FALCS','Y 캐리지 · Pi 선반 ㄱ자'),
9:('듀얼 드라이버 보드 ARD200928','DRV8825 2개를 꽂는 판 (197 받침 위)'),
10:('P 클립 14 mm','안 삼 → 3D 프린트 203p 마커클립으로 대신'),
11:('아두이노 센서 쉴드 V5.0','UNO 1·2 위 — 서보·게이트·스위치 꽂기'),
12:('카메라 케이블 500 mm (Waveshare)','카메라 180 ↔ Pi 5'),
13:('MG90S 서보 (금속 기어)','문 서보 112s 입구 · 170s 격리 · 176s 방생'),
14:('라즈베리파이 카메라 모듈 3','카메라 180 — 말벌 찾기'),
15:('12 V LED 3구 모듈 (10개 묶음)','카메라 조명 182 — 2개 + 예비'),
16:('MOSFET 4채널 SZH-AT021','조명 · 펌프 · 게이트 송신 켜고 끄기'),
17:('DRV8825 스텝 드라이버 (방열판)','X · Y 모터 드라이버'),
18:('리미트 스위치 모듈 VLT-SM006','X · Y 원점 226 + 예비 1'),
19:('삼익 SK08 샤프트 서포트','X 봉 받침 218'),
20:('삼익 SC08UU 케이스 유니트','빔 끝 베어링 222'),
21:('LMK8UU 사각 플랜지 부싱','Y 캐리지 베어링 (CP 판)'),
22:('PCB 서포트 금속 M-15 (수-암)','기둥: YM ↔ YA (F-25와 이어 40), 카메라판 ↔ 위판'),
23:('PCB 서포트 금속 F-25 (암-암)','기둥: YM ↔ YA'),
24:('12 V 5 A 어댑터 (프라임디렉트)','전원 전체 — 이것 하나로'),
25:('강압 모듈 XL4015 (전압 표시)','① 12 → 5 V  ② 12 → 7.4 V'),
26:('DC 잭 → 단자 SZH-LC002','어댑터 플러그 → 선 (+ 예비 1)'),
27:('퓨즈 홀더 FHAM1','12 V 줄 퓨즈'),
28:('블레이드 퓨즈 32 V 5 A','FHAM1에 끼움 + 예비'),
29:('비상 정지 KGE-J4R1R 25Φ','비상 정지 194 (194b 판에)'),
30:('와고 221-415 (5핀)','전원 나누기'),
31:('전선 AWG22 빨강 10 m','+ 전원 줄'),
32:('전선 AWG22 검정 10 m','GND 줄'),
33:('3M 폼 양면테이프 18 mm','빛 게이트 · 와고 붙이기'),
34:('2020 프로파일 맞춤 절단 26토막','프레임 100 (610 × 4 · 320 × 21 · 156 × 1)'),
35:('AL 브래킷 DCB 2025','프레임 모서리 · 이음'),
36:('렌치볼트 M5 × 8 (20시리즈)','프레임 볼트'),
37:('스프링너트 M5 (20시리즈)','프레임 볼트 짝 — 홈에 넣음'),
38:('렌치볼트 M5 × 10 (블랙)','데크 · 위판 · SK08 볼트'),
39:('[키트 A] 렌치볼트 + 너트 480개','M2 · M3 · M4 나사 대부분'),
40:('[키트 B] 둥근·접시머리 볼트 샘플','XY 판 접시머리 (M3 · M4)'),
41:('[키트 C] M3 황동 서포트','M3 기둥 (SP ↔ SV, 보드)'),
42:('[키트 D] M2 황동 서포트','M2 나사 (카메라 · SG90)'),
43:('M3 × 6 둥근머리 (낱개)','짧은 M3 — 기둥 고정'),
44:('M2.5 × 5 둥근머리 (낱개)','모터 앞 M2.5 · Pi'),
45:('[키트] 스텐 렌치볼트 M3·M4·M5 + 너트','M5 × 12 — 리프트 · 빔 L'),
46:('M3 × 8 태핑 (PT2-3X8)','3D 프린트 부품에 박는 나사'),
47:('M3 평와셔','리프트 틈 · 어깨 볼트 밑'),
48:('무두볼트 M3·M4 15종 세트','리프트 로드 끝 304s (M3 × 8)'),
49:('PCB 서포트 금속 M-30 (수-암)','카메라판 기둥 (M-15와 이어 45)'),
50:('LCD 서포트 황동 F-6 (2.5파이)','Pi 기둥'),
51:('케이블타이 100 mm','선 묶기 · 임시 고정'),
52:('M3 너트 (니켈)','귀 · 급이 · 리프트'),
53:('전해 콘덴서 25 V 100 µF','DRV 보드 전원 안정 (보드에 있으면 안 씀)'),
54:('연동 펌프 Kamoer NKP 12 V','급이 펌프 144p'),
55:('실리콘 관 안 3 · 바깥 5, 1 m','급이 관 144hf'),
56:('쇼트키 다이오드 1N5819','펌프 끌 때 전압 튐 막기 (1개 씀)'),
57:('알콜','표본 다루기'),
58:('핀셋','표본 집기'),
59:('SG-90 9 g 서보','펜 들기 서보 205'),
60:('M2.5 너트','어깨 볼트 끝 (SP 바깥)'),
61:('카메라 케이블 300 mm (공식)','카메라 케이블 예비'),
62:('NEMA17 팬케이크 23 mm + T8 리드 8 (내써팝)','마커 X · Y 모터 (LM-NK1134 대신, 11/23) — 절단 X 155 · Y 132'),
63:('스프링너트 M4 (20시리즈) + M4 × 8 둥근머리','217 X 모터판 → +x 레일 바깥 면'),
}
MN={1:'X 빔 −y 끝 (SC8UU · Y 봉 끝)',2:'X 빔 +y 끝',3:'X 리드 너트',4:'Y 모터',5:'X 모터',6:'Y 캐리지 (LMK8UU 2)',
7:'펜 홀더 안내',8:'펜 서보 SG-90',9:'펜 홀더 (203p 클립)',10:'비상 정지 스위치',11:'드라이버 보드 받침',12:'Pi 선반 벽',
13:'X 원점 스위치 팔',14:'입구 문',15:'격리 문',16:'방생 문',17:'마킹실 (리프트 · 격자판)',18:'입구 · 격리 문 + 게이트',
19:'방생 문 + 게이트 G5',20:'마킹 격자 (투명)',21:'말벌 뒤 흰 배경',22:'데크 (전장품 · 트랩)',23:'위판 (카메라 기둥)',
24:'카메라 + LED 2',25:'Pi 선반 바닥',26:'통로 입구',27:'통로 격리 쪽',28:'통로 관 (입구)',29:'통로 관 (격리)',
30:'통로 관 (방생)',31:'상용 트랩에 잇는 칼라',32:'상용 트랩 돔 연결',33:'마커 뚜껑 쉬는 컵 받침',34:'급이실',35:'급이 접시',
36:'급이 펌프 걸이',37:'어깨 볼트 머리 쪽 틈 메우기',38:'마커를 HV 판에 잡는 클립',
39:'X 빔 −y 끝 (SC8UU · Y 봉 끝)',40:'X 빔 +y 끝 (−x 혀 깎음)',41:'Y 모터 NEMA17',42:'X T8 너트',43:'펜 서보 SG-90',44:'Y 캐리지 (LMK8UU 2 · Y T8 너트)'}
PETG={39,40,41,42,43}
PRINT3D={17,18,19,26,27,34,35,37,38}
def mstat(i):
    r=M[i]; how=r[5] or ''
    if r[1]=='취소': return ('취소 (11/23) → 플라스틱 39~44','none')
    if i in PETG: return ('학교 프린트 PETG — 아직','wait')
    if i==44: return ('아크릴몰 추가 주문 — 아직','wait')
    if 'meviy' in how:
        return ('주문 · 영수증11 (11/25 도착)','ok') if r[1]=='O' else ('meviy 담당자 견적 대기 (6장)','wait')
    if i in PRINT3D: return ('Craft-Lab 출력 요청 (11/19)','wait')
    if '아크릴몰' in (r[6] or ''): return ('주문 · 영수증9 (아크릴몰)','ok')
    if '관' in how: return ('나중 (아크릴 관 맞춤)','later')
    return (str(r[1]),'')
def bstat(i):
    r=B[i]; s=r[7]
    if i==10: return ('안 삼 → 203p','none')
    if i==51: return ('아직 — 다이소 등','wait')
    if i in (57,58): return ('있음','ok')
    if i==2: return ('12/4·12/11 도착 → NEMA17로 대체 (취소 여부 확인)','none')
    if i==62: return ('내써팝 — 결제 전','wait')
    if i==63: return ('아직 — 디바이스마트 · 공구상','wait')
    if i==24: return ('컴퓨존 11/20 주문','ok')
    if i==12: return ('엘레파츠 · 영수증10 (12/01쯤 발송)','wait')
    if r[1]=='O': return (f'{SHORT_SELLER.get(s,s)} · {REC.get(s,"")}','ok')
    return (str(r[1]),'')
OWN={
'cam':[('라즈베리파이 5 + AI HAT+ (Hailo)','190 — AI 판단 · 지휘','있음 (팀)'),('Pi 5 공식 27 W 어댑터 · 액티브 쿨러','Pi 5 전원 · 열','있음 (10/28 디바이스마트)')],
'pwr':[('아두이노 UNO R3 × 2','191 · 192 — 움직임 · 문 제어','있음 (팀)')],
'frame':[('상용 트랩 「야생 말벌 포획기」 B형 + 유인액 2병','꾀기 · 가두기 (위 · 아래)','있음 (10/10 불로양봉원)')],
'pen':[('샤피 마커 12색 (노랑 씀 + 뚜껑용 1)','201 — 말벌 등에 점','있음 (10/29 쿠팡)')],
'path':[('등검은말벌 액침표본 × 7','시험 · AI 학습','있음 (10/28 하멜른)')],
}
BOX=[
('1','액추부','움직임을 만드는 것 — 모터 · 서보 · 드라이버 · 원점 스위치','C-1',[62,2,17,9,53,3,4,13,59,18],[11],None,'#2b6cb0'),
('2-①','마킹부 ① 말벌 길 · 마킹실','말벌이 지나가는 길 — 문 · 게이트 · 마킹실 · 리프트 바닥','C-2',[1,48],[17,18,19,14,15,16,20,21,26,27,28,29,30],'path','#c05621'),
('2-②','마킹부 ② XY · 펜','펜을 말벌 위로 옮기고 찍는 기구','C-2',[5,6,19,20,21,22,23,7,60,8,10,63],[39,40,41,42,43,44,5,7,9,13,37,38,33,1,2,3,4,6,8],'pen','#dd6b20'),
('3','카메라부','말벌을 보는 눈과 판단하는 컴퓨터','C-3',[14,12,61,15,49,50],[24,25,12],'cam','#2f855a'),
('4','급이부 (나중)','설탕물 주기 — 12/2 표본 시연엔 없어도 됨','C-4',[54,55,56],[34,35,36],None,'#718096'),
('5-①','나머지 ① 프레임 · 데크','2020 프레임과 아크릴 데크 · 위판, 상용 트랩','C-5',[34,35,36,37,38],[22,23,31,32],'frame','#6b46c1'),
('5-②','나머지 ② 전원 · 배선 · 두뇌','어댑터 → 퓨즈 → 비상 정지 → 와고 → 강압, 아두이노','C-5',[24,26,27,28,29,30,25,31,32,16,11,33],[10],'pwr','#b7791f'),
('5-③','나머지 ③ 나사 키트 · 소모품','여러 부분에 같이 쓰는 나사 · 너트 · 공구','C-5',[39,40,41,42,43,44,45,46,47,52,51,57,58],[],None,'#4a5568'),
]
# check every row assigned once
allb=[i for bx in BOX for i in bx[4]]; allm=[i for bx in BOX for i in bx[5]]
assert sorted(allb)==sorted(B), (set(B)-set(allb), [i for i in allb if allb.count(i)>1])
assert sorted(allm)==sorted(M), (set(M)-set(allm), [i for i in allm if allm.count(i)>1])

def chip(t,k): return f'<span class="st {k}">{E(t)}</span>'
def mname(i):
    r=M[i]; return str(r[4])
def mhow(i):
    r=M[i]; how=r[5] or ''
    if i in PETG: return '3D 프린트 PETG 3T'
    if i==44: return '아크릴 3T (2장 묶음)'
    if 'meviy' in how: return f'알루미늄 {r[7]}T (meviy)'
    if i in PRINT3D: return '3D 프린트 PLA'
    if '아크릴몰' in (r[6] or ''): return f'아크릴 {"투명" if "투명" in r[6] else "백색"} {r[7]}T'
    return how
H=[]
H.append('''<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><style>
@page{size:A4;margin:13mm 12mm 14mm 12mm}
body{font-family:"Noto Sans CJK KR","Noto Sans KR",sans-serif;font-size:9.2pt;color:#1a202c;line-height:1.32;margin:0}
h1{font-size:19pt;margin:0 0 2mm} h2{font-size:14pt;margin:0 0 1.5mm;padding:2mm 3mm;color:#fff;border-radius:2mm}
h3{font-size:10.5pt;margin:2.5mm 0 1mm;break-after:avoid}
.grp{break-inside:avoid} tr{break-inside:avoid}
.sub{color:#4a5568;margin:0 0 3mm}
table{border-collapse:collapse;width:100%;margin-bottom:2mm}
th,td{border:0.6pt solid #cbd5e0;padding:0.75mm 1.4mm;vertical-align:top;text-align:left}
th{background:#edf2f7;font-weight:700;font-size:8.8pt}
td.ck{width:5mm;text-align:center;font-size:12pt;line-height:1}
td.n{white-space:nowrap;text-align:right;font-weight:700}
td.code{white-space:nowrap;font-weight:700;color:#2d3748}
.st{display:inline-block;padding:0.2mm 1.5mm;border-radius:1.5mm;font-size:8.2pt;white-space:nowrap}
.st.ok{background:#e6fffa;color:#22543d}.st.wait{background:#fefcbf;color:#744210;font-weight:700}
.st.later{background:#edf2f7;color:#4a5568}.st.none{background:#fed7d7;color:#742a2a}
.box{page-break-before:always}
.flow{display:flex;align-items:center;gap:2mm;margin:2mm 0 4mm;flex-wrap:nowrap}
.flow div.s{border:1pt solid #2b6cb0;border-radius:2mm;padding:2mm 2.5mm;font-size:9.2pt;background:#ebf8ff;flex:1;text-align:center}
.flow div.a{font-size:15pt;color:#2b6cb0}
.note{background:#fffaf0;border-left:3pt solid #dd6b20;padding:2mm 3mm;margin:2mm 0 3mm;font-size:9pt}
.lbls{display:grid;grid-template-columns:1fr 1fr;gap:4mm}
.lbl{border:1.6pt dashed #2d3748;border-radius:3mm;height:58mm;padding:4mm;box-sizing:border-box;display:flex;flex-direction:column;justify-content:center}
.lbl .no{font-size:30pt;font-weight:900;line-height:1}
.lbl .nm{font-size:15pt;font-weight:700;margin-top:2mm}
.lbl .ds{font-size:9pt;color:#4a5568;margin-top:2mm}
.dot{display:inline-block;width:3mm;height:3mm;border-radius:50%;vertical-align:middle;margin-right:1mm}
small{color:#718096}
</style></head><body>''')
# page 1
H.append('<h1>부품 분류표 — 조립 파트별 상자 8개</h1>')
H.append('<p class="sub">말벌 자동 마킹 트랩 · 승준 · 2026-11-22 (11/23 21시 고침 — XY 모터 NEMA17 · 판 6장 플라스틱) · 기준: 「내가 뭐한거지???」 2판 C(부분별 부품) + 부품정리 엑셀 11/23</p>')
H.append('<div class="flow"><div class="s"><b>① 택배 옴</b><br>판매처 · 영수증 번호 확인</div><div class="a">→</div><div class="s"><b>② 맨 뒤 「택배별 찾아보기」</b><br>품목마다 상자 번호</div><div class="a">→</div><div class="s"><b>③ 그 상자에 넣고</b><br>상자 쪽 표에 ☐ 체크</div><div class="a">→</div><div class="s"><b>④ 조립할 때</b><br>상자 하나 = 조립 한 덩어리</div></div>')
H.append('<div class="note"><b>나눈 방법:</b> 「내가 뭐한거지」 C의 5부분(액추부 · 마킹부 · 카메라부 · 급이부 · 나머지)을 그대로 쓰고, 줄이 많은 <b>마킹부는 2상자</b>(말벌 길 / XY·펜), <b>나머지는 3상자</b>(프레임 / 전원 / 나사)로 나눴다. '
         '문 서보(MG90S)·펜 서보(SG-90)는 C처럼 <b>액추부 상자</b>에 둔다 — 조립할 때 문 하우징(2-①) · 펜(2-②) 상자 옆에 꺼내 놓으면 된다. '
         '<b>나사 키트(5-③)</b>는 여러 상자에 같이 쓰니 따로 둔다. 노란 표시 = 아직 안 왔거나 기다리는 것.</div>')
H.append('<table><tr><th style="width:9%">상자</th><th style="width:27%">이름</th><th>들어가는 것</th><th style="width:9%">줄 수</th><th style="width:30%">기다리는 것 (11/23)</th></tr>')
for no,nm,ds,c,bl,ml,ow,col in BOX:
    waits=[BN[i][0].split(' (')[0] for i in bl if bstat(i)[1]=='wait']+[mname(i) for i in ml if mstat(i)[1]=='wait']
    n=len(bl)+len(ml)+len(OWN.get(ow,[]) if ow else [])
    w=', '.join(waits) if waits else '—'
    H.append(f'<tr><td class="code"><span class="dot" style="background:{col}"></span>{no}</td><td><b>{E(nm)}</b><br><small>「내가 뭐한거지」 {c}</small></td><td>{E(ds)}</td><td class="n">{n}</td><td>{E(w)}</td></tr>')
H.append('</table>')
H.append('<p><small>줄 수 = 사는 것 + 주문·출력하는 것 + 이미 있는 것. 개수는 엑셀 값 그대로(예비 포함). 정산·금액은 이 표에 없음 — 엑셀·구매장부 참고. 영수증 원본은 PC 「정산」 폴더.</small></p>')
# boxes
for no,nm,ds,c,bl,ml,ow,col in BOX:
    H.append(f'<div class="box"><h2 style="background:{col}">상자 {no} · {E(nm)}</h2><p class="sub">{E(ds)} — 「내가 뭐한거지」 {c}</p>')
    if bl:
        H.append('<h3>사는 것</h3><table><tr><th></th><th style="width:5%">줄</th><th style="width:34%">품목</th><th style="width:7%">개수</th><th>어디에 쓰나</th><th style="width:25%">어디서 오나 · 상태</th></tr>')
        for i in bl:
            t,k=bstat(i)
            H.append(f'<tr><td class="ck">☐</td><td class="code">{i}</td><td>{E(BN[i][0])}</td><td class="n">{B[i][10]}</td><td>{E(BN[i][1])}</td><td>{chip(t,k)}</td></tr>')
        H.append('</table>')
    if ml:
        H.append('<h3>우리 도면으로 주문 · 출력하는 것</h3><table><tr><th></th><th style="width:21%">부호 · 이름</th><th style="width:7%">개수</th><th style="width:20%">재료</th><th>하는 일</th><th style="width:25%">상태</th></tr>')
        for i in ml:
            t,k=mstat(i)
            H.append(f'<tr><td class="ck">☐</td><td class="code">{E(mname(i))}</td><td class="n">{M[i][9]}</td><td>{E(mhow(i))}</td><td>{E(MN[i])}</td><td>{chip(t,k)}</td></tr>')
        H.append('</table>')
    if ow and ow in OWN:
        H.append('<h3>이미 있는 것 (같은 상자에)</h3><table><tr><th></th><th style="width:40%">품목</th><th>어디에 쓰나</th><th style="width:25%">어디서</th></tr>')
        for a,b2,c2 in OWN[ow]:
            H.append(f'<tr><td class="ck">☐</td><td>{E(a)}</td><td>{E(b2)}</td><td>{chip(c2,"ok")}</td></tr>')
        H.append('</table>')
    H.append('</div>')
# reverse index by delivery
H.append('<div class="box"><h2 style="background:#1a202c">택배별 찾아보기 — 상자를 열면 어디로?</h2><p class="sub">판매처(영수증) 순서. 줄 = 엑셀 구매목록 순위 / 부호 = CAD 부품 이름.</p>')
where={}
for no,nm,ds,c,bl,ml,ow,col in BOX:
    for i in bl: where[('b',i)]=(no,col)
    for i in ml: where[('m',i)]=(no,col)
groups={}
for i in B:
    t,k=bstat(i)
    if i==10: continue
    s=B[i][7]; key=f'{SHORT_SELLER.get(s,s)} ({REC.get(s,"—")})' if s in REC else s
    groups.setdefault(key,[]).append(('b',i))
for i in M:
    r=M[i]; how=r[5] or ''
    if r[1]=='취소': key='미스미 meviy 담당자 견적 6장 — 11/23 주문 취소'
    elif i in PETG: key='학교 3D 프린트 PETG — XY 판 5장 (11/23)'
    elif i==44: key='아크릴몰 — CP 추가 주문 (11/23)'
    elif 'meviy' in how: key='미스미 meviy 알루미늄 판 (영수증11 10장)'
    elif i in PRINT3D: key='학교 Craft-Lab 3D 프린트 (출력 요청 11/19)'
    elif '아크릴몰' in (r[6] or ''): key='아크릴몰 (영수증9)'
    else: key='나중 — DKD아크릴 관 맞춤 절단'
    groups.setdefault(key,[]).append(('m',i))
order=['아이씨뱅큐 (영수증7)','미스미 (영수증8)','아크릴몰 (영수증9)','엘레파츠 (영수증10)','미스미 meviy 알루미늄 판 (영수증11 10장)','디바이스마트 (영수증12)','네이버 이노공구 (영수증13)','SSG (영수증14)','G마켓 아리조명 (영수증15)','삼원자동화 (영수증16)','모터뱅크 (11/20 주문)','컴퓨존 (11/20 주문)','학교 Craft-Lab 3D 프린트 (출력 요청 11/19)']
SN={'1':'액추부','2-①':'말벌 길 · 마킹실','2-②':'XY · 펜','3':'카메라부','4':'급이부','5-①':'프레임 · 데크','5-②':'전원 · 배선','5-③':'나사 · 소모품'}
keys=[k for k in order if k in groups]+[k for k in groups if k not in order]
for k in keys:
    H.append(f'<div class="grp"><h3>{E(k)}</h3><table><tr><th style="width:9%">줄 · 부호</th><th>품목</th><th style="width:7%">개수</th><th style="width:24%">→ 상자</th></tr>')
    for typ,i in groups[k]:
        no,col=where[(typ,i)]
        nm=SN[no]
        if typ=='b': H.append(f'<tr><td class="code">{i}</td><td>{E(BN[i][0])}</td><td class="n">{B[i][10]}</td><td><span class="dot" style="background:{col}"></span><b>{no}</b> {E(nm)}</td></tr>')
        else: H.append(f'<tr><td class="code">{E(mname(i).split(" ")[0])}</td><td>{E(" ".join(mname(i).split(" ")[1:]))} — {E(MN[i])}</td><td class="n">{M[i][9]}</td><td><span class="dot" style="background:{col}"></span><b>{no}</b> {E(nm)}</td></tr>')
    H.append('</table></div>')
H.append('</div>')
# labels
H.append('<div class="box"><h2 style="background:#1a202c">상자 이름표 — 잘라서 붙이기</h2><div class="lbls">')
for no,nm,ds,c,bl,ml,ow,col in BOX:
    H.append(f'<div class="lbl" style="border-color:{col}"><div class="no" style="color:{col}">{no}</div><div class="nm">{E(nm)}</div><div class="ds">{E(ds)}</div></div>')
H.append('</div></div></body></html>')
open(HERE/'sort.html','w').write('\n'.join(H))
print('ok', len(B), len(M))
