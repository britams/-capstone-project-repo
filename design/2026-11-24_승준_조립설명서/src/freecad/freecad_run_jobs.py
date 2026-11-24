# -*- coding: utf-8 -*-
"""freecad_asm_setup.py 다음에 실행. JOBS_FILE(gen_jobs.py가 만든 json)의 그림을 모두 찍고 renders.zip으로 묶는다.
실행 전에 전역 변수 JOBS_FILE, (선택) ONLY = "S_" 같은 앞글자 를 정해 둔다."""
import json, zipfile, glob, os, time, builtins, FreeCAD as App, Part
WD = r"C:\Users\user\Desktop\창의적종합설계\조립설명서_2026-11-24\_work"
A = App.getDocument("ASM_manual"); F = builtins.ASM_FN
J = json.load(open(JOBS_FILE, encoding="utf-8"))
for nk, src, idx in J["splits"]:          # 부품 사진용 하나짜리 키
    if A.getObject(nk) is None:
        s = A.getObject(src).Shape
        A.addObject("Part::Feature", nk).Shape = Part.makeCompound([s.Solids[i].copy() for i in idx])
A.recompute()
only = globals().get("ONLY", "")
t = time.time(); n = 0
for j in J["jobs"]:
    if only and not j["name"].startswith(only):
        continue
    F["run_job"](j); n += 1
zp = WD + "\\renders_latest.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for f in glob.glob(WD + "\\S_*") + glob.glob(WD + "\\T_*") + glob.glob(WD + "\\X_*"):
        z.write(f, os.path.basename(f))
print(n, "renders", round(time.time() - t, 1), "s ->", zp)
