import re, shutil, zipfile, os
from xml.sax.saxutils import escape as e
import sys; SRC=sys.argv[1]  # 앵커 포스터 양식 pptx (대회 배포 양식 — 레포에 넣지 않음)
D='build/x'; shutil.rmtree(D,ignore_errors=True); zipfile.ZipFile(SRC).extractall(D)
S=D+'/ppt/slides/slide1.xml'; RL=D+'/ppt/slides/_rels/slide1.xml.rels'
x=open(S,encoding='utf-8').read(); rels=open(RL,encoding='utf-8').read()
def sp_of(name):
    m=[m for m in re.finditer(r'<p:sp>.*?</p:sp>',x,re.S) if f'name="{name}"' in m.group()]; assert len(m)==1,name; return m[0]
def paras(sp): return re.findall(r'<a:p>.*?</a:p>',sp,re.S)
def first_rpr(p): return re.search(r'<a:rPr[^>]*/>|<a:rPr[^>]*>.*?</a:rPr>',p,re.S).group()
def mkpara(tpl,text):
    ppr=re.search(r'<a:pPr.*?</a:pPr>|<a:pPr[^>]*/>',tpl,re.S); ppr=ppr.group() if ppr else ''
    rpr=first_rpr(tpl)
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
    new=mkpara(ps[0],text)
    body=re.search(r'(<p:txBody>.*?<a:lstStyle/>)(.*)(</p:txBody>)',sp,re.S)
    x=x[:m.start()]+sp[:body.start(2)]+new+sp[body.end(2):]+x[m.end():]
def set_team(name,rows):
    global x
    m=sp_of(name); sp=m.group(); ps=paras(sp); out=''
    for p,(lab,val) in zip(ps,rows):
        ppr=re.search(r'<a:pPr.*?</a:pPr>',p,re.S).group()
        rprs=re.findall(r'<a:rPr[^>]*>.*?</a:rPr>|<a:rPr[^>]*/>',p,re.S)
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
         f'<p:spPr><a:xfrm><a:off x="{off[0]}" y="{off[1]}"/><a:ext cx="{off[2]}" cy="{off[3]}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>')
    x=x[:m.start()]+sp2+pic+x[m.end():]
    fn=os.path.basename(img); shutil.copy(img,f'{D}/ppt/media/{fn}')
    rels=rels.replace('</Relationships>',f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/{fn}"/></Relationships>')
C=__import__('content'); 
set_title('직사각형 18',C.TITLE)
set_team('직사각형 33',C.TEAM)
for k,v in C.BODY.items(): set_body(k,v)
for i,(k,v) in enumerate(C.PICS.items()): add_pic(k,v,f'rId{50+i}')
open(S,'w',encoding='utf-8').write(x); open(RL,'w',encoding='utf-8').write(rels)
out='build/'+C.OUT
if os.path.exists(out): os.remove(out)
z=zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED)
for root,_,fs in os.walk(D):
    for f in fs:
        p=os.path.join(root,f); z.write(p,os.path.relpath(p,D))
z.close(); print(out)
