import re, shutil, zipfile, os, sys
from xml.sax.saxutils import escape as e
from PIL import Image
SRC=sys.argv[1]; OUT=sys.argv[2]
D='build/panel'; shutil.rmtree(D,ignore_errors=True); zipfile.ZipFile(SRC).extractall(D)
S=D+'/ppt/slides/slide1.xml'; RL=D+'/ppt/slides/_rels/slide1.xml.rels'
x=open(S,encoding='utf-8').read(); rels=open(RL,encoding='utf-8').read()
CM=360000
# 제목 상자
m=[m for m in re.finditer(r'<p:sp>.*?</p:sp>',x,re.S) if 'name="Text Box 9"' in m.group()][0]; sp=m.group()
TITLE=['등검은말벌 둥지 추적 마킹 트랩','Automatic Marking Trap for Tracking Nests of Vespa velutina','Team 초벌','기계자동차공학부 기계공학전공 이서현 · 이승준']
ps=re.findall(r'<a:p>.*?</a:p>',sp,re.S); new=''
for p,t in zip(ps,TITLE):
    ppr=re.search(r'<a:pPr.*?</a:pPr>|<a:pPr[^>]*/>',p,re.S); ppr=ppr.group() if ppr else ''
    rpr=re.search(r'<a:rPr[^>]*/>|<a:rPr[^>]*>.*?</a:rPr>',p,re.S).group()
    new+=f'<a:p>{ppr}<a:r>{rpr}<a:t>{e(t)}</a:t></a:r></a:p>'
a=sp.index('<a:p>'); b=sp.index('</p:txBody>')
x=x[:m.start()]+sp[:a]+new+sp[b:]+x[m.end():]
nid=[300]; add=[]
def tb(x0,y0,w,h,lines,sz=3200):
    nid[0]+=1
    ps=''.join(f'<a:p><a:pPr marL="457200" indent="-457200"><a:lnSpc><a:spcPct val="115000"/></a:lnSpc><a:spcBef><a:spcPts val="900"/></a:spcBef><a:buFont typeface="Arial"/><a:buChar char="•"/></a:pPr><a:r><a:rPr lang="ko-KR" sz="{sz}" dirty="0"><a:solidFill><a:srgbClr val="1F2A44"/></a:solidFill><a:latin typeface="맑은 고딕"/><a:ea typeface="맑은 고딕"/></a:rPr><a:t>{e(l)}</a:t></a:r></a:p>' for l in lines)
    add.append(f'<p:sp><p:nvSpPr><p:cNvPr id="{nid[0]}" name="본문 {nid[0]}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{int(x0*CM)}" y="{int(y0*CM)}"/><a:ext cx="{int(w*CM)}" cy="{int(h*CM)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr><p:txBody><a:bodyPr wrap="square" lIns="0" rIns="0"><a:normAutofit/></a:bodyPr><a:lstStyle/>{ps}</p:txBody></p:sp>')
ri=[60]
def pic(img,x0,y0,w):
    global rels
    im=Image.open(img); h=w*im.height/im.width; nid[0]+=1; rid=f'rId{ri[0]}'; ri[0]+=1
    fn=os.path.basename(img); shutil.copy(img,f'{D}/ppt/media/{fn}')
    rels=rels.replace('</Relationships>',f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/{fn}"/></Relationships>')
    add.append(f'<p:pic><p:nvPicPr><p:cNvPr id="{nid[0]}" name="그림 {nid[0]}"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr><p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill><p:spPr><a:xfrm><a:off x="{int(x0*CM)}" y="{int(y0*CM)}"/><a:ext cx="{int(w*CM)}" cy="{int(h*CM)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>')
    return h
C=__import__('panel_content')
tb(5.0,26.6,17.8,28.5,C.P11,3600); tb(26.6,26.6,14.6,28.5,C.P12,3600)
hh=(55.8-23.4-0.5)/2; ww=hh*31.4/21.4; xx=43.5+(37.6-ww)/2
pic('fig_rep.png',xx,23.4,ww); pic('fig_idea.png',xx,23.4+hh+0.5,ww)
pic('fig_goal.png',4.2,63.2,37.0); pic('fig_result.png',42.0,63.2,37.6)
tb(8.6,98.0,31.6,12.0,C.P41,3400); tb(44.6,97.6,36.0,12.0,C.P42,3400)
x=x.replace('</p:spTree>',''.join(add)+'</p:spTree>')
open(S,'w',encoding='utf-8').write(x); open(RL,'w',encoding='utf-8').write(rels)
if os.path.exists(OUT): os.remove(OUT)
z=zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED)
for root,_,fs in os.walk(D):
    for f in fs: p=os.path.join(root,f); z.write(p,os.path.relpath(p,D))
z.close(); print(OUT)
