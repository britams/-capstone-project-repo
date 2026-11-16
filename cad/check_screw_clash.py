# -*- coding: utf-8 -*-
"""나사끼리 겹침 검사 (서현 11/17 01:23 "가까이 있는 나사들이 이런 식으로 겹쳐 있지는 않은지 전부 확인", CAP-AI-62)
  D5g_full(급이 있음)에서 체결 부품(나사·볼트·너트·와셔·기둥·스페이서) 물체를 낱개 solid로 나눠, 서로 다른 두 solid가
  ① 부피로 겹치면 (> 0.01 mm³) '겹침', ② 안 겹쳐도 0.5 mm보다 가까우면 '너무 가까움' (드라이버·렌치가 안 들어감)
  나사와 그 나사가 지나가는 너트·와셔·기둥은 같은 축에 있으면 짝으로 보고 뺌 (축 거리 < 0.3)
freecad.exe cad/check_screw_clash.py (cwd = cad) → split/_screw_clash.json"""
import json, os, re, traceback
HERE = os.getcwd(); OUT = os.path.join(HERE, "split")
rep = dict(clash=[], near=[])
KEY = re.compile(r"(screw|bolt|nut|washer|standoff|spacer|나사|볼트|너트|와셔|기둥|스페이서|M[2-5](\.\d)? ?[×x] ?\d)", re.I)
SKIP = ("212_beam_plates", "211_y_motor_plate", "217_x_motor_plate", "224_y_nut_POM", "225_x_nut_POM", "214_x_lead", "208_y_lead",
        "176_release", "112_entry", "300_marking", "101_deck", "105_top", "226p_", "197_drv_bracket", "181_camera_plate", "192_arduino",
        "193v_", "193g_", "207_y_rods", "304_floor", "227y_home_switch", "227x_home_switch")
try:
    import FreeCAD as App
    d = App.openDocument(os.path.join(HERE, "D5g_full.FCStd"), True)
    parts = []
    for o in d.Objects:
        if not o.TypeId.startswith("Part::") or o.Shape.isNull() or not KEY.search(o.Label) or o.Label.startswith(SKIP):
            continue
        for i, s in enumerate(o.Shape.Solids):
            parts.append((o.Label[:60], i, s))
    rep["n_objects"] = len(set(p[0] for p in parts)); rep["n_solids"] = len(parts)

    def axis(s):                                    # 가장 큰 원통면 축 (나사·너트·기둥 축)
        cy = [f for f in s.Faces if "Cylinder" in f.Surface.TypeId]
        if not cy:
            return None
        f = max(cy, key=lambda f: f.Area)
        return f.Surface.Center, f.Surface.Axis

    def coaxial(a, b):
        A, B = axis(a), axis(b)
        if not A or not B:
            return False
        if abs(abs(A[1].dot(B[1])) - 1) > 1e-3:
            return False
        dv = B[0] - A[0]
        perp = dv - A[1] * dv.dot(A[1])
        return perp.Length < 0.3

    for i in range(len(parts)):
        la, ia, sa = parts[i]
        ba = sa.BoundBox
        for j in range(i + 1, len(parts)):
            lb, ib, sb = parts[j]
            bb = sb.BoundBox
            if not ba.intersect(bb) and ba.isValid():
                gx = max(ba.XMin - bb.XMax, bb.XMin - ba.XMax, 0); gy = max(ba.YMin - bb.YMax, bb.YMin - ba.YMax, 0); gz = max(ba.ZMin - bb.ZMax, bb.ZMin - ba.ZMax, 0)
                if max(gx, gy, gz) > 0.5:
                    continue
            if coaxial(sa, sb):
                continue
            v = sa.common(sb).Volume
            c = sa.BoundBox.Center
            if v > 0.01:
                rep["clash"].append([la, ia, lb, ib, round(v, 2), [round(c.x, 1), round(c.y, 1), round(c.z, 1)]])
            else:
                dist = sa.distToShape(sb)[0]
                if dist < 0.5:
                    rep["near"].append([la, ia, lb, ib, round(dist, 2), [round(c.x, 1), round(c.y, 1), round(c.z, 1)]])
    App.closeDocument(d.Name)
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_screw_clash.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
