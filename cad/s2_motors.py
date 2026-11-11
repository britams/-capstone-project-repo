# -*- coding: utf-8 -*-
"""S2 마킹부: 28BYJ-48 모터 3개(153·209·215)를 진짜 모터 도면으로 (서현 11/12 01:06 "진짜 모터 도면을 가져와서 넣어", CAP-AI-62)

  freecad.exe cad/s2_motors.py   (따로 띄운 창, 작업 폴더 = cad) → split/_s2_motors.json
도면: Adafruit 858 (28BYJ-48 5 V) STEP, MIT — cad/vendor_mit/adafruit/858_28BYJ48.step
  STEP 좌표: 몸통 가운데 (0,0), 축 (0,8) +z, 귀 윗면 z 0
  우리 국부 좌표(D5e m28byj48): 원점 = 축 가운데·귀 면, +z 축, 몸통 가운데 (0,−8), 귀 x → STEP을 (0,−8,0) 옮기면 같음
자리는 지금 모델의 단순 모양에서 읽음 (몸통 원기둥 r14 축, 보스 r4.5 축, 귀 구멍 r2.1 두 개) — 스크립트 좌표를 다시 계산하지 않음.
축(153r·209r·215r)은 STEP의 축 고체로, 나머지(몸통·보스·선 상자·귀)는 153·209·215로.
"""
import json, os, sys, traceback
HERE = os.getcwd()
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, "split")
STEP = os.path.join(HERE, "vendor_mit", "adafruit", "858_28BYJ48.step")
MOTORS = (("153_floor_stepper", "153r_"), ("209_y_stepper", "209r_"), ("215_x_stepper", "215r_"))
rep = dict(ok=False, motors={})
try:
    import FreeCAD as App
    import Part
    V = App.Vector
    import split3 as S

    def cyls(shape, r):
        return [f for f in shape.Faces if "Cylinder" in str(type(f.Surface)) and abs(f.Surface.Radius - r) < 0.05]

    def frame(st):
        """단순 모양 → (원점, x, y, z) 세상 좌표"""
        boss = cyls(st, 4.5)[0]
        a = boss.Surface.Axis.normalize()
        com = st.CenterOfMass if hasattr(st, "CenterOfMass") else st.Solids[0].CenterOfMass
        ends = [e.Curve.Center for e in boss.Edges if "Circle" in str(type(e.Curve))]
        org = min(ends, key=lambda p: (p - com).Length)          # 보스 아래 끝 = 귀 면
        z = a if (org - com).dot(a) > 0 else -a                   # 몸통은 −z 쪽
        holes = cyls(st, 2.1)
        c = [h.Surface.Center for h in holes]
        c = [p - z * (p - org).dot(z) for p in c]                 # 귀 면으로 내림
        xs = (c[1] - c[0]).normalize()
        body = cyls(st, 14.0)[0].Surface.Center
        v = body - org; v = v - z * v.dot(z)                       # 축 → 몸통 가운데 (−y)
        y = (-v).normalize()
        x = y.cross(z)                                            # 귀는 x 대칭이라 xs 부호는 상관없음
        return org, x, y, z, round(v.Length, 2), round((c[1] - c[0]).Length, 2)

    raw = Part.read(STEP)
    shaft = [s for s in raw.Solids if abs(s.BoundBox.ZMax - 10.0) < 0.01 and s.BoundBox.XLength < 5.1][0]
    stator = Part.makeCompound([s for s in raw.Solids if not s.isSame(shaft)])

    def place(shp, org, x, y, z):
        s = shp.copy()
        s.translate(V(0, -8, 0))
        m = App.Matrix(x.x, y.x, z.x, org.x, x.y, y.y, z.y, org.y, x.z, y.z, z.z, org.z, 0, 0, 0, 1)
        s.transformShape(m)
        return s

    d = App.openDocument(os.path.join(OUT, "S2_마킹부.FCStd"))
    for st_pre, sh_pre in MOTORS:
        so = [o for o in d.Objects if o.Label.startswith(st_pre)][0]
        sh = [o for o in d.Objects if o.Label.startswith(sh_pre)]
        org, x, y, z, off, ear = frame(so.Shape)
        r = dict(origin=[round(org.x, 2), round(org.y, 2), round(org.z, 2)], z=[round(z.x, 3), round(z.y, 3), round(z.z, 3)], body_off=off, ear_pitch=ear,
                 old_vol=round(so.Shape.Volume))
        so.Shape = place(stator, org, x, y, z)
        so.Label = so.Label.split(" ")[0] + " (28BYJ-48 5 V — Adafruit 858 STEP, MIT)"
        if sh:
            sh[0].Shape = place(shaft, org, x, y, z)
        r["new_vol"] = round(so.Shape.Volume)
        rep["motors"][st_pre] = r
    # 겹침: 모터 ↔ S2 전부 + 둘레 (허용: 축 ↔ 커플링 끼움, 귀 볼트·너트 ↔ 귀, 축 ↔ 몸통)
    S.add_context(d, OUT)
    allow = (("153r", "154_"), ("209r", "210_"), ("215r", "216_"), ("153_", "153b"), ("153_", "153n"), ("209_", "153b"), ("215_", "153b"))
    hits = []
    mine = [o for o in d.Objects if o.Label.startswith(tuple(a for a, _ in MOTORS) + tuple(b for _, b in MOTORS))]
    for a in mine:
        for o in d.Objects:
            if o is a or o.TypeId != "Part::Feature" or o.Shape.isNull() or not a.Shape.BoundBox.intersect(o.Shape.BoundBox):
                continue
            if o in mine and o.Name < a.Name:
                continue
            v = a.Shape.common(o.Shape).Volume
            if v > 0.05:
                ka, kb = a.Label.split(" ")[0], o.Label.split(" ")[0]
                ok = any((ka.startswith(p) and kb.startswith(q)) or (kb.startswith(p) and ka.startswith(q)) for p, q in allow)
                hits.append((ka, kb, round(v, 2), "허용" if ok else "문제"))
    rep["overlaps"] = hits
    rep["bad"] = [h for h in hits if h[3] == "문제"]
    S.remove_context(d)
    S.color_doc(d)
    d.recompute()
    if not rep["bad"]:
        d.save()
        rep["saved"] = True
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
with open(os.path.join(OUT, "_s2_motors.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
