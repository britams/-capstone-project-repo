# -*- coding: utf-8 -*-
"""D5g 회로 기판 자세히 (2026-11-08, 승준, CAP-AI-SJ-53) — 승준 지적 2번 '회로를 인터넷 참고해서 자세하게'

1) 서보 허브(60 × 40)·게이트 허브(70 × 30) 만능기판: 서현 `전기회로/hub_boards.py`(CAP-AI-50, 넷 대조 통과)의 배치를 그대로 읽어
   구멍 2.54 격자, 헤더 핀, 세운 저항(220 Ω·10 kΩ), 콘덴서(0.1 µF·1000 µF), 쇼트키 SB540, 납땜 면 버스선·땜납 다리, 부품 면 점퍼를 그림.
   (레포 원본을 GitHub에서 받아 씀 → hub_boards.py 가 바뀌면 다시 만들 때 따라 바뀜)
2) MOSFET 모듈 SZH-AT021: 판매 사진(디바이스마트 1361314) 보고 배치 — 빨간 기판 66.8 × 66.8, 한쪽 가장자리 초록 나사 단자 10극(2극 × 5),
   그 안쪽 IRF540N(TO-220) 4개 눕힘, 가운데 SOIC-16 칩, 반대쪽 3핀 커넥터 4개, 칩 저항·LED.
   [추측 — 사진 배치. 기판 크기는 판매처 표기, 구멍 자리·부품 자리는 실물 재서 고칠 것, 미검증]
부품 모양: KiCad 공식 3D 라이브러리 STEP (D5g_real_parts.SRC 에 더해 같은 캐시로 받음).
"""
import importlib.util
import math
import os
import sys
import tempfile
import urllib.parse
import urllib.request

import FreeCAD as App
import Part

V = App.Vector
RAW = "https://raw.githubusercontent.com/britams/-capstone-project-repo/main/"
K = "https://raw.githubusercontent.com/KiCad/kicad-packages3D/master/"
SRC = {
    "pin1": K + "Connector_PinHeader_2.54mm.3dshapes/PinHeader_1x01_P2.54mm_Vertical.step",
    "r_v": K + "Resistor_THT.3dshapes/R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical.step",
    "cp10": K + "Capacitor_THT.3dshapes/CP_Radial_D10.0mm_P5.00mm.step",
    "cdisc": K + "Capacitor_THT.3dshapes/C_Disc_D3.0mm_W2.0mm_P2.50mm.step",
    "do201": K + "Diode_THT.3dshapes/D_DO-201AD_P15.24mm_Horizontal.step",
    "tb2": K + "TerminalBlock_Phoenix.3dshapes/TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal.step",
    "to220h": K + "Package_TO_SOT_THT.3dshapes/TO-220-3_Horizontal_TabDown.step",
    "soic16": K + "Package_SO.3dshapes/SOIC-16_3.9x9.9mm_P1.27mm.step",
    "xh3": K + "Connector_JST.3dshapes/JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical.step",
    "r0805": K + "Resistor_SMD.3dshapes/R_0805_2012Metric.step",
    "led0805": K + "LED_SMD.3dshapes/LED_0805_2012Metric.step",
}
P = 2.54
ZB = 205.0                                   # 데크 윗면 (D5g_real_parts.apply_circuit_extras 와 같음)


def hub_layout():
    """서현 hub_boards.py 를 레포에서 받아 (같은 폴더 구조로) 불러 판 2장을 돌려줌"""
    base = os.path.join(tempfile.gettempdir(), "sj_hub_src")
    for rel in ("전기회로/hub_boards.py", "design/circuit/circuit.py"):
        fn = os.path.join(base, *rel.split("/"))
        os.makedirs(os.path.dirname(fn), exist_ok=True)
        url = RAW + urllib.parse.quote(rel)
        open(fn, "wb").write(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "FreeCAD-capstone"}), timeout=60).read())
    sys.modules.pop("circuit", None)
    spec = importlib.util.spec_from_file_location("sj_hub_boards", os.path.join(base, "전기회로", "hub_boards.py"))
    hb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hb)
    return {"SERVO_HUB": hb.servo_hub(), "GATE_HUB": hb.gate_hub()}


def _kicad(RP, key, x, y, z, ang=0.0):
    """KiCad 모델: 원점 = 1번 다리, z 0 = 기판 윗면. ang(도)만큼 z축으로 돌린 뒤 (x, y, z)로"""
    if key not in RP.SRC:
        RP.SRC[key] = SRC[key]
    s = RP.load(key)
    if ang:
        s.rotate(V(0, 0, 0), V(0, 0, 1), ang)
    s.translate(V(x, y, z))
    return s


def hub_detail(doc, RP):
    boards = hub_layout()
    rep = []
    for nm, b in boards.items():
        h = RP.HUBS[nm]
        x0, y0, zt = h["x0"], h["y0"], ZB + h["stand"] + RP.PERF["t"]
        zbot = zt - RP.PERF["t"]
        pcb = Part.makeBox(b.L, b.W, RP.PERF["t"], V(x0, y0, zbot))
        holes = []
        for c in range(b.nc):
            for r in range(b.nr):
                if b.ok_hole((c, r)):
                    hx, hy = b.xy((c, r))
                    holes.append(Part.makeCylinder(0.5, RP.PERF["t"] + 2, V(x0 + hx, y0 + hy, zbot - 1)))
        for mx, my in b.mounts:
            holes.append(Part.makeCylinder(RP.PERF["hole"] / 2, RP.PERF["t"] + 2, V(x0 + mx, y0 + my, zbot - 1)))
        pcb = pcb.cut(Part.makeCompound(holes))
        parts, wires = [], []
        W = lambda hh: (x0 + b.xy(hh)[0], y0 + b.xy(hh)[1])
        skip = [o.Shape.BoundBox for o in doc.Objects if o.Label.startswith("193j_")]   # JST J_I2C 가 이미 꽂힌 구멍
        for hh, (node, lab, kind) in b.pins.items():
            if not isinstance(hh[0], int):
                continue
            x, y = W(hh)
            if any(bb.isInside(V(x, y, zt + 1)) for bb in skip):
                continue
            if kind == "wire":                                             # 22 AWG 전선 납땜 (위로 8 mm)
                wires.append(Part.makeCylinder(0.8, 8.0, V(x, y, zt)))
            else:
                parts.append(_kicad(RP, "pin1", x, y, zt))
        for name, val, h1, h2 in b.res:
            (x1, y1), (x2, y2) = W(h1), W(h2)
            ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
            key = {"10k": "r_v", "220": "r_v", "0.1µ": "cdisc", "1000µ": "cp10", "SB540": "do201"}.get(val, "r_v")
            parts.append(_kicad(RP, key, x1, y1, zt, ang))
        for kind, h1, h2, net in b.links:
            (x1, y1), (x2, y2) = W(h1), W(h2)
            d = V(x2 - x1, y2 - y1, 0)
            L = d.Length
            if L < 1e-6:
                continue
            if kind == "bus":                                              # 납땜 면 맨 구리선 Ø0.6
                wires.append(Part.makeCylinder(0.3, L, V(x1, y1, zbot - 0.3), d))
            elif kind == "bridge":                                         # 납땜 면 땜납 다리
                wires.append(Part.makeCylinder(0.45, L, V(x1, y1, zbot - 0.45), d))
            else:                                                          # 부품 면 점퍼 (피복선 Ø1.2, 높이 3)
                for p0, p1 in (((x1, y1, zt), (x1, y1, zt + 3)), ((x1, y1, zt + 3), (x2, y2, zt + 3)), ((x2, y2, zt + 3), (x2, y2, zt))):
                    v = V(*p1) - V(*p0)
                    wires.append(Part.makeCylinder(0.6, v.Length, V(*p0), v))
        lab_b = [o for o in doc.Objects if o.Label.startswith({"SERVO_HUB": "193v_", "GATE_HUB": "193g_"}[nm])][0]
        lab_b.Shape = pcb.removeSplitter() if len(holes) < 400 else pcb
        pre = {"SERVO_HUB": "193v_servo_hub_parts", "GATE_HUB": "193g_gate_hub_parts"}[nm]
        npin = sum(1 for k, v in b.pins.items() if isinstance(k[0], int) and v[2] != "wire")
        for suffix, shp, txt in (("", parts, "부품 (헤더 핀 %d · 저항/콘덴서/다이오드 %d, KiCad STEP)" % (npin, len(b.res))),
                                 ("_wires", wires, "선 (납땜 면 버스·땜납 다리, 부품 면 점퍼, 전선 자리)")):
            o = doc.addObject("Part::Feature", "SJ53C_%s%s" % (nm.lower(), suffix))
            o.Label = "%s%s (%s — 서현 hub_boards.py 배치)" % (pre, suffix, txt)
            o.Shape = Part.makeCompound(shp)
        rep.append("%s: 구멍 %d, 헤더 %d, 부품 %d, 선 %d" % (nm, len(holes), npin, len(b.res), len(wires)))
    return rep


def mosfet_detail(doc, RP):
    """SZH-AT021 — 판매 사진 배치 [추측 — 미검증]"""
    m = RP.MOS
    x0, y0, L, W = m["x0"], m["y0"], m["L"], m["W"]
    zt = ZB + m["stand"] + 1.6
    pcb = Part.makeBox(L, W, 1.6, V(x0, y0, zt - 1.6))
    for sx in (m["off"], L - m["off"]):
        for sy in (m["off"], W - m["off"]):
            pcb = pcb.cut(Part.makeCylinder(m["hole"] / 2, 4, V(x0 + sx, y0 + sy, zt - 3)))
    parts = []
    # 1) 나사 단자 2극 × 5 = 10극 — 한쪽 가장자리를 따라 (아래에서 180° 돌린 뒤 +y 가장자리, 전선은 +y 바깥에서 꽂음)
    tb0 = x0 + (L - 5 * 2 * 5.08) / 2 + 2.54
    for i in range(5):
        parts.append(RP.place_xy(_load(RP, "tb2"), tb0 + i * 10.16 + 2.54, y0 + 5.5, zt, rot=90))
    # 2) IRF540N 4개 — 단자 안쪽 줄, 눕힘 (방열판 탭이 +y)
    for i in range(4):
        s = _load(RP, "to220h")
        s.rotate(V(0, 0, 0), V(0, 0, 1), 0)
        parts.append(RP.place_xy(s, x0 + 12.0 + i * 14.0, y0 + 24.0, zt))
    # 3) SOIC-16 (광절연 칩 자리) 가운데
    parts.append(RP.place_xy(_load(RP, "soic16"), x0 + L / 2, y0 + 42.0, zt, rot=90))
    # 4) 3핀 커넥터 4개 — 위(+y) 가장자리
    for i in range(4):
        parts.append(RP.place_xy(_load(RP, "xh3"), x0 + 11.0 + i * 15.0, y0 + W - 6.0, zt, rot=90))
    # 5) 칩 저항 8 · LED 4 (저항 줄은 TO-220 몸통·SOIC 사이 y0+36 — 34면 TO-220과 0.4 mm³ 겹침)
    for i in range(4):
        parts.append(RP.place_xy(_load(RP, "r0805"), x0 + 9.0 + i * 14.0, y0 + 36.0, zt))
        parts.append(RP.place_xy(_load(RP, "r0805"), x0 + 15.0 + i * 14.0, y0 + 36.0, zt))
        parts.append(RP.place_xy(_load(RP, "led0805"), x0 + 12.0 + i * 14.0, y0 + 52.0, zt))
    o = [x for x in doc.Objects if x.Label.startswith("196m_")][0]
    o.Shape = pcb
    o.Label = "196m_mosfet_module_SZH-AT021 (66.8 × 66.8 빨간 기판, 구멍 자리 미검증)"
    if App.GuiUp:
        o.ViewObject.ShapeColor = (0.80, 0.10, 0.10)
    q = doc.addObject("Part::Feature", "SJ53C_mosfet_parts")
    q.Label = "196m_mosfet_parts (단자 10극·IRF540N 4·SOIC-16·3핀 4·칩 저항/LED — 판매 사진 배치, KiCad STEP, 미검증)"
    comp = Part.makeCompound(parts)
    # (SJ-53) 판 전체를 180° 돌려 둠 — 나사 단자 입구가 덱 가장자리(+y, 빈 곳)를 보게.
    #   −y 쪽에는 빛 게이트 허브(193g)가 5 mm 옆에 있어서 전선을 꽂고 나사를 돌릴 자리가 없음.
    #   3핀 신호 커넥터는 아두이노·허브 쪽(−y)으로 와서 신호선도 짧아짐.
    comp.rotate(V(x0 + L / 2, y0 + W / 2, 0), V(0, 0, 1), 180)
    q.Shape = comp
    return ["MOSFET: 부품 %d (사진 배치)" % len(parts)]


TAP = {2.0: 1.6, 3.0: 2.5}                   # 탭 드릴 지름 (M2 1.6, M3 2.5)
CLR = {2.0: 2.4, 3.0: 3.4}                   # 지나가는 구멍 (보통 맞춤)


def board_screws(doc, RP):
    """(SJ-53) 기판 3장 고정 나사 — 전부 십자 냄비머리, 드라이버로 조립.
    기본: 암-암 기둥(198h M2 × 8, 198m M3 × 6) + 위 나사(기판 → 기둥) + 아래 나사(데크 밑 → 기둥).
    데크 밑에 2020 가로대(y +80)가 있어 아래 나사가 막히는 자리는:
      기둥 대신 나일론 스페이서(구멍만 있는 통) + 위에서 긴 나사 1개 → 기판·스페이서를 지나 데크(아크릴 5 mm) 탭 구멍에 물림.
      나사 끝이 데크 밑면보다 0.6 mm 위에서 멈춰 가로대에 닿지 않음."""
    import D5g_fix_sj53 as FX
    deck = [o for o in doc.Objects if o.Label.startswith("101_deck")][0]
    zdb = deck.Shape.BoundBox.ZMin                                      # 데크 밑면
    tdeck = ZB - zdb
    std = {2.0: (14.0,), 3.0: (12.0,)}                                    # 긴 나사 길이 (규격)
    obst = [o for o in doc.Objects if hasattr(o, "Shape") and o.TypeId != "App::DocumentObjectGroup"
            and getattr(o, "Visibility", True) and o is not deck and not o.Name.startswith("SJ53C_")
            and not o.Label.startswith(("198h_", "198m_", "REF"))]
    shp, sp, fill, cut = [], [], [], []
    cnt = {"top": 0, "bottom": 0, "long": 0}
    for pre, d in (("198h_hub_standoff_servo_hub", 2.0), ("198h_hub_standoff_gate_hub", 2.0), ("198m_mosfet_standoff", 3.0)):
        st = [o for o in doc.Objects if o.Label.startswith(pre)]
        if not st:
            continue
        keep, nsp = [], 0
        for sol in st[0].Shape.Solids:
            b = sol.BoundBox
            cx, cy, hs = b.Center.x, b.Center.y, b.ZLength
            ztop = b.ZMax + RP.PERF["t"]
            bot = FX.pan_screw(V(cx, cy, zdb), V(0, 0, -1), d, tdeck + 3.0)
            del FX.REG[-1]
            bb = bot.BoundBox
            blocked = False
            for o in obst:
                try:
                    ob = o.Shape.BoundBox
                except Exception:
                    continue
                if ob.isValid() and ob.intersect(bb) and bot.common(o.Shape).Volume > 0.01:
                    blocked = True
                    break
            if not blocked:
                keep.append(sol)
                shp.append(FX.pan_screw(V(cx, cy, ztop), V(0, 0, 1), d, 5.0))      # 기판 1.6 + 기둥 3.4
                shp.append(FX.pan_screw(V(cx, cy, zdb), V(0, 0, -1), d, tdeck + 3.0))
                cut.append(Part.makeCylinder(CLR[d] / 2, tdeck + 2, V(cx, cy, zdb - 1)))
                cnt["top"] += 1
                cnt["bottom"] += 1
            else:
                L = [l for l in std[d] if l <= RP.PERF["t"] + hs + tdeck - 0.5][-1]
                shp.append(FX.pan_screw(V(cx, cy, ztop), V(0, 0, 1), d, L))
                od = {2.0: 4.0, 3.0: 6.0}[d]
                sp.append(Part.makeCylinder(od / 2, hs, V(cx, cy, b.ZMin)).cut(Part.makeCylinder(CLR[d] / 2, hs + 2, V(cx, cy, b.ZMin - 1))))
                fill.append(Part.makeCylinder(CLR[d] / 2 + 0.3, tdeck, V(cx, cy, zdb)))     # 옛 구멍 메우고
                cut.append(Part.makeCylinder(TAP[d] / 2, tdeck + 2, V(cx, cy, zdb - 1)))    # 탭 드릴 구멍
                cnt["long"] += 1
                nsp += 1
        if nsp:
            st[0].Shape = Part.makeCompound(keep)
            st[0].Label = st[0].Label.split(" (")[0] + " (%s × %d 암-암 기둥 %d, 구매 — 나머지 %d 자리는 198n 스페이서)" % (
                "M2" if d == 2.0 else "M3", int(round(hs)), len(keep), nsp)
    shape = deck.Shape
    if fill:
        shape = shape.fuse(Part.makeCompound(fill))
    if cut:
        shape = shape.cut(Part.makeCompound(cut))
    deck.Shape = shape.removeSplitter() if fill else shape
    q = doc.addObject("Part::Feature", "SJ53C_board_screws")
    q.Label = "198s_board_screws (십자 냄비머리 — 위 %d · 아래 %d · 긴 나사 %d (M2 × 14 / M3 × 12, 데크 탭))" % (cnt["top"], cnt["bottom"], cnt["long"])
    q.Shape = Part.makeCompound(shp)
    rep = ["기판 나사: 위 %d · 아래 %d · 긴 나사 %d (가로대 위 자리)" % (cnt["top"], cnt["bottom"], cnt["long"])]
    if sp:
        r = doc.addObject("Part::Feature", "SJ53C_board_spacers")
        r.Label = "198n_board_spacers (나일론 스페이서 %d — 구멍만 있는 통, 가로대 위 자리. 데크에 M2·M3 탭)" % len(sp)
        r.Shape = Part.makeCompound(sp)
    return rep

def _load(RP, key):
    if key not in RP.SRC:
        RP.SRC[key] = SRC[key]
    return RP.load(key)


def apply(doc):
    import D5g_real_parts as RP
    rep = []
    for fn in (hub_detail, mosfet_detail, board_screws):
        try:
            rep += fn(doc, RP)
        except Exception as e:                                             # 인터넷이 없으면 단순 모양 그대로
            rep.append("%s 못 함: %s" % (fn.__name__, e))
    a = [g for g in doc.Objects if g.Name == "GSJ_A"]
    for o in doc.Objects:                                                  # 새 객체는 A 구매품 묶음으로
        if o.Name.startswith("SJ53C_") and a and o not in a[0].Group:
            a[0].addObject(o)
            if App.GuiUp and o.Name.endswith("_wires"):
                o.ViewObject.ShapeColor = (0.85, 0.55, 0.25)
            if App.GuiUp and o.Name.endswith("_spacers"):
                o.ViewObject.ShapeColor = (0.95, 0.95, 0.90)
            if App.GuiUp and o.Name.endswith("_screws"):
                o.ViewObject.ShapeColor = (0.25, 0.25, 0.28)
    doc.recompute()
    return rep
