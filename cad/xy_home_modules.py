# -*- coding: utf-8 -*-
"""X·Y 원점 스위치: 맨 KW11-3Z (납땜 단자) → 리미트 스위치 모듈 Voltly VLT-SM006 (기판 + 같은 꼴 마이크로스위치 + 3핀 헤더, 점퍼선만 꽂음)
(서현 11/16 19:39 "1. 추정 치수로 바로 바꾸기", CAP-AI-62) — 부품 파일 split/P2xy_XY플랫폼.FCStd에서 고치고 xy_platform.py attach로 S2에 붙임
  모듈 치수 [추측 — 판매 페이지에 없음, 사서 잼]: 기판 14 × 32 × 1.6 (스위치 끝에 레버, 반대 끝에 M3 구멍 1 + 3핀 헤더), 기판 밑 납땜 다리 → M3 스페이서 3
  X (227x): 팔 226p 위 — 스페이서 3 + 기판 → 스위치 +4.6 위로. 구멍 (x 34, y −75.5), 팔을 y −70까지 늘림, 옛 M2 구멍 메움. M3 × 10 + 너트
  Y (227y): X 너트 판 XN −x 면 — 스페이서 3 + 기판 (z 435~466, X 나사·POM 너트 위) → 스위치 −x 4.6, 아래로 10 (구멍이 POM 너트·SC8UU를 피하게, 레버 쪽은 기판 밑으로 나옴 [추측]). 구멍 (y −63, z 458), XN 옛 M2 구멍 메움. M3 × 12 + 너트
freecad.exe cad/xy_home_modules.py (cwd = cad) → split/P2xy, print/laser/226p_*.dxf, print/xy/XN_*.dxf, split/_xy_home.json"""
import json, os, sys, traceback, glob
HERE = os.getcwd(); OUT = os.path.join(HERE, "split"); sys.path.insert(0, HERE)
rep = dict()
try:
    import FreeCAD as App, Part
    import lift_v2 as L
    V = App.Vector
    box, cyl = L.box, L.cyl
    d = App.openDocument(os.path.join(OUT, "P2xy_XY플랫폼.FCStd"), True)
    ob = lambda p: [o for o in d.Objects if o.TypeId.startswith("Part::") and o.Label.startswith(p)]
    MOD = "Voltly VLT-SM006 리미트 스위치 모듈 — 기판 14 × 32 [추측] + 3핀 헤더, 점퍼선, 구매"

    def fill_small(sol, region, rmax=1.45):        # region (x0,x1,y0,y1,z0,z1) 안 작은 구멍 메움
        s = sol
        for e in sol.Edges:
            c = e.Curve
            if "Circle" in c.TypeId and c.Radius < rmax:
                p = c.Center
                if region[0] <= p.x <= region[1] and region[2] <= p.y <= region[3] and region[4] <= p.z <= region[5]:
                    s = s.fuse(Part.makeCylinder(c.Radius + 0.01, 8, V(p.x, p.y, p.z) - c.Axis * 4, c.Axis))
        return s.common(box(*[sol.BoundBox.XMin, sol.BoundBox.XMax, sol.BoundBox.YMin, sol.BoundBox.YMax, sol.BoundBox.ZMin, sol.BoundBox.ZMax])).removeSplitter()

    # ---------- X ----------
    sx = ob("227x_home_switch_X")[0]
    s = sx.Shape.copy(); s.translate(V(0, 0, 4.6)); sx.Shape = s
    sx.Label = "227x_home_switch_X (%s — xm 37에서 Y 모터판 211 −x 면이 레버를 누름, 팔 226p 위)" % MOD
    for o in ob("227xs_switch_screws_X"):
        d.removeObject(o.Name)
    arm = ob("226p_x_home_arm")[0]
    a = arm.Shape.fuse(box(25.0, 41.0, -79.5, -70.0, 460.0, 463.0)).removeSplitter()
    a = fill_small(a, (25, 41, -110, -70, 455, 470))
    a = a.cut(cyl(1.7, 6, V(34.0, -75.5, 457.0))).removeSplitter()
    arm.Shape = a
    arm.Label = "226p_x_home_arm (X 원점 스위치 팔 — 알루미늄 3 mm 레이저, 갠트리 레일 y −170 위 M5 × 8 2, 스위치 모듈 M3 1)"
    pcb = box(27.0, 41.0, -105.0, -70.0, 466.0, 467.6).cut(cyl(1.6, 4, V(34.0, -75.5, 465.0)))
    hdr = [box(x - 0.32, x + 0.32, -71.5, -64.0, 468.3, 468.94) for x in (31.46, 34.0, 36.54)] + [box(30.0, 38.0, -72.0, -69.5, 467.6, 470.1)]
    n = d.addObject("Part::Feature", "HMx"); n.Shape = Part.makeCompound([pcb] + hdr)
    n.Label = "227xm_home_module_board_X (%s)" % MOD
    hw = [cyl(2.75, 1.8, V(34.0, -75.5, 458.2)), cyl(1.5, 11.8, V(34.0, -75.5, 458.2)), cyl(2.5, 3.0, V(34.0, -75.5, 463.0)) .cut(cyl(1.6, 4, V(34.0, -75.5, 462.5))),
          cyl(3.2, 2.4, V(34.0, -75.5, 467.6)).cut(cyl(1.5, 4, V(34.0, -75.5, 467.0)))]
    n = d.addObject("Part::Feature", "HMxs"); n.Shape = Part.makeCompound(hw)
    n.Label = "227xs_switch_screws_X (M3 × 10 냄비 + 나일론 스페이서 M3 × 3 + 너트 — 팔 밑에서, 구매)"
    # ---------- Y ----------
    sy = ob("227y_home_switch_Y")[0]
    s = sy.Shape.copy(); s.translate(V(-4.6, 0, -10.0)); sy.Shape = s
    sy.Label = "227y_home_switch_Y (%s — ym −40에서 펜 홀더 202 −y 면이 레버를 누름, X 너트 판 XN −x 면, 빔과 같이 움직임)" % MOD
    for o in ob("227ys_switch_screws_Y"):
        d.removeObject(o.Name)
    bp = ob("212_beam_plates")[0]
    xn = [q for q in bp.Shape.Solids if q.BoundBox.XLength < 4][0]
    nx = fill_small(xn, (85, 92, -70, -54, 438, 462))
    nx = nx.cut(cyl(1.7, 6, V(85.0, -63.0, 458.0), V(1, 0, 0))).removeSplitter()
    bp.Shape = Part.makeCompound([nx if q.isSame(xn) else q for q in bp.Shape.Solids])
    x0 = xn.BoundBox.XMin                       # 87.4
    pcb = box(x0 - 3.0 - 1.6, x0 - 3.0, -67.0, -53.0, 435.0, 466.0).cut(cyl(1.6, 4, V(x0 - 6, -63.0, 458.0), V(1, 0, 0)))
    hdr = [box(x0 - 6.2, x0 - 4.6 - 0.0, y - 0.32, y + 0.32, 466.0, 472.0) for y in (-62.54, -60.0, -57.46)]
    n = d.addObject("Part::Feature", "HMy"); n.Shape = Part.makeCompound([pcb] + hdr)
    n.Label = "227ym_home_module_board_Y (%s, 빔과 같이 움직임)" % MOD
    ax = V(-1, 0, 0)
    hw = [cyl(2.75, 1.8, V(x0 + 3.0 + 1.8, -63.0, 458.0), ax), cyl(1.5, 12.0, V(x0 + 3.0 + 1.8, -63.0, 458.0), ax),
          cyl(2.5, 3.0, V(x0, -63.0, 458.0), ax).cut(cyl(1.6, 4, V(x0 + 0.5, -63.0, 458.0), ax)),
          cyl(3.2, 2.4, V(x0 - 4.6, -63.0, 458.0), ax).cut(cyl(1.5, 4, V(x0 - 4.0, -63.0, 458.0), ax))]
    n = d.addObject("Part::Feature", "HMys"); n.Shape = Part.makeCompound(hw)
    n.Label = "227ys_switch_screws_Y (M3 × 12 냄비 + 나일론 스페이서 M3 × 3 + 너트 — XN +x 쪽에서, 구매, 빔과 같이 움직임)"
    d.recompute(); d.save()
    # DXF: 226p (판 = xy), XN (판 = yz)
    def dxf(sl, fn, ax, folder):
        bb = sl.BoundBox
        f = max([x for x in sl.Faces if x.Surface.TypeId == "Part::GeomPlane"], key=lambda x: x.Area)
        g = lambda p: (getattr(p, ax[0]) - getattr(bb, ax[0].upper() + "Min"), getattr(p, ax[1]) - getattr(bb, ax[1].upper() + "Min"))
        ents = []
        for e in f.Edges:
            cv = e.Curve
            if "Circle" in cv.TypeId and e.isClosed():
                cc = g(cv.Center); ents.append("0\nCIRCLE\n8\nCUT\n10\n%.4f\n20\n%.4f\n40\n%.4f" % (cc[0], cc[1], cv.Radius)); continue
            pts = [g(p) for p in e.discretize(Deflection=0.02)]
            for a_, z in zip(pts[:-1], pts[1:]):
                ents.append("0\nLINE\n8\nCUT\n10\n%.4f\n20\n%.4f\n11\n%.4f\n21\n%.4f" % (a_[0], a_[1], z[0], z[1]))
        open(os.path.join(HERE, "print", folder, fn), "w", encoding="ascii").write(
            "0\nSECTION\n2\nHEADER\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n" + "\n".join(ents) + "\n0\nENDSEC\n0\nEOF\n")
        rep[fn] = len(ents)
    dxf(a, "226p_X원점팔_알루미늄3T.dxf", ("x", "y"), "laser")
    dxf(nx, "XN_X너트판_알루미늄3T.dxf", ("y", "z"), "xy")
    rep["arm"] = [round(a.BoundBox.YMin, 1), round(a.BoundBox.YMax, 1)]
    # 부품 파일 안 겹침 — 새 것 + 옮긴 스위치
    CH = ("227x", "227y", "226p")
    okp = (("227x", "227x"), ("227y", "227y"), ("227x", "226p"), ("227y", "212_beam_plates"), ("226p", "226s"), ("226p", "REF_100b"))
    hits = []
    obs = [o for o in d.Objects if o.TypeId.startswith("Part::")]
    for o in [x for x in obs if x.Label.startswith(CH)]:
        for q in obs:
            if q is o:
                continue
            if any(o.Label.startswith(p) and q.Label.startswith(r) or o.Label.startswith(r) and q.Label.startswith(p) for p, r in okp):
                continue
            if o.Shape.BoundBox.intersect(q.Shape.BoundBox):
                v = o.Shape.common(q.Shape).Volume
                if v > 0.05:
                    hits.append([o.Label[:35], q.Label[:35], round(v, 1)])
    rep["hits"] = hits
    App.closeDocument(d.Name)
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_xy_home.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
