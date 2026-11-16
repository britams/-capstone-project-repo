# -*- coding: utf-8 -*-
"""Y 행정 늘리기 (CAP-AI-62, 11/17 03:40 — xy_detail 검사 중 발견)
  캐리지(xy)와 빔(x)끼리 Y로 움직여 본 적이 없었음: 대기(Y −40)에서 +50 (Y +10)부터 홀더 어깨 볼트 너트 202가 YB 판에,
  +51에서 SV 판이 YB에 닿음 → 펌웨어 한계 Y +18 · 마킹실 Ø33 (y −16.5 ~ +16.5)의 +y 쪽 7 mm를 못 감 (11/14부터 있던 문제)
  → YB 판 · +y SC8UU · +y X 봉 213 · 그 SK8 2 · YB 쪽 M4 접시머리 6 · SK8 볼트 4를 +10 (y), Y 봉 207 104 → 114 (미스미 맞춤 길이)
부품 파일 P2xy에서 (다시는 split/P2xy_XY플랫폼_before_ytravel.FCStd에서) → xy_platform attach, 그다음 S2의 218s만 여기서 옮김
GUI FreeCAD에서 exec 가능 → split/_xy_ytravel.json"""
import json, os, sys, shutil, traceback
import FreeCAD as App, Part
HERE = r"C:\capstone\-capstone-project-repo\cad"; OUT = os.path.join(HERE, "split"); sys.path.insert(0, HERE)
V = App.Vector
DY = 10.0
rep = {}
try:
    P = os.path.join(OUT, "P2xy_XY플랫폼.FCStd"); B = os.path.join(OUT, "P2xy_XY플랫폼_before_ytravel.FCStd")
    shutil.copy(B, P) if os.path.exists(B) else shutil.copy(P, B)
    d = App.openDocument(P, True)
    ob = lambda p: [o for o in d.Objects if o.TypeId.startswith("Part::") and o.Label.startswith(p)][0]
    mv = lambda s: (lambda t: (t.translate(V(0, DY, 0)), t)[1])(s.copy())

    def shift(lab, pick):
        o = ob(lab)
        out, n = [], 0
        for s in o.Shape.Solids:
            if pick(s):
                out.append(mv(s)); n += 1
            else:
                out.append(s)
        o.Shape = Part.makeCompound(out)
        return n
    rep["YB"] = shift("212_beam_plates", lambda s: s.BoundBox.YLength < 4 and s.BoundBox.Center.y > 0)
    rep["SC8UU"] = shift("222_x_bearings_SC8UU", lambda s: s.BoundBox.Center.y > 0)
    rep["rod"] = shift("213_x_rods", lambda s: s.BoundBox.Center.y > 0)
    rep["SK8"] = shift("218_rod_supports_SK8", lambda s: s.BoundBox.Center.y > 0)
    rep["M4"] = shift("212_beam_hardware", lambda s: s.BoundBox.Center.y > 20)
    o = ob("207_y_rods")
    out = []
    for s in o.Shape.Solids:
        b = s.BoundBox
        r = b.XLength / 2
        out.append(Part.makeCylinder(r, b.YLength + DY, V(b.Center.x, b.YMin, b.Center.z), V(0, 1, 0)))
    o.Shape = Part.makeCompound(out)
    o.Label = "207_y_rods (Ø8 × 114 양 끝 M4 암나사 — 미스미 맞춤 길이, 판 안쪽 면 사이 (11/17 104 → 114: Y 행정 +10))"
    ob("213_x_rods").Label = "213_x_rods (Ø8 × 200, x −25~175, y −70 · 72 — 11/17 +y 봉 62 → 72: Y 행정)"
    rep["y_rod_len"] = [round(s.BoundBox.YLength, 1) for s in o.Shape.Solids]
    d.recompute(); d.save(); App.closeDocument(d.Name)
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_xy_ytravel.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(rep, ensure_ascii=False))
