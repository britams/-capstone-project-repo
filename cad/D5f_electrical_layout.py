# -*- coding: utf-8 -*-
"""D5f 전기 배치 (서현, 2026-11-06, CAP-AI-23) — D5e 전체 조립 위에 11/02 결정을 자리로 표시

바뀐 것 (design/2026-11-02_전기계통_제어순서_서현.md, 2026-11-06_회로설계_서현.md)
- 190 Pi 5 + AI HAT+: 데크 위 → 같은 x·y에서 위판 아래 (z 565~600) — 카메라 CSI 300 mm
- 191 UNO 1 그대로 + 192 UNO 2를 15 mm 기둥 위에 겹침
- 193 단자대 + 퓨즈, 194 비상 정지 버튼, 195 ULN2003 ×3
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
    ("G1", 0, 0, 275, "x", 6), ("G4", 0, 0, 570, "x", 6),
    ("G2", 24, 0, 349, "y", 6), ("G2b", 28, 0, 349, "y", 6),
    ("G3", 28, 0, 377, "y", 6), ("G3b", 24, 0, 377, "y", 6),
    ("G5", 82, 0, 377, "y", 6), ("G5b", 86, 0, 377, "y", 6), ("G6", 115, 0, 377, "y", 6),
]


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def parts():
    p = {}
    p["190_pi5_aihat (위판 아래, D5f)"] = (box(-125, -40, 15, 65, 565, 600), (0.20, 0.55, 0.30))
    p["192_arduino_uno2 (UNO 1 위 15 mm)"] = (box(-125, -56.4, -75, -21.6, DT + 15, DT + 30), (0.10, 0.45, 0.75))
    p["193_terminal_fuse"] = (box(-50, -10, -72, -58, DT, DT + 14), (0.85, 0.20, 0.20))
    p["194_estop"] = (Part.makeCylinder(15, 30, V(-100, 45, DT)), (0.90, 0.10, 0.10))
    p["195_uln2003_F"] = (box(37.5, 72.5, -66, -34, DT, DT + 6), (0.10, 0.60, 0.20))
    p["195_uln2003_X"] = (box(150, 170, -46, -14, 415, 450), (0.10, 0.60, 0.20))
    p["195_uln2003_Y"] = (box(150, 170, 0, 32, 430, 465), (0.10, 0.60, 0.20))
    for g, x, y, z, ax, r in GATES:
        d = r + 4
        if ax == "y":
            tx = box(x - 2.5, x + 2.5, -d - 6, -d, z - 3, z + 3)
            rx = box(x - 2.5, x + 2.5, d, d + 6, z - 3, z + 3)
            beam = Part.makeCylinder(0.6, 2 * d, V(x, -d, z), V(0, 1, 0))
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
