# -*- coding: utf-8 -*-
"""28BYJ-48 모터를 진짜 도면(Adafruit 858 STEP, MIT)으로 바꾸기 — 어느 문서에나 (CAP-AI-62, 서현 11/12)

  replace(doc) : 153·209·215 몸통과 153r·209r·215r 축을 바꿈. 자리는 지금의 단순 모양에서 읽음.
                 이미 바뀐 것(라벨에 'Adafruit 858')은 건너뜀.
  overlaps(doc, allow) : 바꾼 모터 ↔ 문서 전부 (고체 하나씩, 상자 겹치는 것만)
쓰는 곳: s2_motors.py (S2), full_motors.py (D5g_full), D5g_frame_detail.make() 끝 (다시 만들 때)
STEP 좌표: 몸통 가운데 (0,0), 축 (0,8) +z, 귀 윗면 z 0 → 우리 국부(축 가운데·귀 면 원점, 몸통 (0,−8))로 (0,−8,0) 옮김
"""
import os
import FreeCAD as App
import Part

V = App.Vector
STEP = os.path.join(os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd(), "vendor_mit", "adafruit", "858_28BYJ48.step")
MOTORS = (("153_floor_stepper", "153r_"), ("209_y_stepper", "209r_"), ("215_x_stepper", "215r_"))
TAG = "Adafruit 858"


def _cyls(shape, r):
    return [f for f in shape.Faces if "Cylinder" in str(type(f.Surface)) and abs(f.Surface.Radius - r) < 0.05]


def frame(st):
    """단순 모양 → (원점, x, y, z) — 보스 r4.5 축, 몸통 r14, 귀 구멍 r2.1"""
    boss = _cyls(st, 4.5)[0]
    a = boss.Surface.Axis.normalize()
    com = st.Solids[0].CenterOfMass
    ends = [e.Curve.Center for e in boss.Edges if "Circle" in str(type(e.Curve))]
    org = min(ends, key=lambda p: (p - com).Length)               # 보스 아래 끝 = 귀 면
    z = a if (org - com).dot(a) > 0 else -a                       # 몸통은 −z 쪽
    body = _cyls(st, 14.0)[0].Surface.Center
    v = body - org
    v = v - z * v.dot(z)                                           # 축 → 몸통 가운데 (국부 −y)
    y = (-v).normalize()
    x = y.cross(z)                                                 # 귀는 x 대칭 — 부호 상관없음
    return org, x, y, z, round(v.Length, 2)


def _parts():
    raw = Part.read(STEP)
    shaft = [s for s in raw.Solids if abs(s.BoundBox.ZMax - 10.0) < 0.01 and s.BoundBox.XLength < 5.1][0]
    stator = Part.makeCompound([s for s in raw.Solids if not s.isSame(shaft)])
    return stator, shaft


def _place(shp, org, x, y, z):
    """(11/12) 모양 안에 좌표를 구워 넣음 (Placement는 단위) — 다시 만들기에서 209만 원점으로 돌아간 일이 있었음 (원인 못 찾음)"""
    m = App.Matrix(x.x, y.x, z.x, org.x, x.y, y.y, z.y, org.y, x.z, y.z, z.z, org.z, 0, 0, 0, 1)
    t = App.Matrix()
    t.move(V(0, -8, 0))
    return shp.transformGeometry(m.multiply(t))


def replace(doc):
    stator, shaft = _parts()
    rep = {}
    for st_pre, sh_pre in MOTORS:
        so = [o for o in doc.Objects if o.Label.startswith(st_pre)]
        if not so:
            rep[st_pre] = "없음"
            continue
        so = so[0]
        if TAG in so.Label:
            rep[st_pre] = "이미 바뀜"
            continue
        org, x, y, z, off = frame(so.Shape)
        old = round(so.Shape.Volume)
        so.Placement = App.Placement()
        so.Shape = _place(stator, org, x, y, z)
        so.Label = so.Label.split(" ")[0] + " (28BYJ-48 5 V — %s STEP, MIT)" % TAG
        for sh in [o for o in doc.Objects if o.Label.startswith(sh_pre)]:
            sh.Placement = App.Placement()
            sh.Shape = _place(shaft, org, x, y, z)
        rep[st_pre] = dict(origin=[round(org.x, 2), round(org.y, 2), round(org.z, 2)], z=[round(z.x, 3), round(z.y, 3), round(z.z, 3)],
                           body_off=off, old_vol=old, new_vol=round(so.Shape.Volume))
    doc.recompute()
    return rep


def overlaps(doc, allow=(("153r", "154_"), ("209r", "210_"), ("215r", "216_"))):
    pres = tuple(a for a, _ in MOTORS) + tuple(b for _, b in MOTORS)
    mine = [o for o in doc.Objects if o.Label.startswith(pres)]
    hits = []
    for a in mine:
        for o in doc.Objects:
            if o is a or o.TypeId != "Part::Feature" or o.Shape.isNull() or not a.Shape.BoundBox.intersect(o.Shape.BoundBox):
                continue
            if o in mine and o.Name < a.Name:
                continue
            ka, kb = a.Label.split(" ")[0], o.Label.split(" ")[0]
            try:                                           # 고체 하나씩 (묶음째 common은 닿는 면에서 Null shape, 11/12)
                v = sum(sa.common(o.Shape).Volume for sa in a.Shape.Solids if sa.BoundBox.intersect(o.Shape.BoundBox))
            except Exception as e:
                hits.append((ka, kb, "ERR %s" % e, "확인"))
                continue
            if v > 0.05:
                ok = any((ka.startswith(p) and kb.startswith(q)) or (kb.startswith(p) and ka.startswith(q)) for p, q in allow)
                hits.append((ka, kb, round(v, 2), "허용" if ok else "문제"))
    return hits
