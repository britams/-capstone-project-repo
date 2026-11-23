import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from PIL import Image, ImageDraw, ImageFont, ImageChops
for f in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc']: fm.fontManager.addfont(f)
plt.rcParams['font.family']='Noto Sans CJK JP'
# 막대 그래프 (승준 11/15 재학습 결과, vision/2026-11-15_VespAI_재학습_결과_승준.md)
fig,ax=plt.subplots(figsize=(6.4,3.6),dpi=300)
labs=['v1: 흰 종이에서\n학습','v2: 떠 있는 격자\n영상 추가','v3: 격자를 얹어\n학습 (최종)']
vals=[32.0,26.1,100.0]; cols=['#b8c2cc','#b8c2cc','#2b6cb0']
b=ax.bar(labs,vals,color=cols,width=0.6)
for r,v,t in zip(b,vals,['312/975','472/1811','917/917']):
    ax.text(r.get_x()+r.get_width()/2,v+2,f'{v:.1f} %\n({t})',ha='center',va='bottom',fontsize=10,color='#1f2a44',weight='bold')
ax.set_ylim(0,128); ax.set_ylabel('격자 너머 말벌을 찾은 장면 (%)',fontsize=9.5)
ax.spines[['top','right']].set_visible(False); ax.tick_params(axis='x',labelsize=9); ax.tick_params(axis='y',labelsize=8.5)
ax.set_title('격자 너머 판별: 우리 표본으로 다시 학습 (YOLOv5s)',fontsize=11,weight='bold',color='#1f2a44',loc='left')
fig.tight_layout(); fig.savefig('chart_v3.png'); plt.close(fig)
AR=31.4/21.4; W=3140; H=int(W/AR)
B='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'; R='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
cad=Image.open('/home/claude/repo/cad/img/D5g_도2_정면.png').convert('RGB'); cad=cad.crop((0,150,cad.width,cad.height-90))
bg=Image.new('RGB',cad.size,'white'); cad=cad.crop(ImageChops.difference(cad,bg).convert('L').point(lambda q:255 if q>12 else 0).getbbox())
img=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(img)
d.text((50,30),'설계·판별 결과',font=ImageFont.truetype(B,96),fill=(31,42,68))
s=min(W*0.28/cad.width,(H-260)/cad.height); cad=cad.resize((int(cad.width*s),int(cad.height*s)))
img.paste(cad,(60,180)); d.text((60,H-75),'D5g 정면 (CAD)',font=ImageFont.truetype(R,50),fill=(110,110,110))
x0=int(W*0.33); ch=Image.open('chart_v3.png'); cw=W-x0-60; ch=ch.resize((cw,int(ch.height*cw/ch.width))); img.paste(ch,(x0,170))
y=170+ch.height+10
for t,c,sz in [('시험: 학습에 안 쓴 표본 2마리 · 격자만 있는 화면의 헛것 2.1 % (17/797)',(40,40,40),54),
               ('학습: VespAI 가중치에서 이어서, 표본 6마리 사진 155장 (v1·v2·v3 시험 영상은 서로 다름)',(110,110,110),46)]:
    d.text((x0,y),t,font=ImageFont.truetype(R,sz),fill=c); y+=sz+30
y+=20
for head,txt in [('CAD 검사','움직이는 부품 28 × 고정 139 새 겹침 0 · 판 끝단 ≥ 1.04 mm'),
                 ('제어 시뮬레이션','문 90/90 · Pi 37/37 · 처리 53/53 통과')]:
    d.text((x0,y),head,font=ImageFont.truetype(B,60),fill=(43,108,176)); y+=78
    d.text((x0+20,y),txt,font=ImageFont.truetype(R,54),fill=(40,40,40)); y+=90
print(y,H); img.save('fig_result.png'); img.resize((1000,681)).save('check3.png')
