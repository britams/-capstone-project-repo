# -*- coding: utf-8 -*-
"""(11/15 서현 '안 자르고 그대로 쓰면?') 봉·T8을 규격 길이로 늘렸을 때 늘어난 토막이 다른 부품과 닿는지 — 양 끝·한쪽 끝 다 봄, 움직이는 것은 움직임 범위에서
  freecad.exe cad/_stdlen_check.py → split/_stdlen.json (모델은 안 바꿈)"""
import json, os, traceback
HERE = os.getcwd(); rep = {}
try:
    import FreeCAD as App, Part
    V = App.Vector
    d = App.openDocument(os.path.join(HERE, "D5g_full.FCStd"), True)
    objs = [(o.Label, o.Shape) for o in d.Objects if o.TypeId.startswith("Part::") and not o.Label.startswith("REF")]
    objs = [(l, s) for l, s in objs if not s.isNull() and s.Volume > 0]
    # (부품, 새 길이들, 움직임: 'x' = 빔과 같이 X, 'xy' = 캐리지, None)
    T = [("213_x_rods", (200.0, 250.0, 300.0), None), ("207_y_rods", (150.0, 200.0), "x"), ("214_x_lead_screw_T8", (100.0, 150.0, 300.0), None),
         ("208_y_lead_screw_T8", (150.0, 200.0, 300.0), "x"), ("223_holder_guide_pins", (70.0, 80.0, 100.0), "xy")]
    XS = (-38.0, -20.0, 0.0); YS = (0.0, 26.0, 56.0)
    others = lambda lab: [(l, s) for l, s in objs if not l.startswith(lab)]
    for lab, lens, mv in T:
        sh = [s for l, s in objs if l.startswith(lab)][0]
        out = []
        for sol in sh.Solids:
            cf = [f for f in sol.Faces if "Cylinder" in type(f.Surface).__name__]
            f = max(cf, key=lambda f: f.Area)
            ax = f.Surface.Axis; c = f.Surface.Center; r = f.Surface.Radius
            ts = [(v.Point - c).dot(ax) for v in sol.Vertexes] or [0]
            bb = sol.BoundBox
            ext = [(V(p) - c).dot(ax) for p in [V(bb.XMin, bb.YMin, bb.ZMin), V(bb.XMax, bb.YMax, bb.ZMax)]]
            t0, t1 = min(ext), max(ext); L0 = t1 - t0
            out.append(dict(L0=round(L0, 1), axis=[round(ax.x, 2), round(ax.y, 2), round(ax.z, 2)], c0=[round(v, 1) for v in (c + ax * t0)], r=round(r, 2), res={}))
            for Ln in lens:
                dl = Ln - L0
                if dl <= 0: continue
                for mode in ("lo", "hi", "both"):
                    segs = []
                    if mode in ("lo", "both"):
                        a = dl if mode == "lo" else dl / 2
                        segs.append(Part.makeCylinder(r, a, c + ax * (t0 - a), ax))
                    if mode in ("hi", "both"):
                        a = dl if mode == "hi" else dl / 2
                        segs.append(Part.makeCylinder(r, a, c + ax * t1, ax))
                    worst = {}
                    poses = [(0, 0)] if mv is None else ([(dx, 0) for dx in XS] if mv == "x" else [(dx, dy) for dx in XS for dy in YS])
                    for dx, dy in poses:
                        for sg in segs:
                            s2 = sg.copy(); s2.translate(V(dx, dy, 0))
                            for l, so in others(lab):
                                if mv and l.startswith(("2", "153b", "153n")) and not l.startswith(("213", "218", "217", "215", "216", "214", "219", "220", "226", "227x")):
                                    pass   # 같이 움직이는 부품도 봄 (간단히 모두 봄)
                                if s2.BoundBox.intersect(so.BoundBox):
                                    v = s2.common(so).Volume
                                    if v > 0.05:
                                        k = l[:45]; worst[k] = max(worst.get(k, 0), round(v, 1))
                    out[-1]["res"]["%g_%s" % (Ln, mode)] = worst
        rep[lab] = out
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(HERE, "split", "_stdlen.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import FreeCAD as App
if App.GuiUp: os._exit(0)
