# -*- coding: utf-8 -*-
"""D5f 전기 배치 (서현, 2026-11-06, CAP-AI-23) — D5e 전체 조립 위에 11/02 결정을 자리로 표시

바뀐 것 (design/2026-11-02_전기계통_제어순서_서현.md, 2026-11-06_회로설계_서현.md)
- 190 Pi 5 + AI HAT+: 데크 위 → 같은 x·y에서 위판 아래 (z 565~600) — 카메라 CSI 300 mm
- 191 UNO 1 그대로 + 192 UNO 2를 15 mm 기둥 위에 겹침
- 193 단자대 + 퓨즈, 194 비상 정지 버튼, 195 ULN2003 ×3
- 204 펜 홀더 스프링 지움 (11/02 결정, 승준 Issue #7)
- 28BYJ-48 고정은 M4 × 2 (귀 구멍 Ø4.2) — 볼트 수량은 승준 목록
- 196 빛 게이트 9쌍: 문마다 2개(문판 앞·뒤 각 2 mm) + G1·G4·G6 — 송신·수신 블록과 빔(빨간 선)
모양은 '자리 표시'다 (블록). 브래킷·구멍 모양은 D5f 다음 단계에서 설계한다.

실행 (FreeCAD GUI):
    import sys; sys.path.insert(0, r"<repo>/cad"); import D5f_electrical_layout as E; doc = E.make(); E.render_all(doc, r"<repo>/cad")
"""
import FreeCAD as App
import Part

import D5e_full_assembly as A
import D5e_module_kinematic as K

V = App.Vector
DOC = "D5f_electrical_layout"
DT = K.DECK_TOP          # 205

# 빛 게이트: (이름, 중심 x, y, z, 빔 방향 'y' 또는 'x', 통로 반지름)
GATES = [
    ("G4", 0, 0, 570, "x", 6),                       # G1은 D5e 114_entry_sensor 그대로
    ("G6", 120, 0, 377, "z", 8),                      # 방생 서보(−y)를 피해 위아래로
]
# 문 빔 (11/06): 문판 슬롯 면에서 2 mm 바깥, 통로 가운데(y 0)를 위아래(z)로 지나감.
# 하우징 위·아래 벽에 Ø4.2 구멍 → 3 mm IR LED(몸통 Ø4 × 8 [추측 — 실물 확인]) 를 끼움
#   입구 문 위 LED는 입구 하우징 윗벽(3 mm) + 격리 하우징과의 틈(5 mm)에, 격리 문 아래 LED는 격리 하우징 아랫벽(8 mm)에 → 겹치지 않음
DOOR_BEAMS = {  # 하우징 이름: (zp, [(게이트, x)])
    "112_entry_gate_housing": (349, [("G2", 23), ("G2b", 29)]),
    "170_isolation_gate_housing": (377, [("G3", 29), ("G3b", 23)]),
    "176_release_gate_housing": (377, [("G5", 81), ("G5b", 87)]),
}


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def parts():
    p = {}
    p["190_pi5_aihat (위판 아래, D5f)"] = (box(-125, -40, 15, 65, 565, 600), (0.20, 0.55, 0.30))
    p["192_arduino_uno2 (UNO 1 위 15 mm)"] = (box(-125, -56.4, -75, -21.6, DT + 15, DT + 30), (0.10, 0.45, 0.75))
    p["193_terminal_fuse"] = (box(-50, -10, -72, -58, DT, DT + 14), (0.85, 0.20, 0.20))
    p["194_estop"] = (Part.makeCylinder(15, 30, V(-100, 45, DT)), (0.90, 0.10, 0.10))
    p["195_uln2003_F"] = (box(37.5, 72.5, -66, -34, DT, DT + 6), (0.10, 0.60, 0.20))
    # ULN2003 X·Y: 갠트리 쪽 2020 기둥(x 160~180) 바깥면에 세워 붙임 (모터 선 240 mm 안)
    p["195_uln2003_X"] = (box(181, 187, -46, -14, 415, 450), (0.10, 0.60, 0.20))
    p["195_uln2003_Y"] = (box(181, 187, 0, 32, 430, 465), (0.10, 0.60, 0.20))
    for hname, (zp, beams) in DOOR_BEAMS.items():
        for g, x in beams:
            led = Part.makeCylinder(2.0, 8, V(x, 0, zp - 14)).fuse(Part.makeCylinder(2.0, 8, V(x, 0, zp + 6)))
            p["196_gate_%s_led (위·아래)" % g] = (led, (0.25, 0.25, 0.25))
            p["196_gate_%s_beam" % g] = (Part.makeCylinder(0.6, 12, V(x, 0, zp - 6)), (1.0, 0.0, 0.0))
    for g, x, y, z, ax, r in GATES:
        d = r + 4
        if ax == "y":
            tx = box(x - 2.5, x + 2.5, -d - 6, -d, z - 3, z + 3)
            rx = box(x - 2.5, x + 2.5, d, d + 6, z - 3, z + 3)
            beam = Part.makeCylinder(0.6, 2 * d, V(x, -d, z), V(0, 1, 0))
        elif ax == "z":
            tx = box(x - 2.5, x + 2.5, y - 3, y + 3, z + d, z + d + 6)
            rx = box(x - 2.5, x + 2.5, y - 3, y + 3, z - d - 6, z - d)
            beam = Part.makeCylinder(0.6, 2 * d, V(x, y, z - d), V(0, 0, 1))
        else:
            tx = box(-d - 6, -d, y - 2.5, y + 2.5, z - 3, z + 3)
            rx = box(d, d + 6, y - 2.5, y + 2.5, z - 3, z + 3)
            beam = Part.makeCylinder(0.6, 2 * d, V(-d, y, z), V(1, 0, 0))
        p["196_gate_%s_tx_rx" % g] = (tx.fuse(rx), (0.25, 0.25, 0.25))
        p["196_gate_%s_beam" % g] = (beam, (1.0, 0.0, 0.0))
    return p


def make():
    A.DOC = DOC
    doc = A.make_full()
    for o in doc.Objects:
        if o.Label == "190_pi5_aihat":
            o.ViewObject.Visibility = False        # 옛 자리 (데크 위) 숨김
            o.Label = "190_pi5_aihat (D5e 옛 자리, 숨김)"
    for o in list(doc.Objects):                     # 11/02 결정: 펜 홀더 스프링 204 뺌 (승준 Issue #7-4)
        if o.Label.startswith("204_"):
            doc.removeObject(o.Name)
    for o in doc.Objects:                           # 문 하우징 위·아래 벽에 빔 구멍
        if o.Label in DOOR_BEAMS:
            zp, beams = DOOR_BEAMS[o.Label]
            sh = o.Shape
            for g, x in beams:
                sh = sh.cut(Part.makeCylinder(2.1, 30, V(x, 0, zp - 16)))
            o.Shape = sh.removeSplitter()
            o.Label = o.Label + " (D5f 빔 구멍)"
    grp = doc.addObject("App::DocumentObjectGroup", "G19x_electrical")
    grp.Label = "19x 전기 배치 (D5f, 자리 표시)"
    for i, (nm, (shp, col)) in enumerate(parts().items()):
        o = doc.addObject("Part::Feature", "E%02d" % i)
        o.Label = nm
        o.Shape = shp
        grp.addObject(o)
        if App.GuiUp:
            o.ViewObject.ShapeColor = col
    doc.recompute()
    return doc


VIEWS = [
    ("전기배치_등각", "iso", (-140, 190, -110, 110, 190, 620), ("REF_trap_container", "REF_trap_cap", "REF_trap_silicone_star", "105_top_plate", "104_dome_coupling")),
    ("전기배치_정면", "front", (-140, 190, -110, 110, 190, 620), ("REF_trap_container", "REF_trap_cap", "REF_trap_silicone_star", "105_top_plate", "104_dome_coupling")),
    ("문빔_위", "top", (-20, 130, -40, 40, 330, 400), ("REF_trap_container", "REF_trap_cap", "REF_trap_silicone_star", "105_top_plate", "104_dome_coupling")),
]


def render_all(doc, out_dir):
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.setAnimationEnabled(False)
    Gui.ActiveDocument.ActiveView.setCameraType("Orthographic")
    out = []
    for v in VIEWS:
        p = A.render(doc, out_dir, v)
        np_ = p.replace("D5e_", "D5f_")
        import os
        if os.path.exists(np_):
            os.remove(np_)
        os.rename(p, np_)
        out.append(np_)
    doc.saveAs("%s/%s.FCStd" % (out_dir, DOC))
    return out


def check(doc):
    """새 블록·LED가 모듈 부품과 겹치는지 (부피 > 0.5 mm³). 프레임·트랩은 뺌."""
    ours = [o for o in doc.Objects if o.Name.startswith("E") and o.TypeId == "Part::Feature"]
    others = [o for o in doc.Objects if o.TypeId == "Part::Feature" and not o.Name.startswith("E") and o.Shape.Volume > 0
              and not o.Label.startswith(("REF", "100_", "190_"))]
    hits = []
    for a in ours:
        if "beam" in a.Label:
            continue
        for b in others:
            if a.Shape.BoundBox.intersect(b.Shape.BoundBox):
                v = a.Shape.common(b.Shape).Volume
                if v > 0.5:
                    hits.append((a.Label, b.Label, round(v, 1)))
    return hits
