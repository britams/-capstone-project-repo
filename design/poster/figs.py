import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch, Circle
fp='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'; fb='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
fm.fontManager.addfont(fp); fm.fontManager.addfont(fb)
plt.rcParams['font.family']='Noto Sans CJK JP'
W,H=31.4,21.4
INK='#1f2a44'; ACC='#2b6cb0'; GRY='#8a8f98'; LIG='#e8f0fa'
def fig():
    f=plt.figure(figsize=(W/2.54*0.5,H/2.54*0.5),dpi=300); a=f.add_axes([0,0,1,1]); a.set_xlim(0,W); a.set_ylim(0,H); a.axis('off'); return f,a
def box(a,x,y,w,h,t,sub=None,hl=False,fs=15):
    a.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0,rounding_size=0.5',fc=LIG if hl else 'white',ec=ACC if hl else GRY,lw=2.5 if hl else 1.6))
    a.text(x+w/2,y+h/2+(0.55 if sub else 0),t,ha='center',va='center',fontsize=fs,weight='bold',color=INK)
    if sub: a.text(x+w/2,y+h/2-0.75,sub,ha='center',va='center',fontsize=fs-4,color='#444')
def arr(a,x1,y1,x2,y2,t=None,tx=0,ty=0.4):
    a.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=18,lw=1.8,color=GRY))
    if t: a.text((x1+x2)/2+tx,(y1+y2)/2+ty,t,ha='center',fontsize=11,color='#444')
# 1 과제 목표: 동작 흐름
f,a=fig()
a.text(1,H-1.6,'한 마리를 사람 손 없이: 가두고 → 가려내고 → 표시하고 → 내보낸다',fontsize=15,weight='bold',color=INK)
bw,bh=6.2,3.0; y1=H-7.2
xs=[1,8.4,15.8,23.2]
box(a,xs[0],y1,bw,bh,'① 들어옴','게이트 → 문 닫힘',fs=14)
box(a,xs[1],y1,bw,bh,'② 가려내기','카메라 AI 판별',fs=14)
box(a,xs[2],y1,bw,bh,'③ 붙잡기','바닥 올려 고정',hl=True,fs=14)
box(a,xs[3],y1,bw,bh,'④ 점 찍기','XY 펜, 가슴에 점',hl=True,fs=14)
for i in range(3): arr(a,xs[i]+bw,y1+bh/2,xs[i+1],y1+bh/2)
y2=y1-6.2
box(a,xs[3],y2,bw,bh,'⑤ 내보냄','문 열림·시각 기록',fs=14)
arr(a,xs[3]+bw/2,y1,xs[3]+bw/2,y2+bh)
box(a,xs[1],y2,bw,bh,'격리','여왕벌·다른 종',fs=14)
arr(a,xs[1]+bw/2,y1,xs[1]+bw/2,y2+bh,'일벌 아님',tx=1.9,ty=0)
box(a,xs[2]-1.0,1.0,bw+8.4,2.6,'다시 잡히면 재포획 시각 기록','왕복 시간 → 둥지까지 거리 범위',fs=14)
arr(a,xs[3]+bw/2,y2,xs[3]+bw/2-1.0,3.6)
f.savefig('fig_goal.png'); plt.close(f)
# 2 아이디어: 여왕벌 마킹 통 → 기계
f,a=fig()
a.text(1,H-1.6,'양봉가의 "여왕벌 마킹 통"을 기계로 바꿨다',fontsize=15,weight='bold',color=INK)
def cage(cx,label,actor,col):
    # tube
    a.add_patch(Rectangle((cx-3,4.5),6,9.5,fill=False,ec=GRY,lw=2))
    # mesh
    for i in range(7): a.plot([cx-3+i,cx-3+i],[14,14.5],color=INK,lw=1.5)
    a.plot([cx-3,cx+3],[14.25,14.25],color=INK,lw=2)
    a.text(cx+3.4,14.2,'격자/망',fontsize=11,color=INK,va='center')
    # wasp (ellipse)
    from matplotlib.patches import Ellipse
    a.add_patch(Ellipse((cx,13.3),3.6,1.4,fc='#3b3b3b')); a.add_patch(Ellipse((cx-0.6,13.3),1.2,1.0,fc='#e0a21b'))
    a.text(cx+3.4,13.0,'말벌',fontsize=11,va='center')
    # plunger
    a.add_patch(Rectangle((cx-2.8,11.8),5.6,0.9,fc=col,ec='none')); a.add_patch(Rectangle((cx-0.4,4.5),0.8,7.3,fc=col,ec='none'))
    a.add_patch(FancyArrowPatch((cx+1.6,6.5),(cx+1.6,10.8),arrowstyle='-|>',mutation_scale=20,lw=2.5,color=ACC))
    a.text(cx,1.9,actor,ha='center',fontsize=12,color='#333')
    a.text(cx,16.6,label,ha='center',fontsize=14,weight='bold',color=INK)
    # pen
    a.add_patch(Rectangle((cx-0.25,15.0),0.5,2.0-0.9,fc='#d9b200'))
cage(7.5,'사람: 마킹 통','손으로 플런저를 밀고\n손으로 물감을 찍음','#c9c9c9')
cage(23,'우리: 승강 바닥 + 투명 격자','직선 서보가 바닥을 올리고\nXY 펜이 격자 구멍으로 점','#7fb0e0')
arr(a,12.3,9.5,17.6,9.5,'자동화',ty=0.5)
a.text(W/2,0.35,'근거: 여왕벌 마킹 통 (양봉 표준 도구) · 말벌 고정에도 사용 (Rojas-Nossa 2022)',ha='center',fontsize=10.5,color='#555')
f.savefig('fig_idea.png'); plt.close(f)
# 3 활용: B2G
f,a=fig()
a.text(1,H-1.6,'공공기관 (B2G)용 조사 장비 — 둥지를 없애는 사람에게 범위를 준다',fontsize=15,weight='bold',color=INK)
yy=H-8
for i,x in enumerate([1,5.6,10.2]):
    box(a,x,yy,4.0,3.0,f'트랩 {i+1}','모듈 장착',fs=13)
box(a,15.3,yy-0.2,7.4,3.4,'재포획 시각','트랩별 왕복 시간',hl=True,fs=14)
for x in [5.0,9.6,14.2]: pass
arr(a,14.2,yy+1.5,15.3,yy+1.5)
box(a,23.6,yy-0.2,7.4,3.4,'방제 기관','둥지 범위 겹침',fs=14)
arr(a,22.7,yy+1.5,23.6,yy+1.5)
box(a,16,2.0,14.6,3.4,'둥지 제거 → 꿀벌 피해 감소','신여왕이 나오기 전 여름~초가을',fs=14)
arr(a,27.3,yy-0.2,27.3,5.4)
a.text(1,4.6,'· 사람이 산 말벌을 잡아\n  표시하는 단계를 기계가 대신',fontsize=12,color='#333',va='center')
a.text(1,1.9,'· 양봉농가는 방제 모드로 사용',fontsize=12,color='#333',va='center')
f.savefig('fig_use.png'); plt.close(f)
