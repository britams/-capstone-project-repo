import FreeCAD as App, os, shutil
# (11/17 서현 급이실) 급이부 있는 판 D5g_full: 옛 T 175 대신 급이실 177이 S2에 있음 → 여기서는 급이부 없는 판 몫 아크릴 관 174만 뺌
C=r"C:\capstone\-capstone-project-repo\cad"; D=r"C:\Users\Seohyun_Lee\Desktop\capstone design"
d=App.openDocument(C+r"\D5g_full.FCStd",True)
for o in list(d.Objects):
    if o.TypeId.startswith("Part::") and o.Label.startswith(("174_release_duct","175_release_feed_tee")):
        d.removeObject(o.Name)
d.save(); App.closeDocument(d.Name)
shutil.copy2(C+r"\D5g_full.FCStd", D+r"\D5g_full.FCStd")
open(C+r"\split\_add_feed.done","w").write("ok")
if App.GuiUp: os._exit(0)
