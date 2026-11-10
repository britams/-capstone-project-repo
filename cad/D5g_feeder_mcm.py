# -*- coding: utf-8 -*-
"""급이 방 나사·인서트·T너트를 McMaster 실제 3D(STEP)로 바꾸고 검사 (서현, 2026-11-10, CAP-AI-57)

D5g_frame_detail.make() 끝에서 부름: FM.apply(doc) → 보고 dict
STEP 파일: cad/vendor_step/<부품번호>.STEP — McMaster 페이지에서 '3-D STEP'으로 받은 것 (레포에 안 올림: McMaster CAD는 '참고용' 배포
  조건이고 공개 레포라서. 없으면 McMaster 표 치수로 단순 모양을 대신 넣고 보고에 적음)
부품 [확실 — McMaster 페이지 표, 11/10 확인]
  94459A130 열 압입 인서트 M3 × 0.5, 설치 길이 4.3, 구멍 최대 Ø4, 최소 두께 5.1 (STEP: 바깥 Ø4.74, 작은 끝 Ø3.74)  × 4 (뚜껑 기둥)
  92545A111 손나사 M3 × 8, 머리 Ø8 × 5, 나사산 6.5 (머리 밑 1.5 민짜)                                              × 4 (뚜껑)
  92000A118 냄비머리 십자 M3 × 8, 머리 Ø6 × 2.5, PH1                                                              × 2 (데크 아래 → 발 인서트)
  94459A130 (위와 같음)                                                                                           × 2 (발)
  (처음 안: 위에서 M5 × 14 92000A324 + 와셔 93475A240 + 가로대 T너트 4976N25 — 볼트 위가 그릇이라 드라이버가 못 들어가고,
   옆으로 옮기면 서보 허브·로드셀에 막혀서 바꿈. STEP은 vendor_step에 남겨 둠)
  (11/06의 M3 × 8 볼트 2개 + 마킹실 벽 인서트 2개는 없앰 — D5g_feeder_uln.py FDX ears=False)
"""
import os

import FreeCAD as App
import Part

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
STEP_DIR = os.path.join(HERE, "vendor_step")
BRASS, STEEL, ZINC = (0.80, 0.65, 0.25), (0.75, 0.75, 0.78), (0.82, 0.84, 0.86)

# STEP 안 기준점 (서현 PC에서 STEP을 열어 잰 값, 11/10)
REF = {
    "94459A130": dict(axis="y", big_end=2.15, small_end=-2.15),          # 큰 끝(+y)이 위로 — 판에 맞춤
    "92545A111": dict(axis="z", under=1.5, tip=-6.5),                    # 머리 밑면 z 1.5
    "92000A324": dict(axis="z", under=5.05, tip=-8.95),
    "92000A118": dict(axis="z", under=2.75, tip=-5.25),
    "4976N25": dict(axis="y", half_t=1.6),                               # 구멍 축 y, 길이 x 17.3, 폭 z 10.4
}


def _step(pn):
    p = os.path.join(STEP_DIR, pn + ".STEP")
    return Part.read(p) if os.path.exists(p) else None


def _insert(top, missing):
    s = _step("94459A130")
    if s is None:
        missing.append("94459A130")
        s = Part.makeCylinder(2.35, 4.3, V(0, -2.15, 0), V(0, 1, 0))
    s = s.copy()
    s.rotate(V(0, 0, 0), V(1, 0, 0), 90)            # +y → +z (큰 끝 위)
    s.translate(top - V(0, 0, REF["94459A130"]["big_end"]))
    return s


def _screw(pn, under_at, missing, alt):
    s = _step(pn)
    if s is None:
        missing.append(pn)
        s = alt
    s = s.copy()
    s.translate(under_at - V(0, 0, REF[pn]["under"]))
    return s


def _tnut(center, missing):
    s = _step("4976N25")
    if s is None:
        missing.append("4976N25")
        s = Part.makeBox(17.3, 3.2, 10.4, V(-8.65, -1.6, -5.2))
    s = s.copy()
    s.rotate(V(0, 0, 0), V(1, 0, 0), 90)            # 구멍 축 y → z, 폭(z) → y
    s.translate(center)
    return s


def _washer(p):
    return Part.makeCylinder(5.0, 1.0, p).cut(Part.makeCylinder(2.65, 3, p - V(0, 0, 1)))


def _add(doc, label, shp, col):
    for o in [o for o in doc.Objects if o.Label.startswith(label.split(" ")[0])]:
        doc.removeObject(o.Name)
    o = doc.addObject("Part::Feature", "F" + label.split(" ")[0].replace("-", "_"))
    o.Label, o.Shape = label, shp
    if getattr(o, "ViewObject", None):
        o.ViewObject.ShapeColor = col
    return o


def apply(doc):
    import D5g_feeder_uln as FU
    f, e, ins = FU.FD, FU.FDX, FU.INS
    missing, rep = [], {}
    # --- 1) 뚜껑: 인서트 4 + 손나사 4
    lid_top = f["wall_top"] + 2.0
    I, T = [], []
    for sx in (-1, 1):
        for cy in e["lid_y"]:
            cx = f["x"] + sx * e["lid_dx"]
            I.append(_insert(V(cx, cy, f["wall_top"]), missing))
            alt = Part.makeCylinder(1.5, 8, V(0, 0, -6.5)).fuse(Part.makeCylinder(4, 5, V(0, 0, 1.5)))
            T.append(_screw("92545A111", V(cx, cy, lid_top), missing, alt))
    for pre in ("143s_",):
        for o in [o for o in doc.Objects if o.Label.startswith(pre)]:
            doc.removeObject(o.Name)
    _add(doc, "143i_insert_M3_heatset (McMaster 94459A130 — STEP, 뚜껑 기둥 4개)", Part.makeCompound(I), BRASS)
    _add(doc, "143t_thumbscrew_M3x8 (McMaster 92545A111 — STEP, 4개, 손으로 돌림)", Part.makeCompound(T), STEEL)
    # --- 2) 발
    px = f["x"] + f["post_dx"]
    # (11/10) 발은 데크 아래에서 M3 × 8 (92000A118) → 발 속 인서트 94459A130 (큰 끝이 아래 = 나사 들어오는 쪽)
    deck_bot = f["post_foot_z"] - 5.0                      # 200
    FI, FB = [], []
    for sy in (-FU.FOOT["dy"], FU.FOOT["dy"]):
        x, y = px, f["post_y"] + sy
        s = _insert(V(0, 0, 0), missing)                   # 큰 끝 z 0, 작은 끝 −4.3 → 뒤집어 큰 끝을 발 아래 면에
        s.rotate(V(0, 0, 0), V(1, 0, 0), 180)
        s.translate(V(x, y, f["post_foot_z"]))
        FI.append(s)
        alt = Part.makeCylinder(1.5, 8, V(0, 0, 2.75 - 8)).fuse(Part.makeCylinder(3, 2.5, V(0, 0, 2.75)))
        b = _screw("92000A118", V(0, 0, 0), missing, alt)  # 머리 밑 z 0, 머리 +z → 뒤집어 머리를 아래로
        b.rotate(V(0, 0, 0), V(1, 0, 0), 180)
        b.translate(V(x, y, deck_bot))
        FB.append(b)
    _add(doc, "143fi_insert_M3_foot (McMaster 94459A130 — STEP, 발 2개)", Part.makeCompound(FI), BRASS)
    _add(doc, "143f_screw_M3x8_pan (McMaster 92000A118 — STEP, 데크 아래에서 2개)", Part.makeCompound(FB), STEEL)
    for pre in ("143w_", "143n_"):
        for o in [o for o in doc.Objects if o.Label.startswith(pre)]:
            doc.removeObject(o.Name)
    doc.recompute()
    rep["missing_step"] = missing
    rep.update(check(doc))
    return rep


def check(doc):
    """겹침(나사산 물림은 따로 셈), 물림 길이, 끝 여유, 인서트 벽, 손가락 자리, T너트 홈"""
    import D5g_feeder_uln as FU
    f, e, ins = FU.FD, FU.FDX, FU.INS
    r = {}
    mine = [o for o in doc.Objects if o.Label.startswith(("143i_", "143t_", "143f_", "143fi_"))]
    others = [o for o in doc.Objects if o.TypeId == "Part::Feature" and o not in mine and not o.Shape.isNull()
              and o.Shape.Volume > 0 and not o.Label.startswith(("REF", "FitBox")) and "beam" not in o.Label]
    ov = []
    for a in mine:
        for b in others + [m for m in mine if m.Name > a.Name]:
            if a.Shape.BoundBox.intersect(b.Shape.BoundBox):
                v = a.Shape.common(b.Shape).Volume
                if v > 0.01:
                    ov.append((a.Label.split(" ")[0], b.Label.split(" ")[0], round(v, 2)))
    r["overlaps"] = ov
    # 물림·여유 (숫자 — 위 배치식 그대로)
    top = f["wall_top"]
    r["lid"] = dict(insert=(round(top - ins["L"], 2), top), screw_tip=round(top + 2 - 8, 2), hole_bottom=top - ins["depth"],
                    engage=ins["L"], tip_to_bottom=round((top + 2 - 8) - (top - ins["depth"]), 2),
                    insert_wall=round(ins["boss_r"] - 2.37, 2), boss_depth=ins["depth"], need_depth=5.1)
    fz = f["post_foot_z"]
    r["foot"] = dict(deck=(fz - 5, fz), insert=(fz, fz + 4.3), screw_tip=fz - 5 + 8, engage=round(min(4.3, 8 - 5), 2),
                     foot_top=fz + FU.FOOT["t"], tip_to_foot_top=round(fz + FU.FOOT["t"] - (fz + 3), 2), need_depth=5.1)
    # 손가락 자리: 손나사 머리 둘레 반지름 12, 높이 머리 + 15 에 닿는 고정 부품 (뚜껑 빼고)
    fing = []
    for sx in (-1, 1):
        for cy in e["lid_y"]:
            c = Part.makeCylinder(12, 20, V(f["x"] + sx * e["lid_dx"], cy, top + 2)).cut(Part.makeCylinder(4.5, 21, V(f["x"] + sx * e["lid_dx"], cy, top + 1.5)))
            for b in others:
                if b.Label.startswith("143l_"):
                    continue
                if c.BoundBox.intersect(b.Shape.BoundBox) and c.common(b.Shape).Volume > 1:
                    fing.append(((round(f["x"] + sx * e["lid_dx"]), cy), b.Label.split(" ")[0]))
    r["finger_blockers"] = fing
    # 드라이버 자리: 발 나사 머리 아래로 PH1 축 Ø4.5 × 110 mm (데크를 프레임에 올리기 전 — 데크·가로대는 빼고 봄)
    px = f["x"] + f["post_dx"]
    drv = []
    for sy in (-FU.FOOT["dy"], FU.FOOT["dy"]):
        c = Part.makeCylinder(2.25, 110, V(px, f["post_y"] + sy, f["post_foot_z"] - 5 - 2.5 - 0.2), V(0, 0, -1))
        for b in others:
            if b.Label.startswith(("101_deck",)):
                continue
            if c.BoundBox.intersect(b.Shape.BoundBox) and c.common(b.Shape).Volume > 0.5:
                drv.append((f["post_y"] + sy, b.Label.split(" ")[0]))
    r["driver_blockers"] = drv
    return r
