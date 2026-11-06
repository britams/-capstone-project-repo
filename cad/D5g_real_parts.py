# -*- coding: utf-8 -*-
"""D5g 실제 전기 부품 CAD (승준, 2026-11-06, CAP-AI-SJ-41)

자리 상자를 외부 공개 CAD(STEP)로 만든 실제 모양으로 바꾼다. 승준 PC의 FreeCAD가 인터넷에서 직접 받고(임시 폴더에 저장),
레포에는 STEP을 올리지 않는다 (용량·라이선스 — 출처 주소만 기록).

출처 (모두 공개)
- KiCad 공식 3D 라이브러리 (github.com/KiCad/kicad-packages3D, CC-BY-SA 4.0 + 설계 사용 예외):
  DIP-16 (ULN2003A), JST XH 5핀 세움 (모터 소켓), 핀 헤더 1×4·1×2, LED Ø3, 단자대 Phoenix PT 1,5 5.0 mm, 퓨즈 홀더 5×20 (Bulgin FX0457)
- 라즈베리파이 공식: datasheets.raspberrypi.com/rpi5/RaspberryPi5-step.zip
- ULN2003 기판: 판매 규격 35 × 31.9 × 1.6, M2.5 구멍 간격 30 × 26.5 (판매처 2곳) [가능성 높음]
  부품 배치(칩 가운데, 모터 소켓 위 가장자리, LED 4개 오른쪽, 입력 1×4 아래 왼쪽, 전원 −+ 1×2·점퍼 1×2 아래 오른쪽)는
  판매 사진의 배치 [가능성 높음 — ±2 mm, 실물 보드로 확인]. 부품 하나하나의 모양·크기는 KiCad STEP 그대로 [확실]

실행: import D5g_real_parts as R; R.apply(doc)   (doc = D5g_frame_detail)
"""
import os
import tempfile
import urllib.parse
import urllib.request
import zipfile

import FreeCAD as App
import Part

V = App.Vector
CACHE = os.path.join(tempfile.gettempdir(), "sj_capstone_parts")
KICAD = "https://raw.githubusercontent.com/KiCad/kicad-packages3D/master/"
SRC = {
    "dip16": KICAD + "Package_DIP.3dshapes/DIP-16_W7.62mm.step",
    "xh5": KICAD + "Connector_JST.3dshapes/JST_XH_B5B-XH-A_1x05_P2.50mm_Vertical.step",
    "xh4": KICAD + "Connector_JST.3dshapes/JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical.step",
    "hdr4": KICAD + "Connector_PinHeader_2.54mm.3dshapes/PinHeader_1x04_P2.54mm_Vertical.step",
    "hdr2": KICAD + "Connector_PinHeader_2.54mm.3dshapes/PinHeader_1x02_P2.54mm_Vertical.step",
    "led3": KICAD + "LED_THT.3dshapes/LED_D3.0mm.step",
    "tb4": KICAD + "TerminalBlock_Phoenix.3dshapes/TerminalBlock_Phoenix_PT-1,5-4-5.0-H_1x04_P5.00mm_Horizontal.step",
    "fuse": KICAD + "Fuse.3dshapes/Fuseholder_Cylinder-5x20mm_Bulgin_FX0457_Horizontal_Closed.step",
    "pi5zip": "https://datasheets.raspberrypi.com/rpi5/RaspberryPi5-step.zip",
    "dip28": KICAD + "Package_DIP.3dshapes/DIP-28_W7.62mm.step",
    "sock8": KICAD + "Connector_PinSocket_2.54mm.3dshapes/PinSocket_1x08_P2.54mm_Vertical.step",
    "sock10": KICAD + "Connector_PinSocket_2.54mm.3dshapes/PinSocket_1x10_P2.54mm_Vertical.step",
    "sock6": KICAD + "Connector_PinSocket_2.54mm.3dshapes/PinSocket_1x06_P2.54mm_Vertical.step",
    "jack": KICAD + "Connector_BarrelJack.3dshapes/BarrelJack_CUI_PJ-063AH_Horizontal.step",
}
ULN = dict(L=35.0, W=31.9, t=1.6, hx=30.0, hy=26.5, hole=3.0)
# 보드 중심 기준 배치 (x: 35 방향, y: 31.9 방향), 회전(도, z축)
ULN_LAYOUT = [
    ("dip16", (-2.0, 0.5), 90),     # 칩: 긴 쪽이 x
    ("xh5", (-2.0, 12.0), 90),      # 모터 소켓: 위 가장자리, 긴 쪽 x
    ("led3", (13.5, 9.0), 0), ("led3", (13.5, 4.0), 0), ("led3", (13.5, -1.0), 0), ("led3", (13.5, -6.0), 0),
    ("hdr4", (-9.0, -12.5), 90),    # IN1~IN4
    ("hdr2", (5.0, -12.5), 90),     # 전원 − +
    ("hdr2", (11.5, -12.5), 90),    # ON/OFF 점퍼
]


def fetch(key):
    os.makedirs(CACHE, exist_ok=True)
    url = SRC[key]
    fn = os.path.join(CACHE, key + (".zip" if url.endswith(".zip") else ".step"))
    if not os.path.exists(fn) or os.path.getsize(fn) < 1000:
        parts = urllib.parse.urlsplit(url)
        safe = urllib.parse.urlunsplit((parts.scheme, parts.netloc, urllib.parse.quote(parts.path), "", ""))
        req = urllib.request.Request(safe, headers={"User-Agent": "FreeCAD-capstone"})
        data = urllib.request.urlopen(req, timeout=120).read()
        open(fn, "wb").write(data)
    return fn


_MEMO = {}


def load(key):
    if key not in _MEMO:
        s = Part.Shape()
        s.read(fetch(key))
        _MEMO[key] = s
    return _MEMO[key].copy()


def place_xy(shp, cx, cy, z0, rot=0):
    """KiCad 모델: z = 0 이 기판 윗면. rot = 90 이면 긴 쪽을 x 방향으로 돌림. XY는 바운딩 박스 가운데를 (cx, cy)로"""
    s = shp.copy()
    if rot:
        b = s.BoundBox
        if b.YLength > b.XLength:
            s.rotate(V(0, 0, 0), V(0, 0, 1), 90)
    b = s.BoundBox
    s.translate(V(cx - b.Center.x, cy - b.Center.y, z0))
    return s


def uln_board(cx, cy, zb):
    """zb = 기판 아래 면 높이. 반환: (보드+부품 compound)"""
    u = ULN
    pcb = Part.makeBox(u["L"], u["W"], u["t"], V(cx - u["L"] / 2, cy - u["W"] / 2, zb))
    for sx in (-1, 1):
        for sy in (-1, 1):
            pcb = pcb.cut(Part.makeCylinder(u["hole"] / 2, 5, V(cx + sx * u["hx"] / 2, cy + sy * u["hy"] / 2, zb - 1)))
    parts = [pcb]
    zt = zb + u["t"]
    for key, (dx, dy), rot in ULN_LAYOUT:
        parts.append(place_xy(load(key), cx + dx, cy + dy, zt, rot))
    return Part.makeCompound(parts)


def terminal_fuse(x0, x1, y0, y1, zb):
    """193: 3D 프린트 받침(바닥 2 + 다리 4) + 만능기판 1.6 + 단자대 4핀 × 2 (+5 V 줄 / GND 줄) + 퓨즈 홀더 5×20
    단자대·퓨즈 홀더는 기판에 꽂는 부품(다리가 기판 밑으로 3.6~5.0 나옴) → 기판을 받침 위 4 mm에 띄움"""
    base = Part.makeBox(x1 - x0, y1 - y0, 2.0, V(x0, y0, zb))
    for sx in (x0, x1 - 4):
        for sy in (y0, y1 - 4):
            base = base.fuse(Part.makeBox(4, 4, 4.0, V(sx, sy, zb + 2.0)))
    pcb = Part.makeBox(x1 - x0, y1 - y0, 1.6, V(x0, y0, zb + 6.0))
    zt = zb + 7.6
    tb = load("tb4")
    fu = load("fuse")
    yc = (y0 + y1) / 2
    a = place_xy(tb, x0 + 12, yc - 5.5, zt, 90)       # +5 V 줄
    b2 = place_xy(tb, x0 + 12, yc + 5.5, zt, 90)      # GND 줄
    f = place_xy(fu, x1 - 19, yc, zt, 90)
    return base.removeSplitter(), Part.makeCompound([pcb, a, b2, f])


PI_HOLES = dict(px=58.0, py=49.0, off=3.5)   # B 폼팩터 [확실]
PI_STAND = 5.0                                 # M2.5 × 5 기둥 (구매)


def pi5(x0, y0, z_shelf):
    """공식 STEP. 기판을 눕히고(가장 얇은 쪽 = z), 85 쪽을 x로.
    M2.5 구멍 4개(반지름 1.2~1.5 원통)를 찾아 선반 구멍((x0+3.5, y0+3.5)부터 58 × 49)에 맞추고, 기판 아래 면 = 선반 + 기둥 5"""
    fn = fetch("pi5zip")
    d = os.path.join(CACHE, "pi5")
    if not os.path.isdir(d):
        zipfile.ZipFile(fn).extractall(d)
    steps = [os.path.join(r, f) for r, _, fs in os.walk(d) for f in fs if f.lower().endswith((".step", ".stp"))]
    path = sorted(steps, key=os.path.getsize)[-1]
    s = Part.Shape()
    s.read(path)
    b = s.BoundBox
    dims = [b.XLength, b.YLength, b.ZLength]
    if dims.index(min(dims)) == 1:
        s.rotate(b.Center, V(1, 0, 0), 90)
    elif dims.index(min(dims)) == 0:
        s.rotate(b.Center, V(0, 1, 0), 90)
    b = s.BoundBox
    if b.YLength > b.XLength:
        s.rotate(b.Center, V(0, 0, 1), 90)
    holes = {}
    for f in s.Faces:
        if f.Surface.TypeId == "Part::GeomCylinder" and 1.2 <= f.Surface.Radius <= 1.5 and abs(f.Surface.Axis.z) > 0.99:
            c = f.Surface.Center
            holes[(round(c.x, 1), round(c.y, 1))] = f
    pts = sorted(holes)
    # 4 구멍 = x, y 각각 58 / 49 떨어진 짝
    xs = sorted({p[0] for p in pts})
    ys = sorted({p[1] for p in pts})
    hx0, hy0 = None, None
    for xa in xs:
        for ya in ys:
            if any(abs(xb - xa - PI_HOLES["px"]) < 0.3 for xb in xs) and any(abs(yb - ya - PI_HOLES["py"]) < 0.3 for yb in ys):
                hx0, hy0 = xa, ya
                break
        if hx0 is not None:
            break
    flats = sorted([f for f in s.Faces if f.Surface.TypeId == "Part::GeomPlane" and abs(f.normalAt(0, 0).z) > 0.99 and f.Area > 3000],
                   key=lambda f: f.CenterOfMass.z)
    z_bot = flats[0].CenterOfMass.z if flats else s.BoundBox.ZMin
    if hx0 is None:
        b = s.BoundBox
        hx0, hy0 = b.XMin + PI_HOLES["off"], b.YMin + PI_HOLES["off"]
        note = "구멍 못 찾음 — 외곽 맞춤"
    else:
        note = "구멍 4개 맞춤"
    s.translate(V(x0 + PI_HOLES["off"] - hx0, y0 + PI_HOLES["off"] - hy0, z_shelf + PI_STAND - z_bot))
    stands = [Part.makeCylinder(2.5, PI_STAND, V(x0 + PI_HOLES["off"] + sx, y0 + PI_HOLES["off"] + sy, z_shelf))
              for sx in (0, PI_HOLES["px"]) for sy in (0, PI_HOLES["py"])]
    return s, os.path.basename(path), note, Part.makeCompound(stands)


def apply(doc):
    """D5g 문서의 ULN2003 3장, 193 단자대·퓨즈 상자, Pi 5 외곽을 실제 CAD로"""
    out = []
    for o in [x for x in doc.Objects if x.Label.startswith("195p_uln2003_")]:
        b = o.Shape.BoundBox
        k = o.Label.split("_")[2].split(" ")[0]
        zb = min(f.CenterOfMass.z for f in o.Shape.Faces if abs(f.normalAt(0, 0).z) > 0.99 and f.Area > 900)
        o.Shape = uln_board(b.Center.x, b.Center.y, zb)
        o.Label = "195p_uln2003_%s (KiCad STEP 부품 + 판매 규격 기판)" % k
        out.append(o.Label)
    tf = [x for x in doc.Objects if x.Label.startswith("193_terminal_fuse")]
    if tf and False:   # 11/06 20:23 와고로 바꿈 → apply_wago()
        b = tf[0].Shape.BoundBox
        base, parts = terminal_fuse(b.XMin - 6, b.XMax + 10, b.YMin - 5, b.YMax + 5, b.ZMin)
        doc.removeObject(tf[0].Name)
        o1 = doc.addObject("Part::Feature", "SJR_tb_base")
        o1.Label = "193b_terminal_base (3D 프린트, 데크에 M3 × 2)"
        o1.Shape = base
        o2 = doc.addObject("Part::Feature", "SJR_tb")
        o2.Label = "193_terminal_fuse (KiCad STEP: 단자대 4핀 × 2 + 퓨즈 홀더 5×20)"
        o2.Shape = parts
        out += [o1.Label, o2.Label]
    pi = [x for x in doc.Objects if x.Label.startswith(("190_pi5_aihat (85", "190_pi5_aihat 외곽"))]
    if pi:
        b = pi[0].Shape.BoundBox
        for o in [x for x in doc.Objects if x.Label.startswith(("190r_", "198p_"))]:
            doc.removeObject(o.Name)
        try:
            s, nm, note, stands = pi5(b.XMin, b.YMin, b.ZMin)
            o = doc.addObject("Part::Feature", "SJR_pi5")
            o.Label = "190r_raspberry_pi5 (공식 STEP %s, %s)" % (nm, note)
            o.Shape = s
            o2 = doc.addObject("Part::Feature", "SJR_pi5_st")
            o2.Label = "198p_pi_standoff (M2.5 × 5 기둥 4, 구매)"
            o2.Shape = stands
            pi[0].Label = "190_pi5_aihat 외곽 (AI HAT+ 자리, 반투명 — 숨김)"
            if App.GuiUp:
                pi[0].ViewObject.Visibility = False
            out += [o.Label, o2.Label]
        except Exception as e:
            out.append("Pi 5 STEP 실패: %s" % e)
    apply_wago(doc)
    apply_uno(doc)
    apply_gates_estop(doc)
    apply_circuit_extras(doc)
    doc.recompute()
    return out


# ---------------- (11/06 20:23 승준 결정) 단자대·퓨즈 기판 → 와고 레버 커넥터 ----------------
# 와고 221-415 (5구, 1극): 폭 29.9 × 깊이 18.6 × 높이 8.3 [가능성 높음 — 판매처 표기]. 전선은 앞(깊이 방향)으로 꽂고 레버는 위.
# + 줄 1개, − 줄 1개. 퓨즈는 어댑터 + 전선 중간의 줄 퓨즈(5×20 T2.5A) — 전선에 매달려 데크 자리 없음.
WAGO = dict(W=29.9, D=18.6, H=8.3, n=5, hole=4.0, lever_w=4.2, lever_l=12.0, lever_t=1.6)


def wago_221(x0, y0, z0, front=-1):
    """모서리 (x0, y0, z0)에서 시작하는 221-415 한 개. front=-1 이면 전선 구멍이 −y 쪽"""
    w = WAGO
    body = Part.makeBox(w["W"], w["D"], w["H"], V(x0, y0, z0))
    pitch = w["W"] / w["n"]
    yf = y0 if front < 0 else y0 + w["D"]
    levers = []
    for i in range(w["n"]):
        cx = x0 + pitch * (i + 0.5)
        d = V(0, 1, 0) if front < 0 else V(0, -1, 0)                     # 앞면에서 안쪽으로
        p0 = V(cx, yf - 0.5 * (1 if front < 0 else -1) * 0, z0 + 3.0)
        body = body.cut(Part.makeCylinder(w["hole"] / 2, 10, p0 - d * 1.0, d))
        levers.append(Part.makeBox(w["lever_w"], w["lever_l"], w["lever_t"], V(cx - w["lever_w"] / 2, y0 + w["D"] - w["lever_l"] - 1, z0 + w["H"])))
    return body.removeSplitter(), Part.makeCompound(levers)


def wago_holder(cx, cy, zb):
    """193h 받침 (3D 프린트): 바닥 2 + 와고 두 개를 끼우는 낮은 벽(높이 4), 데크에 M3 × 2"""
    w = WAGO
    gap = 3.0
    L = w["W"] + 4
    Dt = 2 * w["D"] + gap + 4
    base = Part.makeBox(L, Dt, 2.0, V(cx - L / 2, cy - Dt / 2, zb))
    wall = Part.makeBox(L, Dt, 4.0, V(cx - L / 2, cy - Dt / 2, zb + 2)).cut(
        Part.makeBox(w["W"] + 0.4, Dt - 4, 5, V(cx - (w["W"] + 0.4) / 2, cy - (Dt - 4) / 2, zb + 1.9)))
    wall = wall.cut(Part.makeBox(L + 2, Dt - 4, 5, V(cx - L / 2 - 1, cy - (Dt - 4) / 2, zb + 2.5)))   # 앞뒤 열어 전선 지나감
    shp = base.fuse(wall)
    for sx in (-1, 1):
        shp = shp.cut(Part.makeCylinder(1.7, 10, V(cx + sx * 6, cy, zb - 1)))          # M3 구멍 2 (두 와고 사이 틈)
    return shp.removeSplitter(), (cx - w["W"] / 2, cy - Dt / 2 + 2, zb + 2.0), (cx - w["W"] / 2, cy - Dt / 2 + 2 + w["D"] + gap, zb + 2.0)


WAGO_SCREWS = ((47.5, -78.0), (25.0, -57.0), (-37.5, -42.0), (-5.0, -42.0))


def apply_wago(doc):
    """(SJ-49, 서현 CAP-AI-32 요청) 와고 221-415 5개: GND 3개(이어서 11구) + +5 V 2개(이어서 8구).
    자리 [확실 — 모델]: 데크 −y 가장자리, UNO(x ≤ −56.4)와 ULN F(x ≥ 38, y ≥ −66)·입구 깔때기(r 30.5) 사이.
    2줄: 아래줄 y −88 ~ −69.4 (3개), 윗줄 y −66.4 ~ −47.8 (2개). 전선 구멍은 바깥(−y)·안(+y) 쪽, 레버는 위.
    받침 193h: 바닥 2 + 칸막이 높이 4, 데크에 M3 × 10 볼트 4개 + 아래 너트"""
    for o in [o for o in doc.Objects if o.Label.startswith(("193_terminal", "193b_", "193h_", "193w_"))]:
        doc.removeObject(o.Name)
    w = WAGO
    zb = 205.0
    xs = (-53.0, -20.1, 12.8)
    rows = (("GND", -88.0 + 1.0), ("+5V", -66.4 + 1.0))
    cells = [(xs[0], rows[0][1], "GND 1"), (xs[1], rows[0][1], "GND 2"), (xs[2], rows[0][1], "GND 3"),
             (xs[0], rows[1][1], "+5V 1"), (xs[1], rows[1][1], "+5V 2")]
    base = None
    bodies, levers = [], []
    for x0, y0, nm in cells:
        cell = Part.makeBox(w["W"] + 2.4, w["D"] + 1.0, 6.0, V(x0 - 1.2, y0 - 0.5, zb)).cut(
            Part.makeBox(w["W"] + 0.4, w["D"] + 3.0, 6.0, V(x0 - 0.2, y0 - 1.5, zb + 2.0)))
        base = cell if base is None else base.fuse(cell)
        bd, lv = wago_221(x0, y0, zb + 2.0, front=-1 if "GND" in nm else 1)
        bodies.append(bd)
        levers.append(lv)
    screws = []
    for x, y in WAGO_SCREWS:                                             # 칸 바깥 귀 4개 (와고 몸통·깔때기·UNO 피함)
        base = base.fuse(Part.makeBox(9.0, 9.0, 2.0, V(x - 4.5, y - 4.5, zb)))
        base = base.cut(Part.makeCylinder(1.7, 10, V(x, y, zb - 1)))
        screws.append(Part.makeCylinder(1.5, 10, V(x, y, zb + 2.0), V(0, 0, -1)).fuse(Part.makeCylinder(2.75, 3.0, V(x, y, zb + 2.0))))
    for o in doc.Objects:
        if o.Label.startswith("101_deck"):
            sh = o.Shape
            for x, y in WAGO_SCREWS:
                sh = sh.cut(Part.makeCylinder(1.7, 20, V(x, y, zb - 10)))
            o.Shape = sh.removeSplitter()
    out = []
    for nm, shp in (("193h_wago_holder (3D 프린트, 와고 5칸, 데크에 M3 × 10 네 개 + 너트)", base.removeSplitter()),
                    ("193w_wago_221-415 × 5 (아래줄 GND 3 / 윗줄 +5 V 2, 판매품 29.9 × 18.6 × 8.3)", Part.makeCompound(bodies)),
                    ("193w_wago_levers (주황 레버)", Part.makeCompound(levers)),
                    ("193s_bolt_M3x10_wago (4개, 데크 아래 너트)", Part.makeCompound(screws))):
        o = doc.addObject("Part::Feature", "SJW%d" % len(out))
        o.Label = nm
        o.Shape = shp
        out.append(o)
    doc.recompute()
    return out


# ---------------- (SJ-49) 서현 회로 요청: 허브 기판 2장·MOSFET 모듈·패널 퓨즈·J_I2C ----------------
# 만능기판(양면 FR-4, 2.54 피치) — 서보 허브 4 × 6 cm, 게이트 허브(풀업 10 kΩ × 9) 3 × 7 cm, 모서리 구멍 Ø2.0 (가장자리에서 2) [가능성 높음 — 흔한 판매 규격]
# MOSFET 모듈 SZH-AT021: 66.8 × 66.8 × 2.7 (디바이스마트 표기) [가능성 높음] — 구멍 위치 표기 없음 → 모서리 3.5 안쪽 Ø3.2로 그림 [추측 — 실물 재서 고칠 것, 미검증]
# 패널 퓨즈 홀더 5 × 20 (F-520류): 판 구멍 Ø12, 머리 Ø15.2, 전체 32.8 [가능성 높음 — 같은 형식 판매처 치수] → 비상 정지 판 194b 옆에
# J_I2C: JST XH 4핀(B4B-XH-A, KiCad STEP) — 게이트 허브 기판 위 (VS·GND·SDA·SCL, 서현 CAP-AI-35)
PERF = dict(t=1.6, hole=2.0, edge=2.0)
HUBS = {"SERVO_HUB": dict(L=60.0, W=40.0, x0=-30.0, y0=46.0, stand=8.0),
        "GATE_HUB": dict(L=70.0, W=30.0, x0=-127.0, y0=-14.0, stand=8.0)}
MOS = dict(L=66.8, W=66.8, t=2.7, x0=-125.0, y0=20.0, stand=6.0, off=3.5, hole=3.2)


def perfboard(x0, y0, zb, L, W, stand, hole_off=None, hole_d=None, t=None):
    t = t or PERF["t"]
    off = hole_off or (PERF["edge"] + PERF["hole"] / 2)
    d = hole_d or PERF["hole"]
    board = Part.makeBox(L, W, t, V(x0, y0, zb + stand))
    pts = [(x0 + off, y0 + off), (x0 + L - off, y0 + off), (x0 + off, y0 + W - off), (x0 + L - off, y0 + W - off)]
    st = []
    for x, y in pts:
        board = board.cut(Part.makeCylinder(d / 2, t + 2, V(x, y, zb + stand - 1)))
        st.append(Part.makeCylinder(d / 2 + 1.0, stand, V(x, y, zb)).cut(Part.makeCylinder(d / 2 - 0.3, stand + 1, V(x, y, zb - 0.5))))
    for i in range(int((L - 4) / 2.54)):                                  # 2.54 구멍 줄 표시 (가장자리 한 줄씩만)
        for yy in (y0 + 4.0, y0 + W - 4.0):
            board = board.cut(Part.makeCylinder(0.5, t + 2, V(x0 + 3.5 + i * 2.54, yy, zb + stand - 1)))
    return board.removeSplitter(), Part.makeCompound(st), pts


def apply_circuit_extras(doc):
    zb = 205.0
    out = []
    holes = []
    for nm, h in HUBS.items():
        b, st, pts = perfboard(h["x0"], h["y0"], zb, h["L"], h["W"], h["stand"])
        holes += pts
        lab = {"SERVO_HUB": "193v_servo_hub (만능기판 4 × 6 cm — 서보 5개 +5 V·GND·신호 나눔, 8 mm 기둥)",
               "GATE_HUB": "193g_gate_hub (만능기판 3 × 7 cm — 빛 게이트 9쌍 풀업 10 kΩ, J_I2C, 8 mm 기둥)"}[nm]
        out += [(lab, b, (0.15, 0.45, 0.20)), ("198h_hub_standoff_%s (M2 × 8 기둥 4, 구매)" % nm.lower(), st, (0.8, 0.7, 0.3))]
    m = MOS
    b, st, pts = perfboard(m["x0"], m["y0"], zb, m["L"], m["W"], m["stand"], m["off"], m["hole"], m["t"])
    holes += pts
    tb = load("tb4")
    tb = place_xy(tb, m["x0"] + m["L"] / 2, m["y0"] + 6.0, zb + m["stand"] + m["t"], rot=0)
    out += [("196m_mosfet_module_SZH-AT021 (66.8 × 66.8, 구멍 자리 미검증 — 실물 재기)", b.fuse(tb).removeSplitter() if False else Part.makeCompound([b, tb]), (0.10, 0.30, 0.60)),
            ("198m_mosfet_standoff (M3 × 6 기둥 4, 구매)", st, (0.8, 0.7, 0.3))]
    # J_I2C: 게이트 허브 위 오른쪽 끝
    g = HUBS["GATE_HUB"]
    xh = place_xy(load("xh4"), g["x0"] + g["L"] - 10.0, g["y0"] + g["W"] / 2, zb + g["stand"] + PERF["t"], rot=90)
    out.append(("193j_J_I2C_JST_XH_4P (VS·GND·SDA·SCL, KiCad STEP — 게이트 허브 위)", xh, (0.95, 0.95, 0.90)))
    for o in doc.Objects:
        if o.Label.startswith("101_deck"):
            sh = o.Shape
            for x, y in holes:
                sh = sh.cut(Part.makeCylinder(1.0, 20, V(x, y, zb - 10)))
            o.Shape = sh.removeSplitter()
    # 패널 퓨즈: 비상 정지 판 194b를 +y로 늘려 Ø12 구멍, 퓨즈 머리는 밖(−x)
    pl = [o for o in doc.Objects if o.Label.startswith("194b_")]
    if pl:
        pb = pl[0].Shape.BoundBox
        xf = pb.XMax                                                     # 레일 바깥 면 −180
        ext = Part.makeBox(pb.XLength, 22.0, 30.0, V(pb.XMin, pb.YMax - 0.01, 210.0))
        yc, zc = pb.YMax + 11.0, 225.0
        sh = pl[0].Shape.fuse(ext).cut(Part.makeCylinder(6.0, 10, V(pb.XMin - 1, yc, zc), V(1, 0, 0)))
        pl[0].Shape = sh.removeSplitter()
        pl[0].Label = "194b_estop_plate (3D 프린트 4 mm — 비상 정지 Ø22.5 + 퓨즈 Ø12, 레일에 M5 × 8 두 개)"
        cap = Part.makeCylinder(7.6, 9.0, V(pb.XMin, yc, zc), V(-1, 0, 0))
        body = Part.makeCylinder(6.0, 32.8 - 9.0, V(pb.XMin, yc, zc), V(1, 0, 0))
        nut = Part.makeCylinder(8.0, 3.0, V(xf, yc, zc), V(1, 0, 0)).cut(Part.makeCylinder(6.0, 5, V(xf - 1, yc, zc), V(1, 0, 0)))
        out.append(("194f_panel_fuse_holder_5x20 (F-520류, 판 구멍 Ø12, T3A 퓨즈 — 서현 구매확정표 E3)", Part.makeCompound([cap, body, nut]), (0.15, 0.15, 0.15)))
    objs = []
    for nm, shp, col in out:
        for old in [x for x in doc.Objects if x.Label.split(" ")[0] == nm.split(" ")[0]]:
            doc.removeObject(old.Name)
        o = doc.addObject("Part::Feature", "SJX%02d" % len(objs))
        o.Label, o.Shape = nm, shp
        if App.GuiUp and col:
            o.ViewObject.ShapeColor = col
        objs.append(o)
    doc.recompute()
    return objs


# ---------------- (11/06 20:30) 아두이노 UNO R3 — 자리 상자 → 실제 모양 ----------------
# 공식 STEP은 받을 수 없음 (docs.arduino.cc 404, content.arduino.cc 403, SnapEDA 로그인) → 승준이 SnapEDA에서 받으면 바꿔 끼움.
# 기판 68.58 × 53.34 × 1.6, 구멍 Ø3.2 4개 (13.97, 2.54) (15.24, 50.8) (66.04, 7.62) (66.04, 35.56) [확실 — UNO 공식 규격 도면 값]
# 헤더 소켓: 위 1×10 (x 17.53부터) · 1×8 (x 44.45부터), 아래 1×8 전원 (x 26.67부터) · 1×6 아날로그 (x 49.53부터) [가능성 높음 — 실드 규격]
# USB-B: 왼쪽 가장자리에서 6.35 튀어나옴, 입구 12.0 × 10.9, 깊이 16.3 [가능성 높음 — USB-B 외형], 전원 잭: KiCad PJ-063AH
UNO = dict(L=68.58, W=53.34, t=1.6, hole=3.2,
           holes=((13.97, 2.54), (15.24, 50.8), (66.04, 7.62), (66.04, 35.56)),
           heads=(("sock10", 17.53, 50.8, 10), ("sock8", 44.45, 50.8, 8), ("sock8", 26.67, 2.54, 8), ("sock6", 49.53, 2.54, 6)))
UNO_STAND_LOW, UNO_STAND_GAP = 5.0, 15.0     # 사이 15: 12면 위 UNO 핀 끝이 아래 UNO 부품에 닿음 (공식 STEP 겹침 0.36 mm³)
UNO_ORIGIN = (-125.0, -75.0, 205.0)          # D5f 191 상자: x −125~−56.4, y −75~−21.6, 데크 윗면 205     # 데크 → UNO 1, UNO 1 → UNO 2 (M3 황동 기둥)


def uno_board(x0, y0, zb):
    """(x0, y0) = 기판 왼쪽 아래 모서리 (USB 쪽이 x0), zb = 기판 아래 면"""
    u = UNO
    pcb = Part.makeBox(u["L"], u["W"], u["t"], V(x0, y0, zb))
    for hx, hy in u["holes"]:
        pcb = pcb.cut(Part.makeCylinder(u["hole"] / 2, 5, V(x0 + hx, y0 + hy, zb - 1)))
    zt = zb + u["t"]
    parts = [pcb]
    for key, hx, hy, n in u["heads"]:
        parts.append(place_xy(load(key), x0 + hx + 2.54 * (n - 1) / 2, y0 + hy, zt, 90))
    parts.append(place_xy(load("dip28"), x0 + 49.0, y0 + 17.0, zt, 90))
    usb = Part.makeBox(16.3, 12.0, 10.9, V(x0 - 6.35, y0 + 38.1 - 6.0, zt))
    usb = usb.cut(Part.makeBox(9, 8.0, 7.3, V(x0 - 6.4, y0 + 38.1 - 4.0, zt + 1.8)))
    parts.append(usb)
    jk = load("jack")
    b = jk.BoundBox
    if b.YLength > b.XLength:
        jk.rotate(V(0, 0, 0), V(0, 0, 1), 90)
    b = jk.BoundBox
    jk.translate(V(x0 - 1.9 - b.XMin, y0 + 7.6 - b.Center.y, zt))
    parts.append(jk)
    return Part.makeCompound(parts)


def apply_uno(doc):
    """191·192 상자 → UNO 실제 모양 2장 + M3 기둥 (데크 → UNO 1: 5, UNO 1 → UNO 2: 12)"""
    b1 = [o for o in doc.Objects if o.Label.startswith("191_arduino_uno")]
    b2 = [o for o in doc.Objects if o.Label.startswith("192_arduino_uno2")]
    if not b1:
        return []
    x0, y0, deck = UNO_ORIGIN       # D5f 자리 상자 모서리 = 기판 원점 (다시 돌려도 USB 튀어나온 만큼 밀리지 않게 고정)
    z1 = deck + UNO_STAND_LOW
    z2 = z1 + UNO["t"] + UNO_STAND_GAP
    path = find_uno_step()
    raw = None
    if path:
        raw = Part.Shape()
        raw.read(path)
    def board(z):
        if raw is not None:
            shp, hit, _ = uno_official(raw, x0, y0, z)
            if hit == 4:
                return shp, True
        return uno_board(x0, y0, z), False
    shp1, off1 = board(z1)
    b1[0].Shape = shp1
    b1[0].Label = "191_arduino_uno (" + ("Arduino 공식 STEP A000066, 구멍 4개 맞춤" if off1 else "공식 기판 규격 + KiCad STEP 부품") + ")"
    if b2:
        b2[0].Shape = board(z2)[0]
        b2[0].Label = "192_arduino_uno2 (실제 모양, UNO 1 위 M3 × 12 기둥)"
    st = []
    for hx, hy in UNO["holes"]:
        if (hx, hy) == (15.24, 50.8):      # 헤더 소켓과 1.0 mm → 기둥 못 세움 (실물도 같음) → 3점 받침 [확실 — 모델 겹침]
            continue
        st.append(Part.makeCylinder(2.75, UNO_STAND_LOW, V(x0 + hx, y0 + hy, deck)))
        r_up = 2.0 if (hx, hy) == (13.97, 2.54) else 2.75     # 왼쪽 아래 구멍 위: 옆 부품과 닿음 → 외경 4 이하 스페이서 [확실 — 공식 STEP 겹침]
        st.append(Part.makeCylinder(r_up, UNO_STAND_GAP, V(x0 + hx, y0 + hy, z1 + UNO["t"])))
    o = [x for x in doc.Objects if x.Label.startswith("198u_")]
    o = o[0] if o else doc.addObject("Part::Feature", "SJ_uno_st")
    o.Label = "198u_uno_standoff (M3 기둥: 아래 5 × 3, 사이 15 × 3 — 왼쪽 아래 구멍만 외경 4 이하)"
    o.Shape = Part.makeCompound(st)
    doc.recompute()
    return [b1[0]] + b2 + [o]


# ---------------- (11/06 20:35) 빛 게이트·비상 정지 — 자리 상자 → 실제 모양 ----------------
# 문 게이트 6쌍 (G2·G2b·G3·G3b·G5·G5b): 하우징 위·아래 벽 Ø4.2 구멍에 3 mm 적외선 LED / 3 mm 수광 소자 낱개를 꽂음.
#   [확실 — 모델] 입구·격리 문 하우징 사이 틈 5 mm → Adafruit 2167 몸통(20 × 10 × 8)은 안 들어감.
#   모양: KiCad LED_D3.0mm STEP (렌즈 지름 3, 테 3.8 < 구멍 4.2) — 렌즈 끝이 빔 쪽 벽 안 면에 오게.
# 통로 게이트 3쌍 (G1·G4·G6): Adafruit 2167 송신기·수신기 각 20 × 10 × 8 [가능성 높음 — 판매처 표기], 렌즈 Ø3 돌기,
#   선 230 mm. 빔이 지나는 통로 벽·받침에 Ø3.2 구멍.
# 비상 정지: 22 mm 버섯형 (XB7NS8442 같은 것) — 머리 Ø40, 전체 깊이 72 [가능성 높음 — 판매처 표기], 데크 구멍 Ø22.5.
#   판 앞 31 (머리 18 + 목 13) / 판 뒤 41 (몸통 + 접점 블록)으로 나눔 → 판 앞·뒤 나눔은 실물로 확인.
ADA2167 = dict(L=20.0, W=10.0, H=8.0, lens_r=1.5, lens_h=2.0)
LEAD_LOG = []
LEAD = dict(straight=0.0, bend=6.0)   # 문 틈 5 mm에 위·아래 소자 다리가 같은 x에서 마주봄 → 몸통 뒤 1.5에서 바로 꺾음 (2 × (1.5 + 0.5) = 4 < 5), 납땜은 꺾인 6 mm 위에서


def ir_pair_door(doc):
    """196_gate_G2~G5b_led (원기둥 2개) → KiCad 3 mm LED 모양 2개 (위: 렌즈 아래로, 아래: 렌즈 위로)"""
    led = load("led3")
    out = []
    for o in [x for x in doc.Objects if x.Label.startswith("196_gate_G") and "_led" in x.Label]:
        sol = sorted(o.Shape.Solids, key=lambda s: s.BoundBox.ZMin)
        lo, hi = sol[0].BoundBox, sol[-1].BoundBox
        z_beam_lo, z_beam_hi = lo.ZMax, hi.ZMin          # 빔 쪽 끝 (벽 안 면)
        up = led.copy()
        b = up.BoundBox
        up.translate(V(lo.Center.x - b.Center.x, lo.Center.y - b.Center.y, z_beam_lo - b.ZMax))     # 아래 소자: 렌즈가 위
        dn = led.copy()
        dn.rotate(V(0, 0, 0), V(1, 0, 0), 180)
        b = dn.BoundBox
        dn.translate(V(hi.Center.x - b.Center.x, hi.Center.y - b.Center.y, z_beam_hi - b.ZMin))     # 위 소자: 렌즈가 아래
        # 다리: 몸통 뒤로 1.5 mm만 남김 (실물은 구부려 옆으로 뺌 — 문 하우징 사이 틈 5 mm에서 서로 닿지 않게) [확실 — 모델 겹침]
        keep = 7.0
        up = up.common(Part.makeBox(20, 20, keep, V(lo.Center.x - 10, lo.Center.y - 10, z_beam_lo - keep)))
        dn = dn.common(Part.makeBox(20, 20, keep, V(hi.Center.x - 10, hi.Center.y - 10, z_beam_hi)))
        # (SJ-49, 서현 CAP-AI-34) 납땜 여유: 다리를 90° 꺾어 옆으로 6 mm (G2 쪽 +y, G3 쪽 −y로 서로 반대) — 꺾인 부분에 선을 납땜. 다리 간격 2.54 (x)
        side = {"G2": 1, "G2b": 1, "G3": -1, "G3b": -1, "G5": 1, "G5b": 1}.get(o.Label.split("_")[2], 1)
        legs = []
        hous = [h for h in doc.Objects if h.Label.startswith(("112_entry_gate_housing", "170_isolation_gate_housing", "176_release_gate_housing"))]
        for c, z_end, sgn in ((lo.Center, z_beam_lo - keep, -1), (hi.Center, z_beam_hi + keep, 1)):
            # 다리가 하우징 살 밖으로 나오는 곳까지 곧게 (구멍 안에서 꺾을 수 없음) → 나온 뒤 0.2 mm에서 꺾음
            st = 0.0
            def blocked(st_):
                zz = z_end + sgn * (st_ + 0.25)
                return any(h.Shape.isInside(V(c.x + dx_, c.y + side * k, zz), 0.01, True)
                           for h in hous for dx_ in (-1.27, 1.27) for k in (0.5, 2.0, 3.5, 5.0, 5.9))
            while st < 10.0 and blocked(st):
                st += 0.1
            st = round(st + 0.2, 1) if st > 0 else 0.0
            LEAD_LOG.append((o.Label.split(" ")[0], sgn, st))
            for dx in (-1.27, 1.27):
                x = c.x + dx
                zs = z_end if sgn > 0 else z_end - st
                if st > 0:
                    legs.append(Part.makeBox(0.5, 0.5, st, V(x - 0.25, c.y - 0.25, zs)))
                zb_ = z_end + sgn * st - (0.5 if sgn < 0 else 0.0)          # 꺾인 다리 두께 0.5는 몸통 반대쪽으로
                y0 = c.y - 0.25 if side > 0 else c.y + 0.25 - LEAD["bend"]
                legs.append(Part.makeBox(0.5, LEAD["bend"], 0.5, V(x - 0.25, y0, zb_)))
        o.Shape = Part.makeCompound([up, dn] + legs)
        o.Label = o.Label.split(" ")[0].replace("_led", "_ir_pair") + " (3 mm 적외선 LED + 3 mm 수광, KiCad STEP — 다리를 몸통 뒤 1.5에서 옆으로 6 mm 꺾음(납땜 자리), 긴 다리 A·짧은 다리 K, 수광 렌즈가 LED를 마주봄)"
        out.append(o.Label)
    return out


def ada2167(face_center, inward, long_axis):
    """face_center: 렌즈 쪽 면 가운데, inward: 빔 쪽 단위 벡터, long_axis: 20 방향 단위 벡터"""
    a = ADA2167
    n = V(*inward)
    l = V(*long_axis)
    w = n.cross(l)
    m = App.Matrix()
    m.A11, m.A21, m.A31 = l.x, l.y, l.z
    m.A12, m.A22, m.A32 = w.x, w.y, w.z
    m.A13, m.A23, m.A33 = -n.x, -n.y, -n.z
    body = Part.makeBox(a["L"], a["W"], a["H"], V(-a["L"] / 2, -a["W"] / 2, 0))
    lens = Part.makeCylinder(a["lens_r"], a["lens_h"], V(0, 0, -a["lens_h"]))
    s = body.fuse(lens).transformGeometry(m)          # 선(230 mm)은 휘는 전선이라 그리지 않음
    s.translate(V(*face_center))
    return s


def ir_pair_2167(doc):
    """196_gate_G4·G6_tx_rx 상자, 114_entry_sensor_tx·rx 상자 → 2167. 빔이 지나는 통로·받침에 Ø3.2 구멍"""
    out = []
    jobs = []
    for o in doc.Objects:
        if o.Label.startswith(("196_gate_G4_tx_rx", "196_gate_G6_tx_rx", "114_entry_sensor_tx", "114_entry_sensor_rx")):
            jobs.append(o)
    beams = {}
    for o in jobs:
        sols = o.Shape.Solids
        cs = [s.BoundBox.Center for s in sols]
        if len(sols) == 2:
            c0, c1 = cs
        else:
            pair = [x for x in jobs if x is not o and x.Label[:18] == o.Label[:18]] or [x for x in jobs if x is not o and "114_entry_sensor" in x.Label and "114" in o.Label]
            c0, c1 = cs[0], pair[0].Shape.BoundBox.Center
        ax = max(range(3), key=lambda i: abs([c1.x - c0.x, c1.y - c0.y, c1.z - c0.z][i]))
        mid = (c0 + c1) * 0.5
        parts = []
        for s in sols:
            b = s.BoundBox
            c = b.Center
            sign = 1 if [c.x, c.y, c.z][ax] < [mid.x, mid.y, mid.z][ax] else -1
            inward = [0, 0, 0]
            inward[ax] = sign
            fc = [c.x, c.y, c.z]
            fc[ax] = ([b.XMax, b.YMax, b.ZMax][ax] if sign > 0 else [b.XMin, b.YMin, b.ZMin][ax])
            long_axis = [0, 0, 1] if ax != 2 else [1, 0, 0]
            parts.append(ada2167(fc, inward, long_axis))
        o.Shape = Part.makeCompound(parts)
        o.Label = o.Label.split(" ")[0] + " (Adafruit 2167 20 × 10 × 8)"
        d = V(0, 0, 0)
        setattr(d, "xyz"[ax], 1)
        beams[o.Label] = (c0, c1, d)
        out.append(o.Label)
    holes = []
    for c0, c1, d in beams.values():
        L = abs((c1 - c0).dot(d)) + 4
        start = (c0 if (c1 - c0).dot(d) > 0 else c1) - d * 2
        holes.append(Part.makeCylinder(1.6, L, start, d))
    hole = Part.makeCompound(holes)
    for o in doc.Objects:
        if hasattr(o, "Shape") and o.Label.startswith(("110_", "172_", "174_", "199b_", "199c_")) and o.Shape.BoundBox.intersect(hole.BoundBox):
            if o.Shape.common(hole).Volume > 0.01:
                o.Shape = o.Shape.cut(hole).removeSplitter()
    return out


def estop(doc):
    """194 비상 정지: 데크 아래는 상용 트랩 차양막(지름 260, z 145~180)이 전부 덮어 데크 구멍 방식 불가 [확실 — 모델]
    → 데크 높이 2020 레일(x −170 쪽, 바깥 면 x −180) 바깥에 3D 프린트 판 194b (4 mm, Ø22.5 구멍, M5 × 8 + T너트 2)를 달고
      버섯 머리는 프레임 밖(−x)을 보게: 밖에서 누르기 쉬움. 판 뒤 몸통은 레일 위 (z 205~245), UNO와 7 mm 띄움."""
    old = [o for o in doc.Objects if o.Label.startswith("194_estop")]
    if not old:
        return None
    import D5e_module_kinematic as K
    c, s = K.FR["c"], 20.0
    xf = -c - s / 2                     # 레일 바깥 면 −180
    zr = K.FR["deck_z"]                 # 레일 z 180~200
    yc, zc = 0.0, zr + s + 25.0         # 버튼 중심 z 225
    t = 4.0
    plate = Part.makeBox(t, 50, 70, V(xf - t, yc - 25, zr + 2))
    plate = plate.cut(Part.makeCylinder(11.25, 10, V(xf - t - 1, yc, zc), V(1, 0, 0)))
    for dy in (-15, 15):
        plate = plate.cut(Part.makeCylinder(2.75, 10, V(xf - t - 1, yc + dy, zr + s / 2), V(1, 0, 0)))
    head = Part.makeCylinder(14.5, 13, V(xf - t, yc, zc), V(-1, 0, 0)).fuse(
        Part.makeCylinder(20, 18, V(xf - t - 13, yc, zc), V(-1, 0, 0)))
    body = Part.makeCylinder(11.0, 15, V(xf, yc, zc), V(1, 0, 0))
    block = Part.makeBox(26, 40, 30, V(xf + 15, yc - 20, zc - 15))
    old[0].Shape = Part.makeCompound([head, body, block])
    old[0].Label = "194_estop (22 mm 버섯형 NC, 머리 Ø40, 깊이 72 — 프레임 바깥을 봄)"
    pl = [o for o in doc.Objects if o.Label.startswith("194b_")]
    pl = pl[0] if pl else doc.addObject("Part::Feature", "SJ_estop_plate")
    pl.Label = "194b_estop_plate (3D 프린트 4 mm, 레일에 M5 × 8 + T너트 2)"
    pl.Shape = plate.removeSplitter()
    # 앞 버전에서 데크에 뚫었던 Ø22.5 구멍 메움
    for o in doc.Objects:
        if o.Label.startswith("101_deck"):
            b = o.Shape.BoundBox
            fill = Part.makeCylinder(11.25, b.ZLength, V(-100, 45, b.ZMin))
            if o.Shape.common(fill).Volume < fill.Volume * 0.99:
                o.Shape = o.Shape.fuse(fill).removeSplitter()
    return old[0]


def apply_gates_estop(doc):
    out = ir_pair_door(doc) + ir_pair_2167(doc)
    e = estop(doc)
    if e:
        out.append(e.Label)
    doc.recompute()
    return out


# ---------------- (11/06 20:45) 아두이노 UNO 공식 STEP (승준이 SnapEDA에서 받음) ----------------
# 파일: A000066.STEP ('ARDUINO UNO REV3', SolidWorks 2017) — 레포에는 안 올림 (SnapEDA 약관·16 MB). 승준 PC 다운로드 폴더에서 읽음.
# 맞춤: 가장 얇은 방향을 z로 눕힌 뒤, z축으로 0/90/180/270° 돌려 보며 Ø3.2 구멍 4개가 UNO 공식 구멍 자리와 맞는 방향을 고름.
UNO_STEP_GLOB = ("~/Downloads/A000066*.st*p", "~/Downloads/A000066*.ST*P")


def find_uno_step():
    import glob
    for g in UNO_STEP_GLOB:
        f = sorted(glob.glob(os.path.expanduser(g)), key=os.path.getmtime)
        if f:
            return f[-1]
    return None


def _holes_xy(s, rmin=1.4, rmax=1.75):
    pts = []
    for f in s.Faces:
        if f.Surface.TypeId == "Part::GeomCylinder" and rmin <= f.Surface.Radius <= rmax and abs(f.Surface.Axis.z) > 0.99:
            c = f.Surface.Center
            if all(abs(c.x - p[0]) > 0.3 or abs(c.y - p[1]) > 0.3 for p in pts):
                pts.append((c.x, c.y))
    return pts


def uno_official(raw, x0, y0, zb):
    """raw: 읽은 STEP. 기판 왼쪽 아래 모서리 (x0, y0) = UNO 규격 원점, 기판 아래 면 zb. 반환 (shape, 맞춘 구멍 수, (뒤집기, 회전))
    11/06 결과: A000066.STEP 은 얇은 y를 z로 눕힌 뒤 x축 180° 뒤집기 + 회전 0°에서 4/4 맞음"""
    import math
    s = raw.copy()
    b = s.BoundBox
    dims = [b.XLength, b.YLength, b.ZLength]
    i = dims.index(min(dims))
    if i == 1:
        s.rotate(b.Center, V(1, 0, 0), -90)
    elif i == 0:
        s.rotate(b.Center, V(0, 1, 0), 90)
    hs = _holes_xy(s)
    want = UNO["holes"]
    best = None
    for flip in (False, True):
        for rot in (0, 90, 180, 270):
            a = math.radians(rot)
            P = [((x * math.cos(a) - (-y if flip else y) * math.sin(a)), (x * math.sin(a) + (-y if flip else y) * math.cos(a))) for x, y in hs]
            for px, py in P:
                ox, oy = px - want[0][0], py - want[0][1]
                hit = sum(1 for wx, wy in want if any(abs(qx - ox - wx) < 0.4 and abs(qy - oy - wy) < 0.4 for qx, qy in P))
                if best is None or hit > best[0]:
                    best = (hit, flip, rot, ox, oy)
    hit, flip, rot, ox, oy = best
    if flip:
        s.rotate(V(0, 0, 0), V(1, 0, 0), 180)
    if rot:
        s.rotate(V(0, 0, 0), V(0, 0, 1), rot)
    flats = sorted([f for f in s.Faces if f.Surface.TypeId == "Part::GeomPlane" and abs(f.normalAt(0, 0).z) > 0.99 and f.Area > 2500],
                   key=lambda f: f.CenterOfMass.z)
    z_bot = flats[0].CenterOfMass.z if flats else s.BoundBox.ZMin
    s.translate(V(x0 - ox, y0 - oy, zb - z_bot))
    return s, hit, (flip, rot)
