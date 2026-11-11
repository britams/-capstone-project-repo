# -*- coding: utf-8 -*-
"""급이부 — 바깥 병 + 연동 펌프 + 관 + 걸이 (서현, 2026-11-10 밤, CAP-AI-59)

서현 지시 (11/10 19:55~20:11): "설탕물 넣는 세팅이 불편하다, 사용자 편의성 좋게. 동력 써도 되니까."
물빠짐: 물길 바닥 끝(y 90) 바브 → 관 144hd → 프레임 밖으로 열린 끝 — 솜이 못 머금은 물은 고이지 않고 빠짐 (넘침 0)
방식: 프레임 바깥(+y 쪽, 데크 높이 둘레 레일)에 걸이 144b → 병 144n(250 mL)을 세워 둠 → 연동 펌프 144p가 '먹일 때만' 몇 방울
      → 관 144h → 물길 +x 벽 노즐 → 솜 위. 고인 물이 없어 열팽창 넘침·밀봉·뒤집기·물 높이 맞추기가 다 없어짐.
      채우기: 병 뚜껑을 열고 붓기 (병은 바깥, 손 닿는 높이). 펌프는 멈추면 관을 눌러 막아 저절로 안 흐름.
구매품 치수
  펌프 Adafruit 3910 (5~6 V, 0.5 A, 최대 100 mL/min, 관 안 3.5 · 바깥 5, 모터 Ø27.8, 전체 길이 66.8, 104 g) [확실 — Adafruit 상품 페이지]
       머리(롤러 집) 모양·관 자리는 [추측 — 사진 기준 단순 모양: 머리 Ø32 × 22, 관 2개 위로]
  병 Nalgene 2104-0008 HDPE 250 mL 넓은 입 (Ø61 × 높이 131, 뚜껑 43 mm) [가능성 높음 — 판매처 표]. 뚜껑 모양 Ø48 × 15 [추측]
       뚜껑에 Ø5 구멍(관) + Ø2 구멍(공기) 두 개를 뚫음
  관 실리콘 안 3.5 · 바깥 5 (펌프에 딸려 옴, 식품용으로 바꾸면 같은 치수) [확실 — Adafruit 페이지 치수]
  볼트 M5 × 8 + 드롭인 T너트 M5 (2020) 2개씩 — 프레임을 다 조립한 뒤에도 홈에 넣을 수 있는 것 [가능성 높음 — 판매품]
실행: D5g_frame_detail.make() 에서 feeder_mcm 다음에 apply(doc)
"""
import math

import FreeCAD as App
import Part

V = App.Vector

PUMP = dict(motor_d=27.8, L=66.8, head_d=32.0, head_h=22.0, port_dx=6.0, port_L=8.0, A=0.5, flow_ml_min=100.0)
BOT = dict(d=61.0, h=131.0, wall=1.2, cap_d=48.0, cap_h=15.0)
TUBE = dict(id=3.5, od=5.0)
# (11/10 밤) 볼트 x 40 → 27: 머리가 병에 닿음 (6 mm³, 모델 검사)
HB = dict(x0=20.0, x1=140.0, y_face=180.0, t=4.0, z0=92.0, z1=200.0, bolt_x=(27.0, 125.0), bolt_z=190.0,
          bot_x=55.0, gap=2.0, ring_z=(168.0, 178.0), pump_x=112.0)
COL = dict(PRINT=None, BOT=(0.92, 0.95, 1.0), PUMP=(0.25, 0.25, 0.28), TUBE=(0.95, 0.95, 0.95), STEEL=(0.15, 0.15, 0.15))


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def bottle_center():
    h = HB
    return V(h["bot_x"], h["y_face"] + h["t"] + h["gap"] + BOT["d"] / 2, h["z0"] + 3.0)     # 병 바닥 가운데 (11/11: 클램프 2개가 잡음, 바닥은 떠 있음)


def pump_center():
    h = HB
    return V(h["pump_x"], h["y_face"] + h["t"] + h["gap"] + PUMP["head_d"] / 2, h["z0"] + 3.0)  # 모터 아래 끝 가운데


def bottle():
    """144n: 병 + 뚜껑 (뚜껑 관 구멍 Ø5, 공기 구멍 Ø2)"""
    b = bottle_center()
    out = Part.makeCylinder(BOT["d"] / 2, BOT["h"] - BOT["cap_h"], b)
    out = out.cut(Part.makeCylinder(BOT["d"] / 2 - BOT["wall"], BOT["h"] - BOT["cap_h"], b + V(0, 0, BOT["wall"])))
    cap = Part.makeCylinder(BOT["cap_d"] / 2, BOT["cap_h"], b + V(0, 0, BOT["h"] - BOT["cap_h"]))
    cap = cap.cut(Part.makeCylinder(TUBE["od"] / 2, 30, b + V(0, 0, BOT["h"] - 20)))
    cap = cap.cut(Part.makeCylinder(1.0, 30, b + V(12, 0, BOT["h"] - 20)))
    return out, cap


def pump():
    """144p: 모터(아래) + 머리(위) + 관 자리 2개(위로). 축은 세로"""
    p = pump_center()
    motor_h = PUMP["L"] - PUMP["head_h"]
    m = Part.makeCylinder(PUMP["motor_d"] / 2, motor_h, p)
    hd = Part.makeCylinder(PUMP["head_d"] / 2, PUMP["head_h"], p + V(0, 0, motor_h))
    ports = []
    for sx in (-1, 1):
        q = p + V(sx * PUMP["port_dx"], 0, PUMP["L"])
        ports.append(Part.makeCylinder(TUBE["od"] / 2, PUMP["port_L"], q).cut(Part.makeCylinder(TUBE["id"] / 2, PUMP["port_L"] + 1, q - V(0, 0, 0.5))))
    return m.fuse(hd), Part.makeCompound(ports)


def port(side):
    """펌프 관 끝 (side −1 = 들어옴, +1 = 나감) 위 끝 점"""
    return pump_center() + V(side * PUMP["port_dx"], 0, PUMP["L"] + PUMP["port_L"])


def holder():
    """144b (11/11, CAP-AI-61 — 프린트 대신): 알루미늄 판 3 mm (120 × 108 자름·구멍) — 레일 바깥 면 y 180에 M5 2
    병은 파이프 클램프 Ø60 2개(구매, 판에 M4), 펌프는 케이블 타이 2개(구매)로 판에 묶음"""
    h = HB
    yf, t = h["y_face"], h["t"]
    pl = box(h["x0"], h["x1"], yf, yf + t, h["z0"], h["z1"])
    for bx in h["bolt_x"]:
        pl = pl.cut(Part.makeCylinder(2.75, 20, V(bx, yf - 5, h["bolt_z"]), V(0, 1, 0)))
    return pl.removeSplitter()


def clamps():
    """사는 것: 파이프 클램프 2 (병 둘레, 폭 15 · 두께 1.5, 판에 붙는 귀) + 케이블 타이 2 (펌프 둘레, 폭 4 · 두께 1.2)"""
    h = HB
    yf, t = h["y_face"], h["t"]
    b = bottle_center()
    ro = BOT["d"] / 2
    out = []
    for zc in (h["z0"] + 20.0, h["ring_z"][0]):
        ring = Part.makeCylinder(ro + 1.5, 15.0, V(b.x, b.y, zc)).cut(Part.makeCylinder(ro, 20, V(b.x, b.y, zc - 1)))
        ear = box(b.x - 8, b.x + 8, yf + t, b.y - ro, zc, zc + 15.0)
        out.append(ring.fuse(ear).cut(Part.makeCylinder(ro, 20, V(b.x, b.y, zc - 1))))
    pc = pump_center()
    pr = PUMP["motor_d"] / 2
    ties = []
    for zz in (pc.z + 8, pc.z + 30):
        band = Part.makeCylinder(pr + 1.2, 4.0, V(pc.x, pc.y, zz)).cut(Part.makeCylinder(pr, 6, V(pc.x, pc.y, zz - 1)))
        band = band.fuse(box(pc.x - 3, pc.x + 3, yf + t, pc.y - pr, zz, zz + 4))
        ties.append(band.cut(Part.makeCylinder(pr, 6, V(pc.x, pc.y, zz - 1))))
    return Part.makeCompound(out), Part.makeCompound(ties)


def bolts(G):
    """M5 × 8 + 드롭인 T너트 2개씩 — 볼트 머리는 판 바깥(y 184 → 189), 몸통 −y로 홈 안"""
    h = HB
    bb, tt = [], []
    for bx in h["bolt_x"]:
        p = V(bx, h["y_face"] + h["t"], h["bolt_z"])
        bb.append(Part.makeCylinder(2.5, 8, p, V(0, -1, 0)).fuse(Part.makeCylinder(4.25, 5, p, V(0, 1, 0))))
        t = G.tnut_local("rail")
        t.translate(V(-G.BR["hole_at"], 0, 0))
        t.rotate(V(0, 0, 0), V(1, 0, 0), -90)                     # 판 면(+z) → 레일 바깥 면(+y)
        t.translate(V(bx, h["y_face"], h["bolt_z"]))
        tt.append(t)
    return Part.makeCompound(bb), Part.makeCompound(tt)


def tube_along(pts):
    """점들을 잇는 관 (굽힘은 둥글게) — 바깥 Ø5 · 안 Ø3.5"""
    w = Part.makePolygon([V(*p) if not isinstance(p, App.Vector) else p for p in pts])
    d0 = (w.Edges[0].Vertexes[1].Point - w.Edges[0].Vertexes[0].Point).normalize()
    p0 = w.Edges[0].Vertexes[0].Point
    so = Part.Wire(Part.makeCircle(TUBE["od"] / 2, p0, d0))
    si = Part.Wire(Part.makeCircle(TUBE["id"] / 2, p0, d0))
    o = w.makePipeShell([so], True, False, 2)
    i = w.makePipeShell([si], True, False, 2)
    return o.cut(i)


def tube_paths(z_cross):
    """빨대(병 안 → 뚜껑 → 펌프 들어옴), 먹이 관(펌프 나감 → 위로 → 안으로 → 노즐). z_cross = 안으로 들어가는 높이"""
    import D5g_feeder_uln as FU
    f = FU.FD
    b = bottle_center()
    top = b.z + BOT["h"]
    pin, pout = port(-1), port(1)
    suck = [b + V(0, 0, 6), V(b.x, b.y, top + 12), V(pin.x, pin.y, top + 12), pin + V(0, 0, -3)]
    b = FU.BUY                                                       # (11/11) 산 니플: 받침 5 + 육각 3 + 바브 8 → 관을 바브에 6 mm 끼움
    xn = f["x"] + f["ch_w"] / 2 + f["ch_t"] + b["pad_t"] + b["fit_hex_t"] + b["fit_barb_L"] - 6.0
    xr = pout.x
    feed = [pout + V(0, 0, -3), V(xr, pout.y, z_cross), V(xr, f["nz_y"], z_cross), V(xr, f["nz_y"], f["nz_z"]), V(xn, f["nz_y"], f["nz_z"])]
    return suck, feed


def drain_path(zr, xo):
    """물빠짐 관: 바닥 바브 아래 끝 → zr 높이 → x xo로 → 바깥(y 250) → 아래 30 (끝은 열려 있음, 땅으로 떨어짐)"""
    import D5g_feeder_uln as FU
    f = FU.FD
    b = FU.BUY
    z0 = f["floor_z"] - b["pad_t"] - b["fit_hex_t"] - b["fit_barb_L"] + 6.0
    return [V(f["x"], f["dr_y"], z0), V(f["x"], f["dr_y"], zr), V(xo, f["dr_y"], zr), V(xo, 250.0, zr), V(xo, 250.0, zr - 30)]


def _hits(shape, others, tol=0.5):
    out = []
    for o in others:
        if shape.BoundBox.intersect(o.Shape.BoundBox):
            v = shape.common(o.Shape).Volume
            if v > tol:
                out.append((o.Label.split(" ")[0], round(v, 1)))
    return out


def _add(doc, label, shp, col):
    for o in [o for o in doc.Objects if o.Label.startswith(label.split(" ")[0] + " ")]:
        doc.removeObject(o.Name)
    o = doc.addObject("Part::Feature", "F" + label.split(" ")[0])
    o.Label, o.Shape = label, shp
    if col and getattr(o, "ViewObject", None):
        o.ViewObject.ShapeColor = col
    return o


def apply(doc):
    import D5g_frame_detail as G
    rep = {}
    for o in [o for o in doc.Objects if o.Label.startswith(("144n", "144p", "144b_", "144c_", "144z_", "144h", "144s_", "144t_"))]:
        doc.removeObject(o.Name)
    others = [o for o in doc.Objects if o.TypeId == "Part::Feature" and not o.Shape.isNull() and o.Shape.Volume > 0
              and not o.Label.startswith(("REF_camera", "FitBox"))]
    hb = holder()
    cl, ti = clamps()
    bt, cap = bottle()
    pm, ports = pump()
    bo, tn = bolts(G)
    # 먹이 관이 안으로 들어가는 높이: 걸리는 것 없는 첫 높이
    tried = []
    for zc in (300.0, 320.0, 280.0, 340.0, 260.0, 360.0):
        suck, feed = tube_paths(zc)
        tf = tube_along(feed)
        h = [x for x in _hits(tf, others) if not x[0].startswith(("143_",))]
        tried.append((zc, h))
        if not h:
            break
    ts = tube_along(suck)
    dtried = []
    for zr in (330.0, 310.0, 290.0, 345.0):
        for xo in (85.0, 25.0, 100.0):
            dp = drain_path(zr, xo)
            td = tube_along(dp)
            h = [x for x in _hits(td, others + []) if not x[0].startswith(("143_",))]
            h += [("144b/병", 1)] if td.common(hb).Volume > 0.5 or td.common(bt).Volume > 0.5 else []
            dtried.append((zr, xo, h))
            if not h:
                break
        if not h:
            break
    rep["drain_tube"] = dtried[-1][:2]
    rep["drain_tube_tries"] = dtried
    rep["drain_tube_len_mm"] = round(sum(e.Length for e in Part.makePolygon(dp).Edges))
    rep["feed_tube_z"] = tried[-1][0]
    rep["feed_tube_tries"] = tried
    rep["feed_tube_len_mm"] = round(sum(e.Length for e in Part.makePolygon(feed).Edges))
    rep["suck_tube_len_mm"] = round(sum(e.Length for e in Part.makePolygon(suck).Edges))
    new = [("144b_feeder_holder (병·펌프 걸이 — 알루미늄 판 3 mm 120 × 108 자름·구멍, CAP-AI-61)", hb, (0.80, 0.82, 0.85)),
           ("144c_pipe_clamp_D60 (파이프 클램프 Ø60 2개 — 병, 판에 M4, 구매)", cl, (0.70, 0.70, 0.72)),
           ("144z_cable_ties (케이블 타이 2 — 펌프, 구매)", ti, (0.15, 0.15, 0.15)),
           ("144n_bottle_250mL (Nalgene 2104-0008 HDPE, 구매)", bt, COL["BOT"]),
           ("144nc_bottle_cap (병 뚜껑 — 관 Ø5·공기 Ø2 구멍 뚫음)", cap, COL["BOT"]),
           ("144p_pump (연동 펌프 Adafruit 3910, 5~6 V 0.5 A, 구매)", pm, COL["PUMP"]),
           ("144pp_pump_ports (펌프 관 자리)", ports, COL["PUMP"]),
           ("144h_tube_suck (실리콘 관 3.5 × 5, 병 → 펌프, 구매)", ts, COL["TUBE"]),
           ("144hf_tube_feed (실리콘 관 3.5 × 5, 펌프 → 노즐, 구매)", tf, COL["TUBE"]),
           ("144hd_tube_drain (실리콘 관 3.5 × 5, 물길 바닥 → 바깥, 구매)", td, COL["TUBE"]),
           ("144s_bolt_M5x8 (걸이 → 레일, 2개, 구매)", bo, COL["STEEL"]),
           ("144t_tnut_M5_dropin (2020 드롭인 T너트 2개, 구매)", tn, (0.85, 0.75, 0.20))]
    objs = [_add(doc, *n) for n in new]
    doc.recompute()
    rep.update(check(doc, objs, others))
    return rep


def check(doc, objs, others):
    """겹침 (관 ↔ 노즐·펌프 자리, 볼트 ↔ T너트·레일 홈은 따로), 병 들어 올리는 길, 뚜껑 돌릴 손 자리"""
    r = {}
    mine = {o.Label.split(" ")[0]: o for o in objs}
    allow = {("144hf_tube_feed", "143_feed_trough"), ("144h_tube_suck", "144pp_pump_ports"), ("144hf_tube_feed", "144pp_pump_ports"),
             ("144h_tube_suck", "144nc_bottle_cap"), ("144h_tube_suck", "144n_bottle_250mL"), ("144s_bolt_M5x8", "144t_tnut_M5_dropin"),
             ("144pp_pump_ports", "144p_pump"), ("144hd_tube_drain", "143_feed_trough"),
             ("144hf_tube_feed", "143n_nipple_M5_barb"), ("144hd_tube_drain", "143n_nipple_M5_barb")}
    ov = []
    names = list(mine)
    for i, a in enumerate(names):
        for b in names[i + 1:] + [o.Label.split(" ")[0] for o in others]:
            sb = mine[b].Shape if b in mine else [o for o in others if o.Label.split(" ")[0] == b][0].Shape
            sa = mine[a].Shape
            if not sa.BoundBox.intersect(sb.BoundBox):
                continue
            v = sa.common(sb).Volume
            if v > 0.05:
                ok = (a, b) in allow or (b, a) in allow or (a == "144s_bolt_M5x8" and b.startswith("100b_rail")) or (a == "144t_tnut_M5_dropin" and b.startswith("100b_rail"))
                ov.append((a, b, round(v, 2), "허용" if ok else "문제"))
    r["overlaps"] = ov
    r["bad"] = [x for x in ov if x[3] == "문제"]
    # 병 들어 올리는 길: 병을 고리 위로 160 mm 들어 올림 (뚜껑 포함)
    b = bottle_center()
    lift = Part.makeCylinder(BOT["d"] / 2, BOT["h"] + 160, b + V(0, 0, 20))
    fixed = [o for o in others] + [mine["144p_pump"], mine["144pp_pump_ports"]]
    r["bottle_lift_blockers"] = [x for x in _hits(lift, fixed, 1.0)]
    # 뚜껑 돌릴 손: 뚜껑 둘레 반지름 45, 높이 뚜껑 ~ +40 (관은 빼고)
    zc = b.z + BOT["h"] - BOT["cap_h"]
    hand = Part.makeCylinder(45, BOT["cap_h"] + 40, V(b.x, b.y, zc)).cut(Part.makeCylinder(BOT["cap_d"] / 2 + 0.5, 100, V(b.x, b.y, zc - 1)))
    r["cap_hand_blockers"] = [x for x in _hits(hand, others, 1.0)]
    # 걸이 판이 레일 바깥 면에 닿나 (0.3 mm 안)
    hb = mine["144b_feeder_holder"].Shape
    rail = [o for o in others if o.Label.startswith("100b_rail_deck_x+170")]
    r["holder_on_rail_mm"] = round(hb.distToShape(rail[0].Shape)[0], 2) if rail else None
    return r
