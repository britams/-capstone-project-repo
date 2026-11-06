# -*- coding: utf-8 -*-
"""D5g 추가 — 설탕물 급이 방(개념설계) + ULN2003 실제 보드·받침 + 공중 부양 검사 (승준, 2026-11-06, CAP-AI-SJ-40)

D5g_frame_detail.make() 가 부른다. 좌표는 D5e 좌표계 (원점 격자 가운데, +x 방생 문 쪽, +y 먹이통 쪽).

1) 설탕물 급이 방 — '병아리 물그릇' 원리 (뒤집은 병의 입구 높이가 물 높이를 정함, 펌프·전기 없음)
   흐름: 마킹 → 바닥을 급이 높이로 내림 → 말벌이 벽 구멍으로 2 mm 나온 코튼롤 끝을 빨아 먹음 → 방생 문 열림
   구매품: 팰컨 50 mL 원뿔 튜브(코닝 352070: 바깥 Ø29.72, 길이 114.55, 원뿔 16) [확실 — 제조사 도면]
           치과용 코튼롤 2호 Ø10 × 38 [가능성 높음 — 판매처 여러 곳 같은 값]
   설계품(3D 프린트, PETG — 설탕물·세척): 143 급이 물길(벽 → 그릇) + 튜브 그릇 + 기둥 → 발은 데크 위, M5 × 12로 데크를 지나 아래 2020 가로대(y +80) T너트에
   물 높이: 튜브 입구 z 369 (받침 리브 높이로 정함) — 벽 구멍 아래 끝 372.6보다 3.6 mm 낮음, 코튼롤 바깥 끝은 2 mm 잠김 (water_check())
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

# (11/06 밤 고침) 물 높이가 벽 구멍 아래 끝보다 높아 틈으로 새던 것 → 물 높이 369, 코튼롤을 바깥으로 10.6° 내려 바깥 끝만 잠김
#   벽 구멍 아래 끝 372.6 − 물 높이 369 = 3.6 mm 여유 ≥ 낮 열팽창 최대 2.6 mm (튜브 공기 50 mL, +25 K) [확실 — 계산, 문서 3장]
FD = dict(x=55.0, roll_r=5.0, tip_y=16.0, tip_z=379.0, end_y=54.0, end_z=372.0,      # 코튼롤: 안 끝(마킹실) → 바깥 끝(물길)
          wall_hole_r=5.6, wall_hole_z=378.2,
          ch_w=12.0, ch_t=2.0, ch_y0=23.0, ch_y1=95.0, floor_z=361.0, floor_t=3.0, wall_top=388.0,
          tube_y=95.0, tube_r=14.86, tube_L=114.55, cone_L=16.0, tip_r=3.1, mouth_z=369.0,
          bowl_ri=17.5, bowl_t=2.5, bowl_top=400.0, post_y=80.0, post_w=12.0, post_foot_z=205.0,
          post_dx=-3.0)   # (SJ-49) 기둥을 x −3: 막대 로드셀(x 60.15~72.85, y ~77.5) 자리 비움   # 발: 데크(101) 윗면 z 205, 아래 2020 가로대 y +80
FOOT_DX = 12.0     # 발 볼트 x 간격 (머리 Ø8.5가 기둥 12 × 12에 안 닿게: 12 − 4.25 > 6)
ULN = dict(L=35.0, W=31.9, t=1.6, hx=30.0, hy=26.5, hole=2.7, stand=5.0)
ULN_SPOTS = {"X": (170.0, -30.0, 472.0, "rail"), "Y": (170.0, 22.0, 472.0, "rail"), "F": (55.0, -50.0, 205.0, "deck")}


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


# ---------------- 급이 방 ----------------
def cotton_roll():
    f = FD
    p0 = V(f["x"], f["tip_y"], f["tip_z"])
    d = V(0, f["end_y"] - f["tip_y"], f["end_z"] - f["tip_z"])
    return Part.makeCylinder(f["roll_r"], d.Length, p0, d)


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
    px = f["x"] + f["post_dx"]
    post = box(px - pw, px + pw, f["post_y"] - pw, f["post_y"] + pw, f["post_foot_z"] + 3, f["floor_z"] + 0.01)
    foot = box(px - FOOT_DX - 6, px + FOOT_DX + 6, f["post_y"] - 10, f["post_y"] + 10, f["post_foot_z"], f["post_foot_z"] + 3)
    for sx in (-FOOT_DX, FOOT_DX):
        foot = foot.cut(Part.makeCylinder(2.75, 10, V(px + sx, f["post_y"], f["post_foot_z"] - 2)))
    return shp.fuse(post).fuse(foot).removeSplitter()


def wall_hole():
    f = FD
    return Part.makeCylinder(f["wall_hole_r"], 12, V(f["x"], 15.0, f["wall_hole_z"]), V(0, 1, 0))


def water_check():
    """물 높이 여유: 벽 구멍 아래 끝 − 물 높이, 코튼롤 바깥 끝이 잠긴 깊이"""
    f = FD
    hole_bot = f["wall_hole_z"] - f["wall_hole_r"]
    end_bot = f["end_z"] - f["roll_r"]
    return dict(level=f["mouth_z"], hole_bottom=round(hole_bot, 2), margin=round(hole_bot - f["mouth_z"], 2),
                roll_end_bottom=end_bot, immersed=round(f["mouth_z"] - end_bot, 2), floor_top=f["floor_z"] + f["floor_t"])


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
        p = (f["x"] + f["post_dx"] + sx, f["post_y"], f["post_foot_z"] + 3)
        fb.append(Part.makeCylinder(2.5, 12, V(*p), V(0, 0, -1)).fuse(Part.makeCylinder(4.25, 5, V(*p))))
        t = G.tnut_local("rail")
        t.translate(V(f["x"] + f["post_dx"] + sx - G.BR["hole_at"], f["post_y"], rail_top))   # 가로대는 x 방향 → 너트 길이도 x
        ft.append(t)
    for o in doc.Objects:
        if o.Label.startswith("101_deck"):
            sh = o.Shape
            for sx in (-FOOT_DX, FOOT_DX):
                sh = sh.cut(Part.makeCylinder(2.75, 20, V(f["x"] + f["post_dx"] + sx, f["post_y"], f["post_foot_z"] - 10)))
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


# ---------------- 떠 있던 부품 받침 (floating 검사에서 나온 것) ----------------
PI = dict(L=85.0, W=56.0, hx=58.0, hy=49.0, off=3.5, hole=2.7, h=35.0)   # Pi 5 + AI HAT+ (라즈베리파이 B 폼팩터: 구멍 58 × 49, 모서리 3.5) [확실 — 공식 기계 도면 규격]


def support_fixes(doc):
    """190 Pi 5 + AI HAT+ 를 위 가로대(y +80) 안쪽 면에 거는 선반(199a)에 얹고, G4·G6 빛 게이트 송수신기를 덕트에 붙이는 받침(199b·c)"""
    import D5e_module_kinematic as K
    out = []
    pi = [o for o in doc.Objects if o.Label.startswith("190_pi5_aihat (위판 아래")][0]
    b = pi.Shape.BoundBox
    x0, x1, z0 = b.XMin, b.XMax, b.ZMin
    rail_y = K.FR["cross_y"] - 10.0                 # 위 가로대 안쪽 면 (y 70)
    rail_z0 = K.FR["top_z"]
    y0 = rail_y - 3.0 - PI["W"] - 6.0             # (SJ-49) 벽 볼트 머리(5) 자리만큼 Pi를 6 mm 띄움
    # Pi를 판매품 크기(85 × 56)로, 선반 쪽에 붙여 다시 놓음 (구멍 4개 표시)
    board = box(x0, x0 + PI["L"], y0, y0 + PI["W"], z0, z0 + PI["h"])
    for sx in (0, PI["hx"]):
        for sy in (0, PI["hy"]):
            board = board.cut(Part.makeCylinder(PI["hole"] / 2, PI["h"] + 2, V(x0 + PI["off"] + sx, y0 + PI["off"] + sy, z0 - 1)))
    pi.Shape = board
    pi.Label = "190_pi5_aihat (85 × 56 판매품 외곽, 선반 199a 위)"
    shelf = box(x0 - 2, x0 + PI["L"] + 2, y0 - 2, rail_y, z0 - 3, z0)
    wall = box(x0 + 10, x0 + PI["L"] - 10, rail_y - 3, rail_y, z0 - 3, rail_z0 + 20)
    shp = shelf.fuse(wall)
    for sx in (x0 + 20, x0 + PI["L"] - 20):
        shp = shp.cut(Part.makeCylinder(2.75, 10, V(sx, rail_y - 5, rail_z0 + 10), V(0, 1, 0)))
    for sx in (0, PI["hx"]):
        for sy in (0, PI["hy"]):
            shp = shp.cut(Part.makeCylinder(1.1, 5, V(x0 + PI["off"] + sx, y0 + PI["off"] + sy, z0 - 4)))   # M2.5 셀프 탭 구멍
    out.append(("199a_pi_shelf (3D 프린트, 위 가로대 y+80에 M5 × 8 2개)", shp.removeSplitter()))
    for lab, nm in (("196_gate_G4_tx_rx", "199b_gate_holder_G4 (3D 프린트, 덕트 172에 끼움)"), ("196_gate_G6_tx_rx", "199c_gate_holder_G6 (3D 프린트, 덕트 174에 끼움)")):
        g = [o for o in doc.Objects if o.Label == lab][0]
        duct = [o for o in doc.Objects if o.Label.startswith("172_" if "G4" in lab else "174_")][0]
        pieces = []
        for s in g.Shape.Solids:
            d, pts, _ = s.distToShape(duct.Shape)
            p_s, p_d = pts[0]
            sb = s.BoundBox
            # 송수신기 면 → 덕트 면 사이를 송수신기 단면 크기로 채우는 받침
            lo = V(min(p_s.x, p_d.x), min(p_s.y, p_d.y), min(p_s.z, p_d.z))
            hi = V(max(p_s.x, p_d.x), max(p_s.y, p_d.y), max(p_s.z, p_d.z))
            for ax in ("x", "y", "z"):
                if getattr(hi, ax) - getattr(lo, ax) < 0.01:
                    setattr(lo, ax, getattr(sb, ax.upper() + "Min"))
                    setattr(hi, ax, getattr(sb, ax.upper() + "Max"))
            pieces.append(box(lo.x, hi.x, lo.y, hi.y, lo.z, hi.z))
        out.append((nm, Part.makeCompound(pieces)))
    objs = []
    for nm, shp in out:
        o = doc.addObject("Part::Feature", "SJF%d" % len(objs))
        o.Label = nm
        o.Shape = shp
        objs.append(o)
    doc.recompute()
    return objs


# ---------------- (11/06 20시) 벌레 막기 뚜껑 + 방생 출구 일자 ----------------
def trough_lid():
    """143l: 물길·그릇 뚜껑 (3D 프린트). 설탕물이 밖으로 드러나지 않게 덮음.
    튜브 둘레 틈 0.4 mm가 숨구멍(공기만 드나듦) → 그릇 물 표면은 바깥 공기와 이어져 '거꾸로 병' 원리 그대로"""
    f = FD
    x0, x1 = f["x"] - f["ch_w"] / 2 - f["ch_t"], f["x"] + f["ch_w"] / 2 + f["ch_t"]
    ro = f["bowl_ri"] + f["bowl_t"]
    lid = box(x0, x1, f["ch_y0"], f["tube_y"], f["wall_top"], f["wall_top"] + 2)
    lid = lid.cut(Part.makeCylinder(ro, 10, V(f["x"], f["tube_y"], f["wall_top"] - 1)))
    ring = Part.makeCylinder(ro, 2, V(f["x"], f["tube_y"], f["bowl_top"])).cut(
        Part.makeCylinder(f["tube_r"] + 0.4, 4, V(f["x"], f["tube_y"], f["bowl_top"] - 1)))
    # 물길 뚜껑과 그릇 고리를 잇는 경사 다리 2개
    bridge = box(x0, x1, f["tube_y"] - ro - 6, f["tube_y"] - ro + 1, f["wall_top"], f["bowl_top"] + 2).cut(
        Part.makeCylinder(ro, 30, V(f["x"], f["tube_y"], f["wall_top"] - 5)))
    return lid.fuse(ring).fuse(bridge).removeSplitter()


def release_exit_fix(doc):
    """175 출구 원뿔(끝 안지름 3 mm, 말벌 못 나감) → 곧은 관(안 12, 길이 15) + 위 비 가림 갓"""
    import D5e_module_kinematic as K
    old = [o for o in doc.Objects if o.Label.startswith("175_release_oneway")]
    if not old:
        return None
    b = old[0].Shape.BoundBox
    x0, z = b.XMin, K.z_upper
    pipe = Part.makeCylinder(K.DUCT_R, 15, V(x0, 0, z), V(1, 0, 0)).cut(Part.makeCylinder(K.PORT_R, 17, V(x0 - 1, 0, z), V(1, 0, 0)))
    hood = Part.makeCylinder(K.DUCT_R + 4, 12, V(x0 + 10, 0, z), V(1, 0, 0)).cut(
        Part.makeCylinder(K.DUCT_R + 2.5, 14, V(x0 + 9, 0, z), V(1, 0, 0)))
    hood = hood.common(box(x0, x0 + 30, -20, 20, z, z + 20))          # 위 반쪽만
    hood = hood.fuse(box(x0 + 10, x0 + 13, -K.DUCT_R - 4, K.DUCT_R + 4, z + K.DUCT_R - 0.5, z + K.DUCT_R + 4).common(
        Part.makeCylinder(K.DUCT_R + 4, 3, V(x0 + 10, 0, z), V(1, 0, 0))))   # 관과 갓을 잇는 턱
    old[0].Shape = pipe.fuse(hood).removeSplitter()
    old[0].Label = "175_release_exit (곧은 관 안지름 12 + 비 가림 갓, 11/06 승준)"
    doc.recompute()
    return old[0]


# ---------------- (11/06 20시) 방생: 짧게 기어 나와 위로 날아 나가는 굴뚝 ----------------
# 승준 지적: 통로가 길 필요 없음, 말벌은 기어가기보다 위로 날아오르기(상승 비행)를 좋아함.
#   한 번에 한 마리씩 내보내므로 따라갈 정찰벌이 없음 → 혼자서도 바로 찾게: 짧은 목 + 위가 밝게 열린 넓은 굴뚝.
# 자리 제약 [확실 — 모델 측정]: 마커 갠트리(206·212)가 x ≤ 118, z ≥ 396 을 오감 / 방생 서보 y −41.6 ~ −9.1, x ≤ 116.5
#   / 2020 레일(갠트리 둘레, x 160~180) 아래 면 z 452 → 굴뚝은 x 120~174, 꼭대기 z 430.
RS = dict(neck_x0=90.0, neck_x1=122.0, cx=147.0, ri=25.0, t=2.0, z_bot=355.0, z_top=430.0, floor_t=3.0,
          drain_r=1.5, led_r=2.5, led_h=8.6)


def release_shaft():
    """(174 목, 175 굴뚝, 184 출구 조명 자리) 형상. 목: 방생 문 하우징 면 x 90 → 굴뚝 벽 안 (안지름 12)"""
    import D5e_module_kinematic as K
    r, z = RS, K.z_upper
    neck = Part.makeCylinder(K.DUCT_R, r["neck_x1"] - r["neck_x0"], V(r["neck_x0"], 0, z), V(1, 0, 0)).cut(
        Part.makeCylinder(K.PORT_R, r["neck_x1"] - r["neck_x0"] + 10, V(r["neck_x0"] - 1, 0, z), V(1, 0, 0)))
    ro = r["ri"] + r["t"]
    H = r["z_top"] - r["z_bot"]
    shaft = Part.makeCylinder(ro, H, V(r["cx"], 0, r["z_bot"])).cut(
        Part.makeCylinder(r["ri"], H + 2, V(r["cx"], 0, r["z_bot"] + r["floor_t"])))
    shaft = shaft.cut(Part.makeCylinder(K.PORT_R, 2 * ro, V(r["cx"] - ro - 5, 0, z), V(1, 0, 0)).common(
        box(r["cx"] - ro - 6, r["cx"], -20, 20, z - 10, z + 10)))                      # 목이 들어오는 옆 구멍
    neck = neck.cut(Part.makeCylinder(r["ri"], H + 2, V(r["cx"], 0, r["z_bot"] + r["floor_t"])))
    import math
    for k in range(4):                                                                   # 빗물 빠지는 구멍 4 (Ø3, 말벌 못 지나감)
        a = math.radians(45 + 90 * k)
        shaft = shaft.cut(Part.makeCylinder(r["drain_r"], 10, V(r["cx"] + 12 * math.cos(a), 12 * math.sin(a), r["z_bot"] - 2)))
    leds = []
    for k in range(3):                                                                   # 출구 조명 LED 3개: 꼭대기 테두리, 안쪽 위를 비춤
        a = math.radians(90 + 120 * k)
        p = V(r["cx"] + (r["ri"] + r["t"] / 2) * math.cos(a), (r["ri"] + r["t"] / 2) * math.sin(a), r["z_top"])
        leds.append(Part.makeCylinder(r["led_r"], r["led_h"], p))
    neck = neck.cut(shaft)                                                               # 이음매: 굴뚝 벽까지만 (한 덩어리로 출력)
    return neck.removeSplitter(), shaft.removeSplitter(), Part.makeCompound(leds)


def release_shaft_apply(doc):
    """174·175를 바꾸고, 출구 빛 게이트 G6(·받침)을 목 위로 옮김 (x 120 → 108)"""
    neck, shaft, leds = release_shaft()
    for o in doc.Objects:
        if o.Label.startswith("174_release_duct"):
            o.Shape = neck
            o.Label = "174_release_neck (짧은 목 30 mm, 안지름 12 — 굴뚝과 한 덩어리 출력)"
        elif o.Label.startswith("175_release"):
            o.Shape = shaft
            o.Label = "175_release_shaft (위로 열린 굴뚝 안지름 50, 꼭대기 z 430, 빗물 구멍 4)"
    # (11/06 20:13 승준 결정) 출구 조명 LED 뺌: 굴뚝 위가 하늘로 열려 낮에는 이미 밝음, 방생 때 마킹실 조명만 끄면 굴뚝 쪽이 더 밝음.
    #   밤 LED는 나방 등 다른 벌레를 부름. 상용 트랩도 조명 없이 씀.
    for o in [o for o in doc.Objects if o.Label.startswith("184_exit_light")]:
        doc.removeObject(o.Name)
    o = None
    dx = 108.0 - 120.0
    for g in doc.Objects:
        if g.Label.startswith(("196_gate_G6", "199c_gate_holder_G6")) and hasattr(g, "Shape"):
            if abs(g.Shape.BoundBox.Center.x - 120.0) < 1.0:
                s = g.Shape.copy()
                s.translate(V(dx, 0, 0))
                g.Shape = s
    doc.recompute()
    return o


# ---------------- (11/06 밤, CAP-AI-SJ-49) 급이 방 상세설계: 고정·뚜껑 나사·튜브 집게·코튼롤 잡이 ----------------
# 구매품 (McMaster 페이지에서 직접 확인, 11/06):
#   열 압입 인서트 M3 × 0.5, 설치 길이 4.3, 구멍 Ø4.0, 최소 살 두께 5.1 — 94459A130 (50개 $10.91) [확실 — McMaster 표]
#   손나사(손으로 돌리는 나사) M3 × 8, 머리 Ø8 × 5, 18-8 스테인리스 — 92545A111 ($1.73) [확실 — McMaster 표]
#   육각 구멍 볼트 M3 × 8, 머리 Ø5.5 × 3, 18-8 스테인리스 — 91292A112 (100개 $6.46) [확실 — McMaster 표]
#   50 mL 원뿔 튜브 PP Ø30 × 114.3, 입구 안 27 — 7979T44 (25개 $23.79) = 코닝 352070과 같은 규격 [확실 — McMaster 표]
#   코튼롤: McMaster에 없음 → 치과 재료상 '코튼롤 2호 Ø10 × 38' (국내 판매처 여럿) [가능성 높음]
INS = dict(hole=4.0, L=4.3, min_wall=5.1, boss_r=4.0, depth=6.0)        # 인서트 구멍은 6 깊이 (4.3 + 여유)
TS = dict(d=3.0, L=8.0, head_d=8.0, head_h=5.0)                          # 손나사 92545A111
SC = dict(d=3.0, L=8.0, head_d=5.5, head_h=3.0)                          # M3 × 8 91292A112
FDX = dict(ear_dx=13.0, ear_z=368.0, ear_y0=29.0, ear_t=3.0,             # 물길 귀 (마킹실 벽 보스에 M3 × 8)
           lid_dx=11.0, lid_y=(40.0, 66.0),                              # 뚜껑 손나사 자리 (물길 양옆 기둥 위)
           clip_z=(424.0, 434.0), clip_open=120.0,                       # 튜브 집게 고리
           col=(75.6, 79.6), pinch=(44.0, 48.0))                         # 집게 기둥 x, 코튼롤 잡이 y


def _screw(p, d, L, head_d, head_h, down=V(0, 0, -1)):
    return Part.makeCylinder(d / 2, L, p, down).fuse(Part.makeCylinder(head_d / 2, head_h, p, down * -1))


def feeder_detail_shapes(chamber_shape):
    """반환: (새 143 물길, 새 143l 뚜껑, 새 120 마킹실 벽, 인서트 묶음, 손나사 묶음, M3 볼트 묶음)
    1) 마킹실 벽 바깥(+y 면 y 23)에 보스 2개 (Ø8, 6 길이, 인서트) — 물길 양옆 귀를 M3 × 8로 조임 → 물길 앞이 벽에 꽉 붙음
    2) 물길 양옆에 세로 기둥 2개 (Ø8, 위에 인서트) — 뚜껑을 손나사 2개로 누름 (공구 없이 열어 코튼롤 갈기)
    3) 그릇 +x 옆 기둥 → 튜브 집게 고리 (입구 120° 열림, 똑딱 끼움: 열린 폭 26.3 < 튜브 29.7)
    4) 물길 안 코튼롤 잡이 리브 2개 (틈 10 = 롤 지름) — 물은 리브 옆이 아니라 위아래로 흐름 (리브는 벽에서 1 mm만 나옴)"""
    import math
    f, e = FD, FDX
    ch_x0, ch_x1 = f["x"] - f["ch_w"] / 2 - f["ch_t"], f["x"] + f["ch_w"] / 2 + f["ch_t"]
    trough = feed_trough()
    ins, ts, sc = [], [], []
    # 1) 벽 보스 + 귀
    wall = chamber_shape
    for sx in (-1, 1):
        cx = f["x"] + sx * e["ear_dx"]
        boss = Part.makeCylinder(INS["boss_r"], e["ear_y0"] - 23.0, V(cx, 23.0 - 0.2, e["ear_z"]), V(0, 1, 0))
        wall = wall.fuse(boss)
        wall = wall.cut(Part.makeCylinder(INS["hole"] / 2, INS["depth"], V(cx, e["ear_y0"] - INS["depth"], e["ear_z"]), V(0, 1, 0)))
        ins.append(Part.makeCylinder(INS["hole"] / 2 + 0.35, INS["L"], V(cx, e["ear_y0"] - INS["L"], e["ear_z"]), V(0, 1, 0)).cut(
            Part.makeCylinder(1.25, 10, V(cx, e["ear_y0"] - 6, e["ear_z"]), V(0, 1, 0))))
        x_in = ch_x0 if sx < 0 else ch_x1
        ear = box(min(x_in, cx - 5), max(x_in, cx + 5), e["ear_y0"], e["ear_y0"] + e["ear_t"], e["ear_z"] - 5, e["ear_z"] + 5)
        ear = ear.cut(Part.makeCylinder(1.7, 10, V(cx, e["ear_y0"] - 1, e["ear_z"]), V(0, 1, 0)))
        trough = trough.fuse(ear)
        sc.append(_screw(V(cx, e["ear_y0"] + e["ear_t"], e["ear_z"]), SC["d"], SC["L"], SC["head_d"], SC["head_h"], V(0, -1, 0)))
    # 2) 뚜껑 기둥 (물길 양옆)
    for sx in (-1, 1):
        cx = f["x"] + sx * e["lid_dx"]
        for cy in e["lid_y"]:
            col = Part.makeCylinder(INS["boss_r"], f["wall_top"] - f["floor_z"], V(cx, cy, f["floor_z"]))
            trough = trough.fuse(col)
            trough = trough.cut(Part.makeCylinder(INS["hole"] / 2, INS["depth"], V(cx, cy, f["wall_top"] - INS["depth"])))
            ins.append(Part.makeCylinder(INS["hole"] / 2 + 0.35, INS["L"], V(cx, cy, f["wall_top"] - INS["L"])).cut(
                Part.makeCylinder(1.25, 10, V(cx, cy, f["wall_top"] - 6))))
    trough = trough.cut(box(f["x"] - f["ch_w"] / 2, f["x"] + f["ch_w"] / 2, f["ch_y0"] - 1, f["ch_y1"], f["floor_z"] + f["floor_t"], f["wall_top"] + 1))
    # 3) 튜브 집게
    ro = f["bowl_ri"] + f["bowl_t"]
    c0, c1 = e["col"]
    col = box(c0, c1, f["tube_y"] - 4, f["tube_y"] + 4, f["floor_z"], e["clip_z"][1])
    trough = trough.fuse(col.cut(Part.makeCylinder(ro + 0.3, 200, V(f["x"], f["tube_y"], f["floor_z"] - 1))).fuse(
        box(c0 - 1.5, c1, f["tube_y"] - 4, f["tube_y"] + 4, f["floor_z"], f["bowl_top"])))           # 아래는 그릇 벽에 붙임
    ri_c = f["tube_r"] + 0.3
    h = e["clip_z"][1] - e["clip_z"][0]
    ring = Part.makeCylinder(ri_c + 2.5, h, V(f["x"], f["tube_y"], e["clip_z"][0])).cut(
        Part.makeCylinder(ri_c, h + 2, V(f["x"], f["tube_y"], e["clip_z"][0] - 1)))
    a = math.radians(e["clip_open"] / 2)
    z0 = e["clip_z"][0] - 1
    wedge = Part.Face(Part.makePolygon([V(f["x"], f["tube_y"], z0), V(f["x"] - 40, f["tube_y"] - 40 * math.tan(a), z0),
                                        V(f["x"] - 40, f["tube_y"] + 40 * math.tan(a), z0), V(f["x"], f["tube_y"], z0)])).extrude(V(0, 0, h + 2))
    ring = ring.cut(wedge)                                                              # -x 쪽 120° 열림 (튜브를 옆에서 밀어 끼움)
    arm = box(f["x"] + ri_c + 1.5, c1, f["tube_y"] - 4, f["tube_y"] + 4, e["clip_z"][0], e["clip_z"][1])
    trough = trough.fuse(ring).fuse(arm)
    # 4) 코튼롤 잡이 리브
    p0, p1 = e["pinch"]
    for xr in ((f["x"] - f["ch_w"] / 2, f["x"] - f["ch_w"] / 2 + 1.0), (f["x"] + f["ch_w"] / 2 - 1.0, f["x"] + f["ch_w"] / 2)):
        trough = trough.fuse(box(xr[0], xr[1], p0, p1, f["floor_z"] + f["floor_t"] + 4.0, f["wall_top"]))
    # 뚜껑: 귀 4개에 Ø3.4 구멍, 손나사
    lid = trough_lid()
    for sx in (-1, 1):
        cx = f["x"] + sx * e["lid_dx"]
        for cy in e["lid_y"]:
            lid = lid.fuse(Part.makeCylinder(INS["boss_r"] + 1, 2, V(cx, cy, f["wall_top"]))).cut(
                Part.makeCylinder(1.7, 10, V(cx, cy, f["wall_top"] - 3)))
            ts.append(_screw(V(cx, cy, f["wall_top"] + 2), TS["d"], TS["L"], TS["head_d"], TS["head_h"]))
    return (trough.removeSplitter(), lid.removeSplitter(), wall.removeSplitter(),
            Part.makeCompound(ins), Part.makeCompound(ts), Part.makeCompound(sc))


def feeder_detail_apply(doc):
    ch = [o for o in doc.Objects if o.Label.startswith("120_chamber_walls")][0]
    tr = [o for o in doc.Objects if o.Label.startswith("143_feed_trough")][0]
    ld = [o for o in doc.Objects if o.Label.startswith("143l_")][0]
    trough, lid, wall, ins, ts, sc = feeder_detail_shapes(ch.Shape)
    tr.Shape, ld.Shape, ch.Shape = trough, lid, wall
    tr.Label = "143_feed_trough (설탕물 물길·그릇·튜브 집게, 3D 프린트 PETG, 벽 2.0·그릇 2.5)"
    ld.Label = "143l_feed_trough_lid (뚜껑 2, PETG — 손나사 4개로 누름, 공구 없이 열기)"
    ch.Label = "120_chamber_walls (+y 벽 Ø11.2 급이 구멍, 물길 고정 보스 2)"
    out = []
    for nm, shp, col in (("143i_insert_M3_heatset (McMaster 94459A130, 6개)", ins, (0.80, 0.65, 0.25)),
                         ("143t_thumbscrew_M3x8 (McMaster 92545A111, 4개)", ts, (0.75, 0.75, 0.78)),
                         ("143s_bolt_M3x8 (McMaster 91292A112, 2개)", sc, (0.15, 0.15, 0.15))):
        for o in [o for o in doc.Objects if o.Label.startswith(nm.split(" ")[0])]:
            doc.removeObject(o.Name)
        o = doc.addObject("Part::Feature", "P" + nm.split(" ")[0])
        o.Label, o.Shape = nm, shp
        out.append((o, col))
    doc.recompute()
    return out


# ---------------- (CAP-AI-SJ-49) 막대 로드셀 148: 버튼형 → Adafruit 4540 (1 kg, 80 × 12.7 × 12.7) ----------------
# 치수 [확실 — Adafruit 상품 페이지 'Product Dimensions 80.0 × 12.7 × 12.7']
# 구멍 [가능성 높음 — 데이터시트 그림(해상도 낮음)]: 한쪽 끝 2-M4 × 0.7 관통 탭, 다른 끝 2-M5 × 0.8 관통 탭, 끝에서 5·20 (간격 15)
# 자리: 바닥 구동 상자(151 옆판 x 32~36 / 74~78, y ±23) 안은 x 폭 38 → 80 막대가 x로 못 들어감.
#   −y 쪽은 커플링 154(중심 (55, −13), 반지름 10)가 막음 → 막대는 +y로 뻗음, x 60.15~72.85 (커플링까지 1.9, 옆판까지 1.15)
#   자유 끝(M4) y −2.5: 스프링 146이 축 (65, 4)에서 이 끝 블록을 누름 → 받침판 148s(PETG)가 힘을 받아 막대에 전함
#   고정 끝(M5) y 77.5: 캐리지 158에서 +y로 나온 팔(158a, 캐리지와 한 몸 출력)에 M5 × 12 두 개로 매닮 (McMaster 91292A125)
#   막대 높이 z 229.3~242 (모터판 152 윗면 228과 1.3 틈), 받침판 242~244 → 스프링 아래 끝 244 (D5f 값 그대로)
LC = dict(L=80.0, a=12.7, xc=66.5, y_free=-2.5, z_bot=229.3, hole_e=(5.0, 20.0), m4=4.0, m5=5.0,
          gauge=(25.0, 55.0), seat_t=2.0, arm_gap=1.0)


def loadcell_bar():
    """판매품 모양: 몸통 + 가운데 구멍 두 개(스트레인 게이지 자리, 흰 덮개는 검정 띠로) + 끝 구멍 4"""
    c = LC
    x0, y0, z0 = c["xc"] - c["a"] / 2, c["y_free"], c["z_bot"]
    body = Part.makeBox(c["a"], c["L"], c["a"], V(x0, y0, z0))
    for yy in (c["gauge"][0] + 6.0, c["gauge"][1] - 6.0):                     # 굽힘 구멍 2개 (가로 관통, 이어진 모양)
        body = body.cut(Part.makeCylinder(5.0, c["a"] + 2, V(x0 - 1, y0 + yy, z0 + c["a"] / 2), V(1, 0, 0)))
    body = body.cut(Part.makeBox(c["a"] + 2, c["gauge"][1] - c["gauge"][0] - 12.0, 4.0, V(x0 - 1, y0 + c["gauge"][0] + 6.0, z0 + c["a"] / 2 - 2)))
    for e, d in ((c["hole_e"][0], c["m4"]), (c["hole_e"][1], c["m4"])):
        body = body.cut(Part.makeCylinder(d / 2, c["a"] + 2, V(c["xc"], y0 + e, z0 - 1)))
    for e in c["hole_e"]:
        body = body.cut(Part.makeCylinder(c["m5"] / 2, c["a"] + 2, V(c["xc"], y0 + c["L"] - e, z0 - 1)))
    gauge = Part.makeBox(c["a"] + 0.4, c["gauge"][1] - c["gauge"][0], 1.0, V(x0 - 0.2, y0 + c["gauge"][0], z0 + c["a"]))   # 게이지 덮개(흰 실리콘)
    return body.removeSplitter(), gauge


def loadcell_parts(carriage_shape):
    """반환: 새 캐리지(아래 컵 지우고 +y 팔), 막대, 덮개, 받침판, M4 볼트, M5 볼트"""
    c = LC
    x0, x1 = c["xc"] - c["a"] / 2, c["xc"] + c["a"] / 2
    ytop = c["z_bot"] + c["a"]                                       # 242
    # 1) 캐리지: D5f 아래 컵 지움 (축·스프링 자리는 그대로 비움)
    car = carriage_shape.cut(Part.makeCylinder(7.6, 262.0 - 230.0 - 0.01, V(65.0, 4.0, 230.0)))
    # 2) 팔 158a: 캐리지 +y 면(y 20) → y 77.5, 아래 면은 막대 위 1 mm (고정 끝 25 mm만 막대에 닿음)
    yf = c["y_free"] + c["L"]                                        # 77.5
    y_fix0 = yf - 25.0
    arm = box(x0, x1, 19.0, yf, ytop + c["arm_gap"], 274.0)
    arm = arm.fuse(box(x0, x1, y_fix0, yf, ytop, ytop + c["arm_gap"]))
    bolts5 = []
    for e in c["hole_e"]:
        yy = yf - e
        arm = arm.cut(Part.makeCylinder(2.75, 40, V(c["xc"], yy, ytop - 1)))                 # M5 지나는 구멍
        arm = arm.cut(Part.makeCylinder(4.75, 40, V(c["xc"], yy, ytop + 5.0)))              # 머리 자리 (위에서 육각 렌치)
        p = V(c["xc"], yy, ytop + 5.0)
        bolts5.append(Part.makeCylinder(2.5, 12, p, V(0, 0, -1)).fuse(Part.makeCylinder(4.25, 5, p)))
    car = car.fuse(arm).removeSplitter()
    # 3) 받침판 148s: 자유 끝 위, 끝 턱(아래로 3)으로 돌지 않게, M4 × 10 한 개 (y −2.5 + 20), 스프링 가운데 핀 Ø2.2
    ys0, ys1 = c["y_free"] - 2.0, c["y_free"] + 23.0
    seat = box(x0, x1, ys0, ys1, ytop, ytop + c["seat_t"])
    seat = seat.fuse(box(x0, x1, ys0, c["y_free"], ytop - 3.0, ytop))
    seat = seat.fuse(Part.makeCylinder(1.1, 1.5, V(65.0, 4.0, ytop + c["seat_t"])))
    yb = c["y_free"] + c["hole_e"][1]
    seat = seat.cut(Part.makeCylinder(2.2, 10, V(c["xc"], yb, ytop - 1)))
    p = V(c["xc"], yb, ytop + c["seat_t"])
    bolt4 = Part.makeCylinder(2.0, 10, p, V(0, 0, -1)).fuse(Part.makeCylinder(3.5, 4, p))
    bar, gauge = loadcell_bar()
    return car, bar, gauge, seat.removeSplitter(), bolt4, Part.makeCompound(bolts5)


def loadcell_apply(doc):
    car_o = [o for o in doc.Objects if o.Label.startswith("158_carriage")][0]
    for o in [o for o in doc.Objects if o.Label.startswith(("148_load_cell", "148b_", "148g_", "148s_", "148m"))]:
        doc.removeObject(o.Name)
    car, bar, gauge, seat, b4, b5 = loadcell_parts(car_o.Shape)
    car_o.Shape = car
    car_o.Label = "158_carriage (바닥 캐리지 + 로드셀 팔 158a, 3D 프린트 PETG)"
    out = []
    for nm, shp, col in (("148_load_cell_bar (Adafruit 4540 1 kg, 80 × 12.7 × 12.7, 구매)", bar, (0.75, 0.77, 0.80)),
                         ("148g_load_cell_gauge_cover (로드셀에 붙어 옴)", gauge, (0.95, 0.95, 0.95)),
                         ("148s_spring_seat (스프링 받침판, 3D 프린트 PETG)", seat, None),
                         ("148m4_bolt_M4x10 (받침판 → 로드셀 자유 끝, McMaster 91292A116)", b4, (0.15, 0.15, 0.15)),
                         ("148m5_bolt_M5x12 × 2 (팔 → 로드셀 고정 끝, McMaster 91292A125)", b5, (0.15, 0.15, 0.15))):
        o = doc.addObject("Part::Feature", "P" + nm.split(" ")[0])
        o.Label, o.Shape = nm, shp
        out.append((o, col))
    doc.recompute()
    return out
