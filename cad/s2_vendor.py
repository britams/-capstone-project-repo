# -*- coding: utf-8 -*-
"""S2a 바닥 구동 PC판: 리프트 회색 부품을 판매처 STEP으로 (서현 11/12 13:58 "카탈로그에서 받아와서 상세 설계", CAP-AI-62)

  freecad.exe cad/s2_vendor.py   (따로 띄운 창, cwd = cad) → PC 'capstone design_이서현\\CAD files\\split\\S2a_바닥구동_STEP.FCStd'
McMaster CAD는 공개 레포에 올리지 않음 (s1_vendor.py와 같은 규칙). 레포의 S2a는 판매처 표 치수 모양 (lift_module.HW).
넣는 것 (받은도면 step파일, STEP 원점 = 부품 가운데, 축 z):
  147  5033N108  축 Ø4 × 75            → 가운데 (65, 4, 300.5)
  149  61205K72  볼 부싱 4 × 8 × 12      → 가운데 (65, 4, 268)
  146  8969T117  스프링 (자유 25.4)      → 설치 길이 23.61로 z만 줄여 받침 z 239.39에 (그림용 — 실제 감김은 STEP 그대로)
  148k 57485K64  축 칼라 Ø4 × 10 × 5    → 가운데 (65, 4, 289.5)
  227ps 92000A017 M2 × 10 / 227fs 92000A019 M2 × 12 / 153ss 92000A107 M2.5 × 12 → 레포 나사 자리(머리 밑면·방향) 그대로
KW11-3Z 스위치는 판매처 CAD가 없어 레포 모양 그대로 (Omron SS-5GL STEP은 레버 14.5라 KW11 레버 28 자리와 다름 → 안 씀)
"""
import json, os, sys, traceback
HERE = os.getcwd()
sys.path.insert(0, HERE)
STEP = r"C:\Users\Seohyun_Lee\Desktop\capstone design\받은도면 step파일" + "\\"
PC = r"C:\Users\Seohyun_Lee\Desktop\capstone design_이서현\CAD files\split"
OUT = os.path.join(HERE, "split")
rep = dict(ok=False)
try:
    import glob
    import FreeCAD as App
    import Part
    V = App.Vector
    import lift_module as LM
    import D5g_home_switches as HS

    def rd(k):
        return Part.read(glob.glob(STEP + k + "*")[0])

    def at(s, p, rot=None):
        s = s.copy()
        if rot is not None:
            s.rotate(V(0, 0, 0), rot.Axis, rot.Angle * 180 / 3.141592653589793)
        s.translate(p)
        return s

    def screw_put(s, head_under, shank_dir):
        """STEP 나사 (축 z): 머리 쪽 끝을 찾아 머리 밑면 = head_under, 몸통 방향 = shank_dir"""
        b = s.BoundBox
        top_wide = s.common(Part.makeBox(20, 20, 0.3, V(-10, -10, b.ZMax - 0.3))).BoundBox.XLength > 3.0
        # 머리 밑면 z: 머리 쪽 끝에서 가장 넓은 단면이 끝나는 곳 — 머리 높이는 판매처 표 M2 1.3, M2.5 1.6 근사 대신 단면으로 찾음
        zs = [b.ZMax - 0.1 * i for i in range(40)] if top_wide else [b.ZMin + 0.1 * i for i in range(40)]
        zu = zs[-1]
        for z in zs:
            w = s.common(Part.makeBox(20, 20, 0.05, V(-10, -10, z - 0.025))).BoundBox.XLength
            if w < b.XLength * 0.75:
                zu = z
                break
        s = s.copy()
        s.translate(V(0, 0, -zu))
        down = V(0, 0, -1) if top_wide else V(0, 0, 1)                 # STEP에서 몸통이 가는 쪽
        r = App.Rotation(down, shank_dir)
        s = _rot(s, r)
        s.translate(head_under)
        return s

    def _rot(s, r):
        s = s.copy()
        s.Placement = App.Placement(V(0, 0, 0), r).multiply(s.Placement)
        return s

    d = App.openDocument(os.path.join(OUT, "S2a_바닥구동.FCStd"))
    H = LM.HW
    cx, cy = H["xy"]
    new = {}
    new["147_"] = at(rd("5033N108"), V(cx, cy, sum(H["sh_z"]) / 2))
    new["149_"] = at(rd("61205K72"), V(cx, cy, sum(H["bush_z"]) / 2))
    sp = rd("8969T117")
    m = App.Matrix()
    m.scale(1, 1, H["L_inst"] / 25.4)
    sp = sp.transformGeometry(m)
    sp.translate(V(cx, cy, H["seat"] + H["L_inst"] / 2 - (sp.BoundBox.ZMax + sp.BoundBox.ZMin) / 2))
    new["146_"] = sp
    new["148k"] = at(rd("57485K64"), V(cx, cy, H["col_z"] + H["col_w"] / 2))
    # 나사: 레포와 같은 자리
    k = HS.KW
    def sw_screws(O, eL, eW, eH, step):
        out = []
        for l in ((k["L"] - k["hole_p"]) / 2, (k["L"] + k["hole_p"]) / 2):
            c = O + eL * l + eH * k["hole_z"]
            out.append(screw_put(rd(step), c + eW * k["W"], eW * -1))
        return Part.makeCompound(out)
    z_lev = H["col_z"] - H["delta"]
    new["227ps"] = sw_screws(V(61.8, 30.5, z_lev - HS.LEVER_TOP), V(0, -1, 0), V(1, 0, 0), V(0, 0, 1), "92000A017")
    new["227fs"] = sw_screws(V(36.0, 3.3, 262.0 - HS.LEVER_TOP), V(0, 1, 0), V(1, 0, 0), V(0, 0, 1), "92000A019")
    xf = LM.X_BACK - 10.5
    zm = 268.0
    new["153ss"] = Part.makeCompound([screw_put(rd("92000A107"), V(xf - 8.0, LM.Y_C + dy, zm), V(1, 0, 0)) for dy in (-5.0, 5.0)])
    names = {"147_": "McMaster 5033N108 STEP", "149_": "McMaster 61205K72 STEP", "146_": "McMaster 8969T117 STEP (설치 길이로 z 줄임)",
             "148k": "McMaster 57485K64 STEP", "227ps": "McMaster 92000A017 STEP", "227fs": "McMaster 92000A019 STEP", "153ss": "McMaster 92000A107 STEP"}
    done = []
    for pre, shp in new.items():
        o = [x for x in d.Objects if x.Label.startswith(pre)]
        if not o:
            continue
        o[0].Shape = shp
        o[0].Label = o[0].Label.split(" ")[0] + " (" + names[pre] + ")"
        done.append(pre)
    rep["replaced"] = done
    # 겹침: 바꾼 것 ↔ S2a 전부 (나사산 물림·끼움은 허용)
    allow = {("147_", "149_"), ("147_", "140_"), ("147_", "148k"), ("227ps", "158_"), ("227ps", "227p"), ("227fs", "151_"), ("227fs", "227f"),
             ("153ss", "158_"), ("153ss", "153s"), ("149_", "158_")}
    hits = []
    for pre in done:
        a = [x for x in d.Objects if x.Label.startswith(pre)][0]
        for o in d.Objects:
            if o is a or not hasattr(o, "Shape") or o.Shape.isNull() or not a.Shape.BoundBox.intersect(o.Shape.BoundBox):
                continue
            v = a.Shape.common(o.Shape).Volume
            if v > 0.05:
                b = o.Label.split(" ")[0]
                ok = any(pre.startswith(x) and b.startswith(y) or b.startswith(x) and pre.startswith(y) for x, y in allow)
                hits.append((pre, b, round(v, 2), "허용" if ok else "문제"))
    rep["overlaps"] = hits
    rep["bad"] = [h for h in hits if h[3] == "문제"]
    os.makedirs(PC, exist_ok=True)
    d.saveAs(os.path.join(PC, "S2a_바닥구동_STEP.FCStd"))
    rep["saved"] = os.path.join(PC, "S2a_바닥구동_STEP.FCStd")
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
with open(os.path.join(OUT, "_s2_vendor.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
