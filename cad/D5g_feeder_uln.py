# -*- coding: utf-8 -*-
"""D5g 추가 — 설탕물 급이 방(개념설계) + ULN2003 실제 보드·받침 + 공중 부양 검사 (승준, 2026-11-06, CAP-AI-SJ-40)

D5g_frame_detail.make() 가 부른다. 좌표는 D5e 좌표계 (원점 격자 가운데, +x 방생 문 쪽, +y 먹이통 쪽).

1) 설탕물 급이 방 — '병아리 물그릇' 원리 (뒤집은 병의 입구 높이가 물 높이를 정함, 펌프·전기 없음)
   흐름: 마킹 → 바닥을 급이 높이로 내림 → 말벌이 벽 구멍으로 2 mm 나온 코튼롤 끝을 빨아 먹음 → 방생 문 열림
   구매품: 팰컨 50 mL 원뿔 튜브(코닝 352070: 바깥 Ø29.72, 길이 114.55, 원뿔 16) [확실 — 제조사 도면]
           치과용 코튼롤 2호 Ø10 × 38 [가능성 높음 — 판매처 여러 곳 같은 값]
   설계품(3D 프린트, PETG — 설탕물·세척): 143 급이 물길(벽 → 그릇) + 튜브 그릇 + 기둥 → 발은 데크 위, M5 × 12로 데크를 지나 아래 2020 가로대(y +80) T너트에
   물 높이: 튜브 입구 z 374 → 물길 바닥 369, 코튼롤 아래 끝 373 → 롤이 1 mm 이상 잠김 (입구 높이를 받침 리브로 정함)
   바뀐 곳: 144 먹이통·142 심지(자리 상자) 지움, 120 마킹실 벽 +y 쪽에 Ø10.6 구멍 (x 55, z 378)
   튜브 자리 y 95: 마커 X 빔(212, y −74~66)이 x로 지나가는 자리 밖이라 위로 길어도 안 부딪침
2) ULN2003 드라이버 보드 — 판매품 35 × 31.9 × 11, M2.5 구멍 30 × 26.5 [가능성 높음 — 판매처 2곳 같은 값]
   X·Y 보드: 갠트리 둘레 레일(x 160~180, z 452~472) 윗면에 197 받침(3D 프린트) + M5 × 8 + T너트로 고정 (D5f 상자는 기둥 없는 곳에 떠 있었음)
   F 보드: 데크 위 같은 자리, 높이 5 받침 기둥 4개
3) floating(doc): 다른 부품과 0.3 mm 안에 닿지 않는 부품 목록 (빔·참고 제외)
"""
import FreeCAD as App
import Part

V = App.Vector

FD = dict(x=55.0, zc=378.0, roll_r=5.0, roll_y0=16.0, roll_L=38.0, wall_hole_r=5.3,
          ch_w=12.0, ch_t=2.0, ch_y0=23.0, ch_y1=95.0, floor_z=366.0, floor_t=3.0, wall_top=388.0,
          tube_y=95.0, tube_r=14.86, tube_L=114.55, cone_L=16.0, tip_r=3.1, mouth_z=374.0,
          bowl_ri=17.5, bowl_t=2.5, bowl_top=400.0, post_y=80.0, post_w=12.0, post_foot_z=205.0)   # 발: 데크(101) 윗면 z 205, 아래 2020 가로대 y +80
FOOT_DX = 12.0     # 발 볼트 x 간격 (머리 Ø8.5가 기둥 12 × 12에 안 닿게: 12 − 4.25 > 6)
ULN = dict(L=35.0, W=31.9, t=1.6, hx=30.0, hy=26.5, hole=2.7, stand=5.0)
ULN_SPOTS = {"X": (170.0, -30.0, 472.0, "rail"), "Y": (170.0, 22.0, 472.0, "rail"), "F": (55.0, -50.0, 205.0, "deck")}


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


# ---------------- 급이 방 ----------------
def cotton_roll():
    f = FD
    return Part.makeCylinder(f["roll_r"], f["roll_L"], V(f["x"], f["roll_y0"], f["zc"]), V(0, 1, 0))


def falcon_tube_inverted():
    """입구가 아래 (z mouth_z), 원뿔 끝이 위"""
    f = FD
    body_L = f["tube_L"] - f["cone_L"]
    c = Part.makeCylinder(f["tube_r"], body_L, V(f["x"], f["tube_y"], f["mouth_z"]))
    cone = Part.makeCone(f["tube_r"], f["tip_r"], f["cone_L"], V(f["x"], f["tube_y"], f["mouth_z"] + body_L))
    outer = c.fuse(cone)
    inner = Part.makeCylinder(f["tube_r"] - 0.97, body_L, V(f["x"], f["tube_y"], f["mouth_z"] - 0.01))
    return outer.cut(inner).removeSplitter()


def feed_trough():
    """143: 물길(벽 바깥 y 23 → 그릇) + 튜브 그릇(받침 리브 3개) + 기둥 → 2020 가로대(y +80) 윗면"""
    f = FD
    x0, x1 = f["x"] - f["ch_w"] / 2 - f["ch_t"], f["x"] + f["ch_w"] / 2 + f["ch_t"]
    ch = box(x0, x1, f["ch_y0"], f["ch_y1"], f["floor_z"], f["wall_top"])
    ch = ch.cut(box(f["x"] - f["ch_w"] / 2, f["x"] + f["ch_w"] / 2, f["ch_y0"] - 1, f["ch_y1"], f["floor_z"] + f["floor_t"], f["wall_top"] + 1))
    ro = f["bowl_ri"] + f["bowl_t"]
    bowl = Part.makeCylinder(ro, f["bowl_top"] - f["floor_z"], V(f["x"], f["tube_y"], f["floor_z"]))
    bowl = bowl.cut(Part.makeCylinder(f["bowl_ri"], f["bowl_top"], V(f["x"], f["tube_y"], f["floor_z"] + f["floor_t"])))
    shp = ch.fuse(bowl)
    shp = shp.cut(Part.makeCylinder(f["bowl_ri"], f["bowl_top"], V(f["x"], f["tube_y"], f["floor_z"] + f["floor_t"])))   # 그릇 안에는 물길 벽 없음
    import math
    for k in range(3):        # 받침 리브: 튜브 입구를 z mouth_z 에 올림
        a = math.radians(90 + 120 * k)
        cx, cy = f["x"] + (f["bowl_ri"] - 2.5) * math.cos(a), f["tube_y"] + (f["bowl_ri"] - 2.5) * math.sin(a)
        shp = shp.fuse(box(cx - 1.5, cx + 1.5, cy - 1.5, cy + 1.5, f["floor_z"] + f["floor_t"] - 0.01, f["mouth_z"]))
    pw = f["post_w"] / 2
    post = box(f["x"] - pw, f["x"] + pw, f["post_y"] - pw, f["post_y"] + pw, f["post_foot_z"] + 3, f["floor_z"] + 0.01)
    foot = box(f["x"] - FOOT_DX - 6, f["x"] + FOOT_DX + 6, f["post_y"] - 10, f["post_y"] + 10, f["post_foot_z"], f["post_foot_z"] + 3)
    for sx in (-FOOT_DX, FOOT_DX):
        foot = foot.cut(Part.makeCylinder(2.75, 10, V(f["x"] + sx, f["post_y"], f["post_foot_z"] - 2)))
    return shp.fuse(post).fuse(foot).removeSplitter()


def wall_hole():
    f = FD
    return Part.makeCylinder(f["wall_hole_r"], 12, V(f["x"], 15.0, f["zc"]), V(0, 1, 0))


# ---------------- ULN2003 보드 (판매품 외형) ----------------
def uln_board(cx, cy, z0):
    """보드 아래 면이 z0+stand. 35는 x, 31.9는 y. 부품: DIP16, XH 5핀(흰), 핀 헤더 6, LED 4"""
    u = ULN
    zb = z0 + u["stand"]
    pcb = box(cx - u["L"] / 2, cx + u["L"] / 2, cy - u["W"] / 2, cy + u["W"] / 2, zb, zb + u["t"])
    for sx in (-1, 1):
        for sy in (-1, 1):
            pcb = pcb.cut(Part.makeCylinder(u["hole"] / 2, 5, V(cx + sx * u["hx"] / 2, cy + sy * u["hy"] / 2, zb - 1)))
    zt = zb + u["t"]
    chip = box(cx - 9.65, cx + 9.65, cy - 3.2 + 4, cy + 3.2 + 4, zt, zt + 3.3)                  # ULN2003A DIP-16
    xh = box(cx - 6.2, cx + 6.2, cy - 15.9, cy - 10.1, zt, zt + 7.0)                            # 모터 소켓 XH 5핀
    hdr = box(cx + 11.0, cx + 13.5, cy - 7.6, cy + 7.6, zt, zt + 8.5)                           # 입력 핀 6
    leds = [Part.makeCylinder(1.5, 5.0, V(cx - 12 + 4 * i, cy + 13.0, zt)) for i in range(4)]
    stands = [Part.makeCylinder(2.5, u["stand"], V(cx + sx * u["hx"] / 2, cy + sy * u["hy"] / 2, z0)) for sx in (-1, 1) for sy in (-1, 1)]
    board = pcb.fuse([chip, xh, hdr] + leds)
    return board, Part.makeCompound(stands)


def uln_rail_bracket(cx, cy, z0):
    """197: 레일 윗면(z0)에 놓는 판 38 × 52 × 3 — 가운데 키(홈에), M5 구멍 2 (y ±22), 보드 기둥 4 자리는 판 위"""
    p = box(cx - 19, cx + 19, cy - 26, cy + 26, z0, z0 + 3)
    p = p.fuse(box(cx - 2.8, cx + 2.8, cy - 26, cy + 26, z0 - 0.5, z0))
    for sy in (-22, 22):
        p = p.cut(Part.makeCylinder(2.75, 10, V(cx, cy + sy, z0 - 2)))
    return p.removeSplitter()


def make_into(doc, G):
    """doc(D5g)에 급이 방과 ULN2003 실제 보드를 넣는다. G = D5g_frame_detail 모듈 (볼트·T너트 모양)"""
    rm = [o for o in doc.Objects if o.Label.startswith(("144_food_tank", "142_feeder_wick", "195_uln2003"))]
    for o in rm:
        doc.removeObject(o.Name)
    for o in doc.Objects:
        if o.Label.startswith("120_chamber_walls"):
            o.Shape = o.Shape.cut(wall_hole()).removeSplitter()
            o.Label = "120_chamber_walls (+y 벽 Ø10.6 급이 구멍)"
    add = []
    add.append(("142n_cotton_roll_#2 (Ø10×38, 구매)", cotton_roll(), (0.97, 0.97, 0.92)))
    add.append(("144n_falcon_50mL_inverted (설탕물 50 mL, 구매)", falcon_tube_inverted(), (0.85, 0.92, 1.0)))
    add.append(("143_feed_trough (설탕물 방 물길·그릇·기둥, 3D 프린트 PETG)", feed_trough(), None))
    f = FD
    # 기둥 발 → 데크(5) 지나 아래 2020 가로대(y +80, 윗면 z = 데크 아래 면) T너트, M5 × 12
    import D5e_module_kinematic as K
    rail_top = K.FR["deck_z"] + 20.0
    fb, ft = [], []
    for sx in (-FOOT_DX, FOOT_DX):
        p = (f["x"] + sx, f["post_y"], f["post_foot_z"] + 3)
        fb.append(Part.makeCylinder(2.5, 12, V(*p), V(0, 0, -1)).fuse(Part.makeCylinder(4.25, 5, V(*p))))
        t = G.tnut_local("rail")
        t.translate(V(f["x"] + sx - G.BR["hole_at"], f["post_y"], rail_top))   # 가로대는 x 방향 → 너트 길이도 x
        ft.append(t)
    for o in doc.Objects:
        if o.Label.startswith("101_deck"):
            sh = o.Shape
            for sx in (-FOOT_DX, FOOT_DX):
                sh = sh.cut(Part.makeCylinder(2.75, 20, V(f["x"] + sx, f["post_y"], f["post_foot_z"] - 10)))
            for sx in (-1, 1):
                for sy in (-1, 1):
                    cx, cy, _z, _k = ULN_SPOTS["F"]
                    sh = sh.cut(Part.makeCylinder(1.35, 20, V(cx + sx * ULN["hx"] / 2, cy + sy * ULN["hy"] / 2, f["post_foot_z"] - 10)))
            o.Shape = sh.removeSplitter()
            o.Label = "101_deck (급이 기둥 M5 구멍 2, F 보드 M2.5 구멍 4)"
    for k, (cx, cy, z0, kind) in ULN_SPOTS.items():
        if kind == "rail":
            br = uln_rail_bracket(cx, cy, z0)
            add.append(("197_uln_bracket_%s (3D 프린트)" % k, br, None))
            zb = z0 + 3
            for sy in (-22, 22):
                p = (cx, cy + sy, zb)
                fb.append(Part.makeCylinder(2.5, 8, V(*p), V(0, 0, -1)).fuse(Part.makeCylinder(4.25, 5, V(*p))))
                t = G.tnut_local("rail")
                t.translate(V(-G.BR["hole_at"], 0, 0))
                t.rotate(V(0, 0, 0), V(0, 0, 1), 90)        # 길이 방향을 레일(y) 방향으로
                t.translate(V(cx, cy + sy, z0))
                ft.append(t)
        else:
            zb = z0
        board, stands = uln_board(cx, cy, zb)
        add.append(("195p_uln2003_%s (판매품 35×31.9)" % k, board, (0.10, 0.50, 0.25)))
        add.append(("198_uln_standoff_%s (M2.5 × 5 기둥 4, 구매)" % k, stands, (0.80, 0.70, 0.30)))
    add.append(("100h_bolt_M5x8_mounts", Part.makeCompound(fb), (0.1, 0.1, 0.1)))
    add.append(("100i_tnut_M5_mounts", Part.makeCompound(ft), (0.85, 0.75, 0.20)))
    objs = []
    for nm, shp, col in add:
        o = doc.addObject("Part::Feature", "SJ%02d" % len(objs))
        o.Label = nm
        o.Shape = shp
        objs.append((o, col))
    doc.recompute()
    return objs


def floating(doc, tol=0.3):
    """보이는 부품 중 다른 어떤 부품과도 tol 안에 닿지 않는 것 (떠 있는 것)"""
    skip = ("REF_", "196_gate", "SJ_fit")
    obs = [o for o in doc.Objects if hasattr(o, "Shape") and o.TypeId != "App::DocumentObjectGroup" and not o.Shape.isNull()
           and (not App.GuiUp or o.ViewObject.Visibility) and not o.Label.startswith(skip)]
    out = []
    for o in obs:
        b = o.Shape.BoundBox
        bb = App.BoundBox(b.XMin - tol, b.YMin - tol, b.ZMin - tol, b.XMax + tol, b.YMax + tol, b.ZMax + tol)
        ok = False
        for p in obs + [x for x in doc.Objects if x.Label.startswith("REF_trap") and hasattr(x, "Shape")]:
            if p is o or not bb.intersect(p.Shape.BoundBox):
                continue
            if o.Shape.distToShape(p.Shape)[0] <= tol:
                ok = True
                break
        if not ok:
            out.append(o.Label)
    return out
