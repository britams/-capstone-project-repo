import re, shutil, zipfile, os
from xml.sax.saxutils import escape as e
SRC='/mnt/user-data/uploads/4d99da49-3._2026____________________________.pptx'
D='build/x'; shutil.rmtree(D,ignore_errors=True); zipfile.ZipFile(SRC).extractall(D)
S=D+'/ppt/slides/slide1.xml'; RL=D+'/ppt/slides/_rels/slide1.xml.rels'
x=open(S,encoding='utf-8').read(); rels=open(RL,encoding='utf-8').read()
def sp_of(name):
    m=[m for m in re.finditer(r'<p:sp>.*?</p:sp>',x,re.S) if f'name="{name}"' in m.group()]; assert len(m)==1,name; return m[0]
def paras(sp): return re.findall(r'<a:p>.*?</a:p>',sp,re.S)
def first_rpr(p): return re.search(r'<a:rPr[^>]*/>|<a:rPr[^>]*>.*?</a:rPr>',p,re.S).group()
def fixfont(rpr):
    rpr=rpr.replace('lang="en-US" altLang="ko-KR"','lang="ko-KR" altLang="en-US"')
    rpr=re.sub(r' spc="-?\d+"','',rpr)
    if '<a:ea ' not in rpr and '<a:latin' in rpr:
        rpr=re.sub(r'(<a:latin [^>]*/>)',r'\1<a:ea typeface="맑은 고딕" panose="020B0503020000020004" pitchFamily="50" charset="-127"/>',rpr,1)
    return rpr
def mkpara(tpl,text):
    ppr=re.search(r'<a:pPr.*?</a:pPr>|<a:pPr[^>]*/>',tpl,re.S); ppr=ppr.group() if ppr else ''
    ppr=ppr.replace('algn="just"','algn="l"')
    rpr=fixfont(first_rpr(tpl))
    return f'<a:p>{ppr}<a:r>{rpr}<a:t>{e(text)}</a:t></a:r></a:p>'
def set_body(name,lines):
    global x
    m=sp_of(name); sp=m.group(); ps=paras(sp)
    new=ps[0]+''.join(mkpara(ps[1],'- '+l) for l in lines)
    body=re.search(r'(<p:txBody>.*?<a:lstStyle/>)(.*)(</p:txBody>)',sp,re.S)
    sp2=sp[:body.start(2)]+new+sp[body.end(2):]
    x=x[:m.start()]+sp2+x[m.end():]
def set_title(name,text):
    global x
    m=sp_of(name); sp=m.group(); ps=paras(sp)
    new=''.join(mkpara(ps[0],t) for t in (text if isinstance(text,list) else [text]))
    body=re.search(r'(<p:txBody>.*?<a:lstStyle/>)(.*)(</p:txBody>)',sp,re.S)
    x=x[:m.start()]+sp[:body.start(2)]+new+sp[body.end(2):]+x[m.end():]
def set_team(name,rows):
    global x
    m=sp_of(name); sp=m.group(); ps=paras(sp); out=''
    for p,(lab,val) in zip(ps,rows):
        ppr=re.search(r'<a:pPr.*?</a:pPr>',p,re.S).group()
        rprs=re.findall(r'<a:rPr[^>]*>.*?</a:rPr>|<a:rPr[^>]*/>',p,re.S)
        rprs=[fixfont(r).replace('sz="4800"','sz="4400"') for r in rprs]   # 11/23 학부까지 넣어 한 줄에 들어가게 48 → 44 pt
        out+=f'<a:p>{ppr}<a:r>{rprs[0]}<a:t>{e(lab)}</a:t></a:r><a:r>{rprs[1]}<a:t>{e("| "+val)}</a:t></a:r></a:p>'
    for p in ps[len(rows):]: out+=re.sub(r'<a:t>[^<]*</a:t>','<a:t></a:t>',p)
    body=re.search(r'(<p:txBody>.*?<a:lstStyle/>)(.*)(</p:txBody>)',sp,re.S)
    x=x[:m.start()]+sp[:body.start(2)]+out+sp[body.end(2):]+x[m.end():]
pid=[200]
def add_pic(name,img,rid):
    global x,rels
    m=sp_of(name); sp=m.group()
    off=re.search(r'<a:off x="(\d+)" y="(\d+)"/><a:ext cx="(\d+)" cy="(\d+)"/>',sp).groups()
    sp2=re.sub(r'<a:t>[^<]*</a:t>','<a:t></a:t>',sp)
    pid[0]+=1
    pic=(f'<p:pic><p:nvPicPr><p:cNvPr id="{pid[0]}" name="그림 {name}"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
         f'<p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
         f'<p:spPr><a:xfrm><a:off x="{off[0]}" y="{off[1]}"/><a:ext cx="{off[2]}" cy="{off[3]}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:ln w="25400"><a:solidFill><a:srgbClr val="2563A8"/></a:solidFill></a:ln></p:spPr></p:pic>')
    x=x[:m.start()]+pic+x[m.end():]   # 양식 사각형은 지우고 그림에 네 변 테두리
    fn=os.path.basename(img); shutil.copy(img,f'{D}/ppt/media/{fn}')
    rels=rels.replace('</Relationships>',f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/{fn}"/></Relationships>')
C=__import__('content'); 
set_title('직사각형 18',C.TITLE)
set_team('직사각형 33',C.TEAM)
for k,v in C.BODY.items(): set_body(k,v)
# 양식 큰 제목도 본문과 같은 글꼴·왼쪽 맞춤, 본문·제목 왼쪽 시작점 통일 (양식은 6.8~8.3 cm로 들쭉날쭉)
def fix_head(name, x_cm):
    global x
    m=sp_of(name); sp=m.group()
    sp=re.sub(r'<a:rPr[^>]*/>|<a:rPr[^>]*>.*?</a:rPr>',lambda r: fixfont(r.group()),sp,flags=re.S).replace('algn="just"','algn="l"')
    sp=re.sub(r'<a:off x="\d+"',f'<a:off x="{int(x_cm*360000)}"',sp,1)
    x=x[:m.start()]+sp+x[m.end():]
for n in ['직사각형 22','직사각형 23']: fix_head(n, 8.2)        # marL 없음
for n in ['직사각형 27','직사각형 41']: fix_head(n, 7.1)        # marL 1.1 cm → 글 시작 8.2
for n in C.BODY: fix_head(n, 7.1)
# 제목 두 줄 (11/23 21:38 서현 새 제목) → 팀 정보와 붙지 않게 제목 상자를 2 cm 올림
mt=sp_of('직사각형 18'); st=re.sub(r'(<a:off x="\d+") y="\d+"',lambda r:f'{r.group(1)} y="{int(5.1*360000)}"',mt.group(),1); x=x[:mt.start()]+st+x[mt.end():]
def em(t):   # 글 폭 어림 (한글 1, 영문·숫자 0.58, 빈칸 0.3, 가운뎃점 0.45) — shortcut: 실제 맑은 고딕 폭 아님, 꺾임이 어긋나면 렌더로 확인
    return sum(1.0 if ord(ch)>0x2E80 else 0.3 if ch==' ' else 0.45 if ch in '·,.' else 0.58 for ch in t)
EM_MAX=25.0; H=[]
# 세로 배치: 양식 위치 대신 실제 줄 수로 위에서부터 같은 간격으로 쌓음 (줄 간격 고정 pt → PowerPoint·LibreOffice 같음)
ORDER=[('h','직사각형 22'),('b','직사각형 20'),('b','직사각형 21'),('h','직사각형 23'),('b','직사각형 35'),('b','직사각형 37'),
       ('h','직사각형 27'),('b','직사각형 42'),('h','직사각형 41'),('b','직사각형 43'),('b','직사각형 44')]
LN={'h':76,'b':58}; GAP={'h':0.2,'b':1.2}; SEC=2.4; y=33.8; prev=None   # pt, cm
for kind,name in ORDER:
    m=sp_of(name); sp=m.group()
    sp=re.sub(r'<a:lnSpc>.*?</a:lnSpc>',f'<a:lnSpc><a:spcPts val="{LN[kind]*100}"/></a:lnSpc>',sp,flags=re.S)
    sp=re.sub(r'<a:spcBef>.*?</a:spcBef>','<a:spcBef><a:spcPts val="0"/></a:spcBef>',sp,flags=re.S)
    sp=re.sub(r'<a:spcAft>.*?</a:spcAft>','<a:spcAft><a:spcPts val="0"/></a:spcAft>',sp,flags=re.S)
    n=sum(max(1,-(-em(t)//EM_MAX)) for t in [''.join(re.findall(r'<a:t>([^<]*)</a:t>',p)) for p in re.findall(r'<a:p>.*?</a:p>',sp,flags=re.S)]) if kind=='b' else len(re.findall(r'<a:p>',sp))
    h=0.254+n*LN[kind]*2.54/72; H.append(h)
    if prev: y+=SEC if kind=='h' else GAP[prev]
    sp=re.sub(r'(<a:off x="\d+") y="\d+"/><a:ext cx="(\d+)" cy="\d+"',lambda r:f'{r.group(1)} y="{int(y*360000)}"/><a:ext cx="{r.group(2)}" cy="{int(h*360000)}"',sp,1)
    x=x[:m.start()]+sp+x[m.end():]; y+=h; prev=kind
print('본문 끝 y =',round(y,1),'cm (로고 131.5 위여야 함)'); assert y<131.0
for i,(k,v) in enumerate(C.PICS.items()): add_pic(k,v,f'rId{50+i}')
x=re.sub(r'<a:rPr(?![^>]*noProof)',r'<a:rPr noProof="1"',x)
open(S,'w',encoding='utf-8').write(x); open(RL,'w',encoding='utf-8').write(rels)
out='build/'+C.OUT
if os.path.exists(out): os.remove(out)
z=zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED)
for root,_,fs in os.walk(D):
    for f in fs:
        p=os.path.join(root,f); z.write(p,os.path.relpath(p,D))
z.close(); print(out)
