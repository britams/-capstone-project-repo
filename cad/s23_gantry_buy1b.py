# -*- coding: utf-8 -*-
"""갠트리 '전부 사는 것' 1단계 고침 (11/15, CAP-AI-62) — s23_gantry_buy1 검사에서 나온 겹침 3가지
  1) X 모터: L 브래킷 DCB 2025가 모터 몸통과 겹침 → 브래킷 없앰. 판(알루미늄 3 mm 레이저)을 +x 레일의 −x 옆면(x 160)에 바로 대고
     M5 × 8 + 스프링너트 2개로 고정. 그래서 모터·커플링·T8·귀 나사를 +x로 15 mm 옮김 (판 x 142 → 157).
  2) ULN2003 받침 197 X·Y: 내린 받침 위 기판·기둥·나사가 안 따라 내려옴 + SK8 자리와 겹침 →
     기판·기둥·나사 −12 mm, X 받침은 y +14 (SK8 사이 y −44 ~ 36 안), Y 받침은 −x 갠트리 레일(x −18)로 (y −14).
  3) 옛 프린트 218·217을 레일에 붙이던 M5 나사·T너트 (100j·100k 중 6쌍) 지움 — 새 SK8 나사는 S2 218s.
  순서: s23_gantry_buy1 (한 번만) → (이것, 한 번만) → full_merge → s2_motion_v3_check
  freecad.exe cad/s23_gantry_buy1b.py (cwd = cad) → split/S2·S3 고쳐 씀, split/_gantry_buy1b.json"""
import json, os, sys, traceback, glob, time
HERE = os.getcwd(); OUT = os.path.join(HERE, "split"); sys.path.insert(0, HERE)
rep = dict(hits=[], removed=[])
def _save(doc, path):          # buy1과 같음: save가 이름 바꿀 때 잠기면 임시 파일을 직접 옮김
    try:
        doc.save(); App.closeDocument(doc.Name); return
    except OSError:
        pass
    App.closeDocument(doc.Name)
    tmp = sorted(glob.glob(path + ".*-*"), key=os.path.getmtime)[-1]
    for _ in range(60):
        try:
            os.replace(tmp, path); return
        except OSError:
            time.sleep(2)
    raise OSError("replace failed " + tmp)
try:
    import FreeCAD as App, Part
    import lift_v2 as L
    V = App.Vector
    box, cyl = L.box, L.cyl
    def split_move(o, pick, vec):          # o의 고체 중 pick(bb)인 것만 vec만큼 옮김
        sols = o.Shape.Solids; out = []
        for s in sols:
            t = s.copy()
            if pick(s.BoundBox):
                t.translate(vec)
            out.append(t)
        o.Shape = Part.makeCompound(out) if len(out) > 1 else out[0]
    # ---------------- S3
    s3 = App.openDocument(os.path.join(OUT, "S3_프레임회로.FCStd"))
    lab3 = lambda p: [o for o in s3.Objects if o.Label.startswith(p)]
    yX = lambda b: b.Center.y < -2      # X 받침 쪽 (y −56 ~ −4), 옮기기 전 위치로 가름
    mvX, mvY = V(0, 14, 0), V(-188, -14, 0)
    for side, vec in (("X", mvX), ("Y", mvY)):
        for p in ("195p_uln2003_" + side, "198_uln_standoff_" + side):
            for o in lab3(p):
                split_move(o, lambda b: True, V(0, 0, -12) + vec)
        for o in lab3("197_uln_bracket_" + side):
            split_move(o, lambda b: True, vec)
    for p, dz in (("100h_bolt_M5x8_mounts", -12), ("100i_tnut_M5_mounts", 0)):
        for o in lab3(p):
            out = []
            for s in o.Shape.Solids:
                t = s.copy(); b = s.BoundBox
                if b.Center.x > 150:
                    t.translate(V(0, 0, dz) + (mvX if yX(b) else mvY))
                out.append(t)
            o.Shape = Part.makeCompound(out)
    old_xy = [(-18, -65), (170, -77.5), (-18, 57), (170, 69.5), (170, -80), (170, -50)]
    near = lambda b: any(abs(b.Center.x - x) < 1.5 and abs(b.Center.y - y) < 1.5 for x, y in old_xy) and 438 <= b.ZMin and b.ZMax <= 485
    for p in ("100j_bolt_M5_parts", "100k_tnut_M5_parts"):
        for o in lab3(p):
            keep = [s for s in o.Shape.Solids if not near(s.BoundBox)]
            rep["removed"].append([o.Label[:30], len(o.Shape.Solids) - len(keep)])
            o.Shape = Part.makeCompound(keep)
    _save(s3, os.path.join(OUT, "S3_프레임회로.FCStd"))
    # ---------------- S2
    s2 = App.openDocument(os.path.join(OUT, "S2_마킹부.FCStd"))
    ob = lambda p: [o for o in s2.Objects if o.Label.startswith(p)]
    for p in ("217b_", "217s_", "217_x_motor_plate"):
        for o in ob(p):
            s2.removeObject(o.Name)
    DX = 15.0
    for p in ("215_", "215r_", "216_", "214_"):
        for o in ob(p):
            o.Placement.Base = o.Placement.Base + V(DX, 0, 0)
    for p in ("153b_", "153n_"):
        for o in ob(p):
            if o.Shape.BoundBox.XMin > 130:          # X 모터 귀 것만 (Y 모터 것은 x 81~122)
                o.Placement.Base = o.Placement.Base + V(DX, 0, 0)
    YA, zx, xp0 = -65.0, 425.0, 157.0
    M28 = dict(ear_c=35.0, off=8.0, ear_hole=4.2)
    pl = box(xp0, xp0 + 3, YA - 22, YA + 22, 400, 459).cut(cyl(5.0, 5, V(xp0 - 1, YA, zx), V(1, 0, 0)))
    for sy in (-1, 1):
        pl = pl.cut(cyl(M28["ear_hole"] / 2, 5, V(xp0 - 1, YA + sy * M28["ear_c"] / 2, zx - M28["off"]), V(1, 0, 0)))
    hw = []
    for yb in (YA - 9, YA + 9):      # ±9: SK8 나사(y −81·−49)와 같은 y 피함
        pl = pl.cut(cyl(2.75, 5, V(xp0 - 1, yb, 450), V(1, 0, 0)))
        hw.append(L.pan(V(xp0, yb, 450), V(1, 0, 0), 5.0, 8.0))
        hw.append(box(160.5, 165.5, yb - 3, yb + 3, 445, 455))        # 20시리즈 스프링너트 (레일 −x 옆 홈)
    add = [("217_x_motor_plate (알루미늄 판 3 mm 레이저 — +x 레일 −x 옆면에 바로, 28BYJ 귀 Ø4.2 2·축 Ø10·M5 Ø5.5 2)", pl.removeSplitter(), (0.45, 0.6, 0.85)),
           ("217s_x_motor_screws (20시리즈 M5 × 8 둥근머리 2 + 스프링너트 2, 구매)", Part.makeCompound(hw), (0.35, 0.35, 0.37))]
    for lab, shp, col in add:
        n = s2.addObject("Part::Feature", "B1b_%d" % len(s2.Objects))
        n.Shape, n.Label = shp, lab
        if App.GuiUp:
            n.ViewObject.ShapeColor = col
    _save(s2, os.path.join(OUT, "S2_마킹부.FCStd"))
    # ---------------- 고정 겹침 검사 (바뀐 것 ↔ 전부)
    every = []
    for f in ("S1_급이부", "S2_마킹부", "S3_프레임회로"):
        dd = App.openDocument(os.path.join(OUT, f + ".FCStd"), True)
        every += [(f[:2] + " " + o.Label, o.Shape.copy()) for o in dd.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull() and not o.Label.startswith("REF")]
        App.closeDocument(dd.Name)
    CH = ("213", "214", "215", "216", "217", "218", "153b", "153n", "195p_uln", "197", "198", "100h", "100i")
    probe = [(l, s) for l, s in every if l.split(" ", 1)[1].startswith(CH)]
    ok_pairs = (("213", "218_rod"), ("213", "222"), ("218s", "218_rod"), ("218s", "100"), ("217s", "217"), ("217s", "100"),
                ("215", "217_"), ("216", "217_"), ("214", "216"), ("216", "215"), ("153", "217_"), ("153", "215"),
                ("197", "100"), ("198", "197"), ("198", "195p"), ("100h", "197"), ("100h", "100"), ("100i", "100"))
    seen = set()
    for la, sa in probe:
        for lb, sb in every:
            if la == lb or (lb, la) in seen:
                continue
            a, b = la.split(" ", 1)[1], lb.split(" ", 1)[1]
            if any(a.startswith(p) and b.startswith(q) or a.startswith(q) and b.startswith(p) for p, q in ok_pairs):
                continue
            if sa.BoundBox.intersect(sb.BoundBox):
                try:
                    v = sa.common(sb).Volume
                except Exception:
                    v = 0.0
                if v > 0.05:
                    rep["hits"].append([la[:45], lb[:45], round(v, 1)]); seen.add((la, lb))
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_gantry_buy1b.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
