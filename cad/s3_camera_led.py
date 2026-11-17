# -*- coding: utf-8 -*-
"""카메라 판 181 넓힘 + 조명 LED 3구 모듈 2 (서현 11/17 16시 '카메라 판을 넓혀 양옆에', CAP-AI-62)
  옛 링 조명 182 (Ø30)를 지우고, LED 모듈 2개(78 × 15 × 6 [추측 — 판매처에 치수 없음])를 판 아래 카메라 양옆(y 방향으로 길게)에 폼 테이프로.
  판 181: 아크릴 3 mm 레이저, x 26~84 · y −42~38 (옛 38.5~71.5 · −23.5~18.5). 카메라 M2 구멍 4 · M3 기둥 구멍 2는 같은 자리.
  높이 조절 = M3 기둥 (30 + 15 + 8) 바꿔 끼우기 → 카메라·조명이 같이 움직임. 이 스크립트가 위아래로 옮겨 보며 부딪히는지 잼.
한 번만 — 다시는 split/S3_프레임회로_before_camled.FCStd에서. GUI FreeCAD에서 exec 가능 (os._exit 없음) → split/_camera_led.json"""
import json, os, shutil, traceback, glob, time, math
import FreeCAD as App, Part
HERE = r"C:\capstone\-capstone-project-repo\cad"; OUT = os.path.join(HERE, "split")
DESK = r"C:\Users\Seohyun_Lee\Desktop\capstone design\주문제작 파일\레이저_판"
V = App.Vector
rep = {}
PX0, PX1, PY0, PY1, PZ0, PZ1 = 26.0, 84.0, -42.0, 38.0, 554.0, 557.0          # 새 판 181
LED = [(34.0, -2.0), (76.0, -2.0)]                                              # 모듈 가운데 (x, y), y로 78 길게
LW, LL, LT = 15.0, 78.0, 6.0


def _save(doc, path):
    try:
        doc.save(); return
    except OSError:
        pass
    tmp = sorted(glob.glob(path + ".*-*"), key=os.path.getmtime)[-1]
    for _ in range(60):
        try:
            os.replace(tmp, path); return
        except OSError:
            time.sleep(2)
    raise OSError("replace failed " + tmp)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def dxf_from_shape(sh, path):                       # s23_trap_offset.py와 같음 (판 가운데를 잘라 선·원)
    bb = sh.BoundBox; ws = sh.slice(V(0, 0, 1), (bb.ZMin + bb.ZMax) / 2); e = []; nh = 0
    for w in ws:
        for ed in w.Edges:
            c = ed.Curve
            if "Circle" in type(c).__name__ and ed.isClosed():
                e.append("0\nCIRCLE\n8\nCUT\n10\n%.4f\n20\n%.4f\n40\n%.4f" % (c.Center.x - bb.XMin, c.Center.y - bb.YMin, c.Radius)); nh += 1
            else:
                pts = [ed.Vertexes[0].Point, ed.Vertexes[-1].Point] if "Line" in type(c).__name__ else ed.discretize(Deflection=0.02)
                for p, q in zip(pts[:-1], pts[1:]):
                    e.append("0\nLINE\n8\nCUT\n10\n%.4f\n20\n%.4f\n11\n%.4f\n21\n%.4f" % (p.x - bb.XMin, p.y - bb.YMin, q.x - bb.XMin, q.y - bb.YMin))
    open(path, "w", encoding="ascii").write("0\nSECTION\n2\nHEADER\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n" + "\n".join(e) + "\n0\nENDSEC\n0\nEOF\n")
    return dict(size=[round(bb.XLength, 1), round(bb.YLength, 1)], entities=len(e), circles=nh)


try:
    P, B = os.path.join(OUT, "S3_프레임회로.FCStd"), os.path.join(OUT, "S3_프레임회로_before_camled.FCStd")
    shutil.copy(B, P) if os.path.exists(B) else shutil.copy(P, B)
    d = App.openDocument(P, True)
    ob = lambda p: [o for o in d.Objects if o.TypeId.startswith("Part::") and o.Label.startswith(p)]
    cs = [s.BoundBox.Center for o in ob("180s_camera_screws") for s in o.Shape.Solids]
    bb = [s.BoundBox.Center for o in ob("181s_camera_standoffs") for s in o.Shape.Solids]
    rep["holes"] = dict(m2=len(cs), m3=len(bb))
    for o in ob("181_camera_plate") + ob("182_"):
        d.removeObject(o.Name)
    cb = box(PX0, PX1, PY0, PY1, PZ0, PZ1)
    for c in cs:
        cb = cb.cut(Part.makeCylinder(1.2, 5, V(c.x, c.y, PZ0 - 1)))
    for c in bb:
        cb = cb.cut(Part.makeCylinder(1.7, 5, V(c.x, c.y, PZ0 - 1)))
    cb = cb.removeSplitter()
    pl = d.addObject("Part::Feature", "CAM_PLATE"); pl.Shape = cb
    pl.Label = "181_camera_plate (카메라 판 — 아크릴 3 mm 레이저 58 × 80, 카메라 M2 × 8 + 너트 4 · 아래 양옆 LED 모듈 2 — 11/17 넓힘)"
    led = Part.makeCompound([box(x - LW / 2, x + LW / 2, y - LL / 2, y + LL / 2, PZ0 - LT, PZ0) for x, y in LED])
    lo = d.addObject("Part::Feature", "CAM_LED"); lo.Shape = led
    lo.Label = "182_light_LED_modules (간판용 LED 3구 모듈 백색 12 V 2 — 판 181 아래 카메라 양옆, 폼 양면테이프, 78 × 15 × 6 [추측], 구매 — 11/17 링 Ø30 대신)"
    d.recompute(); _save(d, P)
    rep["plate"] = dict(valid=cb.isValid(), solids=len(cb.Solids))
    rep["dxf"] = dxf_from_shape(cb, os.path.join(HERE, "print", "laser", "181_카메라판_아크릴3T.dxf"))
    if os.path.isdir(DESK):
        shutil.copy(os.path.join(HERE, "print", "laser", "181_카메라판_아크릴3T.dxf"), DESK)
    # 겹침: 새 것 ↔ 전부 (지금 높이) + 카메라 묶음을 위아래로 옮겨 봄
    every = []
    for ff in ("S1_급이부", "S2_마킹부", "S2a_바닥구동", "S3_프레임회로"):
        dd = App.openDocument(os.path.join(OUT, ff + ".FCStd"), True)
        every += [(o.Label, o.Shape.copy()) for o in dd.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull() and not o.Label.startswith(("190_", "REF_"))]
        App.closeDocument(dd.Name)
    CAM = ("180", "181", "182")
    ok = (("181_", "180"), ("181_", "181s"), ("182", "181_"), ("181s", "105"), ("180s", "180"))
    move = [(la, sa) for la, sa in every if la.startswith(CAM)]
    rest = [(lb, sb) for lb, sb in every if not lb.startswith(CAM)]
    XY = ("2", "3")                                   # 200·300번대 = XY·바닥 (움직이는 것 포함)

    def hits(dz, new_only):
        out = []
        for la, sa in move:
            if new_only and not la.startswith(("181_", "182")):
                continue
            s = sa.copy(); s.translate(V(0, 0, dz))
            for lb, sb in rest:
                if any(la.startswith(p) and lb.startswith(q) or la.startswith(q) and lb.startswith(p) for p, q in ok):
                    continue
                if lb.startswith("181s") and dz:          # 기둥은 길이를 바꿔 끼우므로 안 셈
                    continue
                if s.BoundBox.intersect(sb.BoundBox):
                    v = s.common(sb).Volume
                    if v > 0.05:
                        out.append([la[:30], lb[:40], round(v, 1)])
        return out
    rep["hits_now"] = hits(0, True)
    xy_top = max(sb.BoundBox.ZMax for lb, sb in rest if lb.startswith(XY) and sb.BoundBox.YMin < PY1 and sb.BoundBox.YMax > PY0 and sb.BoundBox.ZMax < 540)
    rep["xy_moving_top_z"] = round(xy_top, 1)
    rep["range"] = {}
    for dz in (-35, -30, -20, -10, 10, 15, 19, 25):
        rep["range"][dz] = len(hits(dz, False))
    rep["range_detail_25"] = hits(25, False)[:5]
    App.closeDocument(d.Name)
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_camera_led.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(rep, ensure_ascii=False)[:3000])
