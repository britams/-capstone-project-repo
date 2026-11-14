# -*- coding: utf-8 -*-
"""(11/15 서현, CAP-AI-62) 열압입 인서트(인두 필요) 없앰: 카메라 걸이 181 인서트 구멍 Ø4 → M3 태핑 밑구멍 Ø2.5 (출력 파일도),
   데크 인서트 100n → 관통 + 너트 (데크 DXF는 s3_deck_hole에서 이미 Ø3.4). S3 고쳐 씀"""
import json, os, traceback
HERE = os.getcwd(); rep = {}
try:
    import FreeCAD as App, Part, MeshPart
    s3 = App.openDocument(os.path.join(HERE, "split", "S3_프레임회로.FCStd"))
    br = [o for o in s3.Objects if o.Label.startswith("181_camera_bracket")][0]
    sh = br.Shape; n = 0
    for f in list(sh.Faces):
        s = f.Surface
        if "Cylinder" in type(s).__name__ and abs(s.Radius - 2.0) < 0.02:
            ax = s.Axis; c = s.Center
            ts = [ (v.Point - c).dot(ax) for v in f.Vertexes ]
            t0, t1 = min(ts), max(ts)
            base = c + ax * t0
            sh = sh.fuse(Part.makeCylinder(2.05, t1 - t0, base, ax)).cut(Part.makeCylinder(1.25, t1 - t0 + 0.02, base - ax * 0.01, ax))
            n += 1
    sh = sh.removeSplitter()
    rep["holes"] = n; rep["valid"] = sh.isValid(); rep["solids"] = len(sh.Solids)
    br.Shape = sh
    br.Label = br.Label.replace("카메라 M2 × 6 네 개", "카메라 M2 × 6 네 개, 위판 쪽 M3 태핑 밑구멍 Ø2.5 2 (11/15 인서트 없앰)")
    for o in list(s3.Objects):
        if o.Label.startswith(("181i_bracket_inserts", "100n_insert_M3_heatset_deck")):
            rep.setdefault("removed", []).append(o.Label[:40]); s3.removeObject(o.Name)
        elif o.Label.startswith("181s_bracket_bolts"):
            o.Label = "181s_bracket_bolts (M3 × 10 십자 냄비 태핑 2 — 위판 위에서 걸이 밑구멍 Ø2.5로, 11/15)"
        elif o.Label.startswith("100m_bolt_M3x10_deck"):
            o.Label = "100m_bolt_M3x10_deck (데크 아래에서 4개, 십자 냄비 M3 × 10 + 데크 위 M3 너트 — 11/15 인서트 없앰, 데크 구멍 Ø3.4)"
    s3.save()
    out = os.path.join(HERE, "print", "all")
    MeshPart.meshFromShape(Shape=sh, LinearDeflection=0.05, AngularDeflection=0.3).write(os.path.join(out, "181_camera_bracket.stl"))
    sh.exportStep(os.path.join(out, "181_camera_bracket.step"))
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(HERE, "split", "_cam_tap.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import FreeCAD as App
if App.GuiUp: os._exit(0)
