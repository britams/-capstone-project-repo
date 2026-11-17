import FreeCAD as App, os, shutil, json
C=r"C:\capstone\-capstone-project-repo\cad"; D=r"C:\Users\Seohyun_Lee\Desktop\capstone design"
d=App.openDocument(C+r"\D5g_full.FCStd",True)
gone=[]
for o in list(d.Objects):
    if o.TypeId.startswith("Part::") and o.Label.startswith(("144b_","144z_","144p_","144pp_","144s_","144t_","175_release_feed_tee","144hf_","177")):   # 11/17 급이실 177·접시 서랍 177d도 뺌
        gone.append(o.Label[:30]); d.removeObject(o.Name)
for o in d.Objects:
    if o.Label.startswith("174_release_duct"):
        o.Label="174_release_duct_acryl (아크릴 파이프 바깥 18 · 안 14 — DKD아크릴 맞춤 절단, 끝 x 140이 출구 — _no: 급이부 없음 (급이부 있는 판 D5g_full은 이 자리에 급이실 177))"
d.saveAs(C+r"\D5g_full_no.FCStd"); App.closeDocument(d.Name)
shutil.copy2(C+r"\D5g_full_no.FCStd", D+r"\D5g_full_no.FCStd")
json.dump(gone, open(C+r"\split\_make_no.json","w",encoding="utf-8"), ensure_ascii=False)
if App.GuiUp: os._exit(0)
