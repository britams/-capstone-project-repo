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
# 2 아이디어: 선행 연구 + 마킹 통 → 우리
f,a=fig()
a.text(1,H-1.5,'선행 연구 두 가지를 하나로: 판별 (VespAI) + 고정·표시 (마킹 통)',fontsize=14.5,weight='bold',color=INK)
import matplotlib.image as mpimg
img=mpimg.imread('vespai_v.jpg')
a.imshow(img,extent=(0.8,10.2,5.2,14.6),zorder=1)
a.text(5.5,16.4,'선행① VespAI (2024)',ha='center',fontsize=12,weight='bold',color=INK)
a.text(5.5,3.9,'카메라 AI로 판별까지만\n(표시는 하지 않음)',ha='center',fontsize=11,color='#333',va='center')
a.text(5.5,1.4,'예시 영상: O\'Shea-Wheller 2024, CC BY-NC-SA 4.0',ha='center',fontsize=8.5,color='#666')
def cage(cx,label,actor,col,y0=5.0,sc=0.75):
    from matplotlib.patches import Ellipse
    T=lambda yy: y0+(yy-4.5)*sc
    a.add_patch(Rectangle((cx-3*sc,T(4.5)),6*sc,9.5*sc,fill=False,ec=GRY,lw=2))
    for i in range(7): a.plot([cx-3*sc+i*sc]*2,[T(14),T(14.5)],color=INK,lw=1.5)
    a.plot([cx-3*sc,cx+3*sc],[T(14.25)]*2,color=INK,lw=2)
    a.add_patch(Ellipse((cx,T(13.3)),3.6*sc,1.4*sc,fc='#3b3b3b')); a.add_patch(Ellipse((cx-0.6*sc,T(13.3)),1.2*sc,1.0*sc,fc='#e0a21b'))
    a.add_patch(Rectangle((cx-2.8*sc,T(11.8)),5.6*sc,0.9*sc,fc=col,ec='none')); a.add_patch(Rectangle((cx-0.4*sc,T(4.5)),0.8*sc,7.3*sc,fc=col,ec='none'))
    a.add_patch(FancyArrowPatch((cx+1.6*sc,T(6.5)),(cx+1.6*sc,T(10.8)),arrowstyle='-|>',mutation_scale=16,lw=2.2,color=ACC))
    a.add_patch(Rectangle((cx-0.2*sc,T(14.6)),0.4*sc,1.3*sc,fc='#d9b200'))
    a.text(cx,16.4,label,ha='center',fontsize=12,weight='bold',color=INK)
    a.text(cx,3.9,actor,ha='center',fontsize=11,color='#333',va='center')
cage(15.7,'선행② 여왕벌 마킹 통','손으로 밀어 고정하고\n손으로 표시','#c9c9c9')
cage(26.4,'우리: 자동 마킹 트랩','AI 판별 → 서보가 고정\n→ XY 펜이 표시','#7fb0e0')
a.text(26.4,1.4,'고정 원리 근거: Rojas-Nossa 2022',ha='center',fontsize=8.5,color='#666')
arr(a,10.6,9.6,12.3,9.6); arr(a,19.2,9.6,22.4,9.6,'합침',ty=0.4)
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
