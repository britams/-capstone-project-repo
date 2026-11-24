import sys, subprocess, json
from PIL import Image
idx=json.load(open('pv/idx.json'))
ids=sys.argv[2:]; out=sys.argv[1]
ims=[]
for s in ids:
    n=idx[s] if s in idx else int(s)
    subprocess.run(['pdftoppm','-r','70','-png','-f',str(n),'-l',str(n),'manual_body.pdf','pv/tmp'],check=True)
    import glob
    f=sorted(glob.glob('pv/tmp-*.png'))[-1]
    ims.append(Image.open(f).convert('RGB'))
    import os; os.remove(f)
w,h=ims[0].size
sheet=Image.new('RGB',(2*w,((len(ims)+1)//2)*h),'white')
for i,im in enumerate(ims): sheet.paste(im,((i%2)*w,(i//2)*h))
sheet.save(out)
