# -*- coding: utf-8 -*-
"""D5f 전기 배치 (서현, 2026-11-06, CAP-AI-23) — D5e 전체 조립 위에 11/02 결정을 자리로 표시

바뀐 것 (design/2026-11-02_전기계통_제어순서_서현.md, 2026-11-06_회로설계_서현.md)
- 190 Pi 5 + AI HAT+: 데크 위 → 같은 x·y에서 위판 아래 (z 565~600) — 카메라 CSI 300 mm
- 191 UNO 1 그대로 + 192 UNO 2를 15 mm 기둥 위에 겹침
- 193 단자대 + 퓨즈, 194 비상 정지 버튼, 195 ULN2003 ×3
- 204 펜 홀더 스프링 지움 (11/02 결정, 승준 Issue #7)
- 28BYJ-48 고정은 M4 × 2 (귀 구멍 Ø4.2) — 볼트 수량은 승준 목록
- 196 빛 게이트 9쌍: 문마다 2개(문판 앞·뒤 각 2 mm) + G1·G4·G6 — 송신·수신 블록과 빔(빨간 선)
- (11/06 18:38, CAP-AI-27) 바닥 안내 바꿈 — 서현 "최대한 기성품으로, 바꿔":
  밀대(147)를 Ø4 × 80 경화 직선 축(기성품)으로, 안내를 LM4UU(기성품, Ø4/Ø8 × 12)로. LM4UU는 캐리지(158, 두께 12)에 끼움.
  로드셀(148)·스프링(146)은 캐리지 아래 컵(158에 한 몸으로 출력) 안으로: 컵 바닥 → 로드셀(버튼 위) → 스프링(구멍 Ø4.4 안내) → 축 아래 끝.
  축 자리는 (65, 4): 나사 축 커플링·너트 플랜지·가이드봉을 피하는 자리. 바닥판 121은 Ø6 비접촉 구멍, 가운데 Ø5 구멍은 막음.
  → 말벌이 벗어나 생기는 모멘트는 캐리지 안내(너트·가이드봉)가 받고, 힘 측정 길(축-LM4UU)에는 볼 마찰만 남음
     (역학계산 2차 A: 98 % 이상, design/2026-11-06_S4_스프링146_역학계산_2차_서현.md)
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


# 바닥 안내 (11/06 18:38) — 기성품: 축 Ø4 × 80 (경화, h6), LM4UU, 스프링(카탈로그, 바깥 ≤ 4.1), 버튼 로드셀
FG = dict(x=65.0, y=4.0, zc=262.0, zf=335.0, shaft_r=2.0, shaft_len=80.0, lm_r=4.0, lm_ri=2.0, lm_len=12.0,
          cup_r=7.5, cup_bot=236.0, lc_r=6.0, lc_h=6.0, lc_pocket_r=6.2, bore_r=2.2,
          sp_ro=1.43, sp_ri=1.20, base_clear_r=3.0, insert=3.0, stroke=36.5)
FLOOR_GROUP = ("140_", "146_", "147_", "148_", "149_", "158_", "159_")   # 바닥과 같이 오르내리는 부품


def cylz(r, h, x, y, z):
    return Part.makeCylinder(r, h, V(x, y, z))


def floor_guide(doc):
    """D5e의 146·147·148을 지우고 기성품 안내로 바꿈 (자세: 대기, 캐리지 아래 면 zc 262)"""
    f = FG
    x, y = f["x"], f["y"]
    z_lc = f["cup_bot"] + 2.0                               # 로드셀 아래 면 238
    z_sp = z_lc + f["lc_h"]                                 # 스프링 아래 끝 244
    z_sh = f["zf"] + f["insert"] - f["shaft_len"]           # 축 아래 끝 258
    for o in list(doc.Objects):
        if o.Label.split(" ")[0] in ("146_spring", "147_push_rod", "148_load_cell"):
            doc.removeObject(o.Name)
    for o in doc.Objects:
        lab = o.Label.split(" ")[0]
        if lab == "158_carriage":
            sh = o.Shape.cut(cylz(f["lm_r"], f["lm_len"] + 2, x, y, f["zc"] - 1))                 # LM4UU 자리
            cup = cylz(f["cup_r"], f["zc"] - f["cup_bot"], x, y, f["cup_bot"])
            cup = cup.cut(cylz(f["lc_pocket_r"], f["lc_h"] + 0.5, x, y, z_lc))                       # 로드셀 자리
            cup = cup.cut(cylz(f["bore_r"], f["zc"] - z_sp + 1, x, y, z_sp))                         # 스프링 구멍 Ø4.4
            cup = cup.cut(Part.makeBox(9, 3, 4, V(x, y - 1.5, z_lc)))                               # 로드셀 선 구멍 (+x)
            o.Shape = sh.fuse(cup).removeSplitter()
            o.Label = "158_carriage (D5f: LM4UU 자리 + 아래 컵)"
        elif lab == "121_chamber_base":
            sh = o.Shape.fuse(cylz(2.5, 5, 55, 0, 330)).cut(cylz(f["base_clear_r"], 12, x, y, 325))
            o.Shape = sh.removeSplitter()
            o.Label = "121_chamber_base (D5f: 가운데 구멍 막음, Ø6 비접촉 구멍)"
        elif lab == "140_lift_floor":
            sh = o.Shape.fuse(cylz(2.0, 3, 55, 0, f["zf"])).cut(cylz(f["shaft_r"], f["insert"], x, y, f["zf"]))
            o.Shape = sh.removeSplitter()
            o.Label = "140_lift_floor (D5f: 축 자리 (65, 4))"
    new = {
        "147_shaft_D4x80 (기성품 경화 축)": (cylz(f["shaft_r"], f["shaft_len"], x, y, z_sh), (0.75, 0.75, 0.78)),
        "149_LM4UU (기성품 볼 부싱)": (cylz(f["lm_r"], f["lm_len"], x, y, f["zc"]).cut(cylz(f["lm_ri"], f["lm_len"] + 2, x, y, f["zc"] - 1)), (0.55, 0.55, 0.6)),
        "146_spring (기성품, 바깥 2.86 자리)": (cylz(f["sp_ro"], z_sh - z_sp, x, y, z_sp).cut(cylz(f["sp_ri"], z_sh - z_sp + 2, x, y, z_sp - 1)), (0.85, 0.65, 0.1)),
        "148_load_cell (기성품 버튼형)": (cylz(f["lc_r"], f["lc_h"], x, y, z_lc), (0.3, 0.3, 0.3)),
    }
    grp = doc.addObject("App::DocumentObjectGroup", "G14x_floor_guide")
    grp.Label = "14x 바닥 안내 (D5f, 기성품)"
    for i, (nm, (shp, col)) in enumerate(new.items()):
        o = doc.addObject("Part::Feature", "FG%02d" % i)
        o.Label = nm
        o.Shape = shp
        grp.addObject(o)
        if App.GuiUp:
            o.ViewObject.ShapeColor = col
    doc.recompute()


def check_floor(doc, lift=(0.0, 18.25, 36.5)):
    """바닥 무리를 0 / 중간 / 끝까지 올려 고정 부품과 겹침 (부피 > 0.5 mm³). 모터 축 회전 부품(153r·154·155)은 고정으로 봄"""
    move = [o for o in doc.Objects if o.TypeId == "Part::Feature" and o.Label.startswith(FLOOR_GROUP)]
    fixed = [o for o in doc.Objects if o.TypeId == "Part::Feature" and o not in move and o.Shape.Volume > 0
             and not o.Label.startswith(("REF", "100_", "190_", "FitBox")) and "beam" not in o.Label]
    hits = []
    for dz in lift:
        for a in move:
            sa = a.Shape.copy()
            sa.translate(V(0, 0, dz))
            for b in fixed:
                if sa.BoundBox.intersect(b.Shape.BoundBox):
                    v = sa.common(b.Shape).Volume
                    if v > 0.5:
                        hits.append((dz, a.Label, b.Label, round(v, 1)))
        # 바닥 무리끼리 (스프링·축·컵·LM4UU)
    inner = []
    for i, a in enumerate(move):
        for b in move[i + 1:]:
            if a.Shape.BoundBox.intersect(b.Shape.BoundBox):
                v = a.Shape.common(b.Shape).Volume
                if v > 0.5:
                    inner.append((a.Label, b.Label, round(v, 1)))
    return hits, inner


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
    floor_guide(doc)
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
    ("바닥안내_정면", "front", (25, 85, -30, 30, 225, 345), ("REF_trap_container", "REF_trap_cap", "REF_trap_silicone_star", "105_top_plate", "104_dome_coupling", "120_chamber_walls", "151_drive_side_L", "151_drive_side_R")),
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
