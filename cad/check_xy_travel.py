# -*- coding: utf-8 -*-
"""캐리지(xy 무리)와 빔(x 무리) 사이 Y 행정 검사 (CAP-AI-62, 11/17) — s2_motion_v3_check는 움직이는 것 ↔ 고정만 봐서 이 둘 사이는 안 봤음
대기 Y −40에서 dy = 0 … 64 (1 mm) 옮기며 처음 닿는 dy → Y 최대 = −40 + dy − 1. 그리고 바뀐 고정 부품(SK8·볼트·+y X 봉) ↔ S1·S2·S3 정지 겹침
freecad.exe cad/check_xy_travel.py (cwd = cad) → split/_xy_travel.json"""
import json, os, traceback
HERE = os.getcwd(); OUT = os.path.join(HERE, "split")
XY = ("201_", "202_", "203_", "204_", "205", "206_", "221_", "223_", "224_")
XO = ("207_", "208_", "209", "210_", "211_", "212_", "222_", "225_", "227y", "153b_", "153n_")
rep = dict(first_hit=None, static=[])
try:
    import FreeCAD as App
    V = App.Vector
    every = []
    for f in ("S1_급이부", "S2_마킹부", "S3_프레임회로"):
        d = App.openDocument(os.path.join(OUT, f + ".FCStd"), True)
        every += [(f[:2] + " " + o.Label, o.Shape.copy()) for o in d.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull() and not o.Label.startswith("REF")]
        App.closeDocument(d.Name)
    lab = lambda l: l.split(" ", 1)[1]
    xy = [(l, s) for l, s in every if lab(l).startswith(XY)]
    xo = [(l, s) for l, s in every if lab(l).startswith(XO) and ("[marker]" in l or not lab(l).startswith(("153b_", "153n_")))]
    xys = [(l, i, t) for l, s in xy for i, t in enumerate(s.Solids)]
    xos = [(l, i, t) for l, s in xo for i, t in enumerate(s.Solids)]
    for dy in range(0, 65):
        hit = None
        for la, ia, sa in xys:
            s = sa.copy(); s.translate(V(0, dy, 0))
            for lb, ib, sb in xos:
                if lab(lb).startswith("208_y_lead") and lab(la).startswith("224_y_nut_POM"):
                    continue
                if s.BoundBox.intersect(sb.BoundBox) and s.common(sb).Volume > 0.05:
                    hit = [dy, la[:45], ia, lb[:45], ib]; break
            if hit:
                break
        if hit:
            rep["first_hit"] = hit; break
    rep["y_max"] = (-40 + rep["first_hit"][0] - 1) if rep["first_hit"] else ">= 24"
    CH = ("218_rod_supports_SK8", "218s_SK8_bolts", "213_x_rods")
    ok = (("218_rod", "213_x_rods"), ("218s", "218_rod"), ("218s", "100"), ("213_x_rods", "222_"), ("218s", "217s"))
    for la, sa in every:
        if not lab(la).startswith(CH):
            continue
        for lb, sb in every:
            if la == lb or (lab(lb).startswith(CH) and lb < la):
                continue
            if any(lab(la).startswith(p) and lab(lb).startswith(q) or lab(la).startswith(q) and lab(lb).startswith(p) for p, q in ok):
                continue
            if sa.BoundBox.intersect(sb.BoundBox):
                v = sa.common(sb).Volume
                if v > 0.05:
                    rep["static"].append([la[:40], lb[:40], round(v, 1)])
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_xy_travel.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
