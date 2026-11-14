# -*- coding: utf-8 -*-
"""(11/15 서현 "안 자르고 그대로" → "해 그렇게", CAP-AI-62) 봉·T8을 파는 길이 그대로 — 자르는 공구 없이.
  X 봉 Ø8 163 → 200 (+x로), Y 봉 Ø6 124 → 150 (+y로), 안내 핀 Ø3 69 → 70 (위로), X T8 93 → 150 (모터 반대 −x로), Y T8 133 → 150 (+y로).
  늘어난 끝이 지나가게 출력 부품 구멍을 끝까지 뚫음: 218 X 봉 받침 (+x 쪽 2개), 212 빔 끝 블록 B (+y — Y 봉 2·T8).
  검사 근거: _stdlen_check.py (11/15 02:24·02:36) — 이 길이들은 위 두 구멍 말고 닿는 것 없음 (움직임 범위 포함).
  ※ s2_doors_v3.py를 다시 돌리면 옛 S2 백업에서 시작하므로 이 스크립트를 그 뒤에 다시 돌릴 것.
  freecad.exe cad/s2_stdlen.py (cwd = cad) → split/S2_마킹부.FCStd 고쳐 씀, print/all/218·212 다시, split/_stdlen_apply.json"""
import json, os, traceback
HERE = os.getcwd(); OUT = os.path.join(HERE, "split")
NEW = {"213_x_rods": (200.0, "hi"), "207_y_rods": (150.0, "hi"), "223_holder_guide_pins": (70.0, "hi"),
       "214_x_lead_screw_T8": (150.0, "hi"), "208_y_lead_screw_T8": (150.0, "hi")}
rep = dict(changed=[], holes={}, hits=[])
try:
    import FreeCAD as App, Part, MeshPart
    V = App.Vector

    def axis_of(sol):
        f = max([f for f in sol.Faces if "Cylinder" in type(f.Surface).__name__], key=lambda f: f.Area)
        ax, c, r = f.Surface.Axis, f.Surface.Center, f.Surface.Radius
        ts = [(v.Point - c).dot(ax) for v in sol.Vertexes]
        bb = sol.BoundBox
        ts = [(V(p) - c).dot(ax) for p in (V(bb.XMin, bb.YMin, bb.ZMin), V(bb.XMax, bb.YMax, bb.ZMax))]
        return ax, c, r, min(ts), max(ts)

    d = App.openDocument(os.path.join(OUT, "S2_마킹부.FCStd"))
    obj = lambda p: [o for o in d.Objects if o.Label.startswith(p)][0]
    lines = {}
    for p, (Ln, mode) in NEW.items():
        o = obj(p)
        sols = []
        for sol in o.Shape.Solids:
            ax, c, r, t0, t1 = axis_of(sol)
            L0 = t1 - t0
            if L0 >= Ln - 0.5:
                sols.append(sol); continue
            sols.append(sol.fuse(Part.makeCylinder(r, Ln - L0 + 0.01, c + ax * (t1 - 0.01), ax)).removeSplitter())
            lines.setdefault(p, []).append((c + ax * t0, ax, r, Ln))
        o.Shape = Part.makeCompound(sols) if len(sols) > 1 else sols[0]
        if "규격 길이" not in o.Label:
            o.Label = o.Label + " — 규격 %g mm 그대로 (자르지 않음, 11/15)" % Ln
        rep["changed"].append([o.Label[:70], round(Ln, 1)])
    # 구멍 끝까지: 늘린 봉·나사의 축을 따라 긴 원통으로 깎음 (봉 r + 0.15, T8은 r 4.5)
    for part, src in (("218_rod_supports", "213_x_rods"), ("212_beam_end_blocks", "207_y_rods"), ("212_beam_end_blocks", "208_y_lead_screw_T8")):
        o = obj(part); sh = o.Shape; n = 0
        for p0, ax, r, Ln in lines.get(src, []):
            rr = 4.5 if "T8" in src else r + 0.15
            cyl = Part.makeCylinder(rr, Ln + 40, p0 - ax * 20, ax)
            if sh.BoundBox.intersect(cyl.BoundBox) and sh.common(cyl).Volume > 0.01:
                sh = sh.cut(cyl); n += 1
        o.Shape = sh.removeSplitter() if n else sh
        rep["holes"][part + "<" + src] = n
        if n and "끝까지" not in o.Label:
            o.Label = o.Label + " — 봉·T8 지나가게 구멍 끝까지 (11/15)"
    d.save()
    # 출력 파일 다시
    pa = os.path.join(HERE, "print", "all")
    for p, fn in (("218_rod_supports", "218_rod_supports"), ("212_beam_end_blocks", "212_beam_end_blocks")):
        s = obj(p).Shape
        MeshPart.meshFromShape(Shape=s, LinearDeflection=0.05, AngularDeflection=0.3).write(os.path.join(pa, fn + ".stl"))
        s.exportStep(os.path.join(pa, fn + ".step"))
        rep.setdefault("print", {})[fn] = dict(valid=s.isValid(), solids=len(s.Solids), vol_cm3=round(s.Volume / 1000, 2))
    # 고정 겹침 검사: 바뀐 것 ↔ S1·S2·S3 (같이 끼워지는 짝은 뺌)
    pairs_ok = (("213", "218"), ("213", "222"), ("207", "212"), ("207", "221"), ("208", "212"), ("208", "224"), ("208", "210"), ("214", "216"),
                ("214", "225"), ("214", "212"), ("223", "206"), ("223", "202"))
    changed = [o for o in d.Objects if o.Label.startswith(tuple(NEW) + ("218_", "212_"))]
    every = []
    for f in ("S1_급이부", "S3_프레임회로"):
        dd = App.openDocument(os.path.join(OUT, f + ".FCStd"), True)
        every += [(o.Label, o.Shape.copy()) for o in dd.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull()]
        App.closeDocument(dd.Name)
    every += [(o.Label, o.Shape) for o in d.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull()]
    for a in changed:
        for lb, sb in every:
            if lb == a.Label or lb.startswith("REF"):
                continue
            if any(a.Label.startswith(p) and lb.startswith(q) or a.Label.startswith(q) and lb.startswith(p) for p, q in pairs_ok):
                continue
            if a.Shape.BoundBox.intersect(sb.BoundBox):
                try:
                    v = a.Shape.common(sb).Volume
                except Exception:
                    v = 0.0
                if v > 0.05:
                    rep["hits"].append([a.Label[:40], lb[:40], round(v, 1)])
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_stdlen_apply.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
