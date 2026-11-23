import re, shutil, zipfile, os
from xml.sax.saxutils import escape as e
D='plan'; shutil.rmtree(D,ignore_errors=True); zipfile.ZipFile('/mnt/user-data/uploads/64046d44-___________.hwpx').extractall(D)
P=D+'/Contents/section0.xml'; x=open(P,encoding='utf-8').read()
def para(t,ppr='1',cpr='11'):
    return f'<hp:p id="0" paraPrIDRef="{ppr}" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="{cpr}"><hp:t>{e(t)}</hp:t></hp:run></hp:p>'
cells=list(re.finditer(r'<hp:tc[ >].*?</hp:tc>',x,re.S))
def fill(i,lines,ppr='1',cpr='11'):
    return (cells[i].start(),cells[i].end(),lines,ppr,cpr)
V={
15:(['YOLO 판별 기반 등검은말벌 자동 마킹·둥지 거리 추정 트랩 — 시판 트랩 장착형 자동 표시 모듈'],'17','12'),
17:(['초벌 — 이서현 (팀장), 이승준'],'1','11'),
19:(['1. 배경: 등검은말벌은 꿀벌을 잡아먹는 외래종으로, 2019년 생태계교란 생물로 지정됨. 양봉 피해를 줄이는 근본 대책은 둥지 제거임. 트랩으로 잡아도 둥지의 여왕벌이 일벌을 계속 생산함.',
     '2. 문제: 둥지를 찾는 첫 단계 (말벌을 잡아 몸에 표시하고 돌아오는 시간을 잼)는 지금 사람이 손으로 함 → 쏘임 위험, 마취·고정에 시간이 걸림 (얼음 마취 10~12분, Kennedy 2018), 기록이 사람마다 다름.',
     '3. 목표: 시판 말벌 트랩에 얹는 모듈로, 들어온 말벌을 한 마리씩 가두고 → YOLO 모델로 종을 판별하고 크기를 재어 여왕벌을 가려낸 뒤 → 일벌만 가슴에 점 마킹을 하고 → 내보내며 시각을 기록하는 일을 사람 손 없이 수행함.',
     '4. 요구 조건: 한 번에 한 마리만 처리, 한 마리 처리 3분 이내, 여왕벌·다른 종은 격리, 12 V 전원 하나, 재료비 지원 범위 (50만 원) 안.',
     '5. 사용자: 둥지를 제거하는 공공기관 (지자체·방제 기관, B2G). 양봉농가는 다 가두는 방제 모드로 사용.']),
21:(['① 문제설정 (S0, 9월) → ② 개념설계: 목적·기능 계통도, 개념설계도 (S1, 10/11) → ③ 진행상황 보고 (10/12) → ④ 재설계: 형광 가루 → 수성 마커, 시판 트랩 레트로핏, "한 마리를 정확히" 원칙 (10/28) → ⑤ 상세설계 D0~D6: 설계변수표, 마킹실·XY·문·빛 게이트·회로 (10월 말~11월)',
     '⑥ 분석: 역학계산 10문제 (11/02 발표), FreeCAD + Python CAD 움직임·간섭 검사, 제어 시뮬레이션 → ⑦ 판별 AI: VespAI 시험 (10/28~11/02) → 우리 표본·격자 조건으로 YOLO 파인 튜닝 (11/15) → ⑧ 부품 구매·가공 (11/17~) → ⑨ 조립·표본 시험 → ⑩ 발표 (12/2 창의융합 판넬, 12/4 앵커 포스터)']),
23:(['• 목표설정·합성: 기능을 가두기·판별·고정·표시·내보내기로 나누고 기구를 고름 — 입구 서보 문 + 적외선 빛 게이트 3쌍, Raspberry Pi 5 카메라 + YOLO 판별, 승강 바닥 (리니어 서보)과 투명 격자판으로 고정 (여왕벌 마킹 통 원리), XY 리드스크루 모터 + 서보 펜 들기, 수성 아크릴 마커.',
     '• 분석: 축 처짐·나사 토크·펜 누름 힘 (0.25~0.34 N) 계산, CAD 움직임·간섭 검사 (움직이는 부품 28 × 고정 139, 새 겹침 0), 판 구멍 끝단 거리 검사, 제어 시뮬레이션 (모터 92/92, 문 90/90, Pi 37/37, 처리 55/55 — 합계 274개 통과).',
     '• 제작·시험·평가: 2020 알루미늄 프레임, 아크릴·알루미늄 판 주문 가공, 3D 프린트 부품, Arduino UNO 2대 제어 + Pi 5 판별, 격자 너머 판별 YOLO 파인 튜닝 v3 (학습에 안 쓴 표본 2마리의 철망 시험 영상에서 917/917 장면 검출, 격자만 화면 헛것 2.1 %), 실물 조립 후 표본 말벌로 동작 시험 예정.']),
25:(['경제성: 재료비 지원 50만 원 안에서 구매·정산. 안전성: 사람이 말벌을 만지지 않음, 12 V 저전압. 신뢰성: 판별 실패 시 표시하지 않고 격리. 생산성: 새 트랩이 아니라 시판 트랩에 얹는 모듈. 법·윤리: 생태계교란 생물의 방사는 생물다양성법상 금지 → 조사 모드는 퇴치 권한이 있는 공공기관 운용을 전제로 하고, 기본은 다 가두는 방제 모드. 환경: 실외 방수·전원은 다음 사양.']),
}
for i in sorted(V,reverse=True):
    v=V[i]; lines,ppr,cpr=(v,'1','11') if isinstance(v,list) else v
    c=cells[i]; s=c.group()
    a=s.index('<hp:subList'); a=s.index('>',a)+1; b=s.index('</hp:subList>')
    s2=s[:a]+''.join(para(t,ppr,cpr) for t in lines)+s[b:]
    x=x[:c.start()]+s2+x[c.end():]
x=x.replace('2024년도 1학기','2026년도 2학기',1).replace('(작성일자 : 2024. 00. 00)','(작성일자 : 2026. 11. 23.)',1)
open(P,'w',encoding='utf-8').write(x)
# Preview 텍스트는 그대로 두어도 됨
out='/home/claude/cf/말벌트랩_설계계획서.hwpx'
if os.path.exists(out): os.remove(out)
z=zipfile.ZipFile(out,'w')
z.write(D+'/mimetype','mimetype',compress_type=zipfile.ZIP_STORED)
for root,_,fs in os.walk(D):
    for f in fs:
        p=os.path.join(root,f); n=os.path.relpath(p,D)
        if n!='mimetype': z.write(p,n,compress_type=zipfile.ZIP_DEFLATED)
z.close(); print(out)
