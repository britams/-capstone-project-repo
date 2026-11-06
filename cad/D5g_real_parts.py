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
    "hdr4": KICAD + "Connector_PinHeader_2.54mm.3dshapes/PinHeader_1x04_P2.54mm_Vertical.step",
    "hdr2": KICAD + "Connector_PinHeader_2.54mm.3dshapes/PinHeader_1x02_P2.54mm_Vertical.step",
    "led3": KICAD + "LED_THT.3dshapes/LED_D3.0mm.step",
    "tb4": KICAD + "TerminalBlock_Phoenix.3dshapes/TerminalBlock_Phoenix_PT-1,5-4-5.0-H_1x04_P5.00mm_Horizontal.step",
    "fuse": KICAD + "Fuse.3dshapes/Fuseholder_Cylinder-5x20mm_Bulgin_FX0457_Horizontal_Closed.step",
    "pi5zip": "https://datasheets.raspberrypi.com/rpi5/RaspberryPi5-step.zip",
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


def apply_wago(doc):
    """193 단자대·퓨즈 기판(193, 193b)을 지우고 와고 2개 + 받침으로"""
    old = [o for o in doc.Objects if o.Label.startswith(("193_terminal", "193b_"))]
    cx, cy, zb = -30.0, -65.0, 205.0
    if old:
        b = old[0].Shape.BoundBox
        cx, cy = b.Center.x, b.Center.y
    for o in old:
        doc.removeObject(o.Name)
    holder, p1, p2 = wago_holder(cx, cy, zb)
    b1, l1 = wago_221(*p1, front=-1)
    b2, l2 = wago_221(*p2, front=1)
    out = []
    for nm, shp in (("193h_wago_holder (3D 프린트, 데크에 M3 × 2)", holder),
                    ("193w_wago_221-415 × 2 (+5 V 줄 / GND 줄, 판매품 29.9 × 18.6 × 8.3)", Part.makeCompound([b1, b2])),
                    ("193w_wago_levers (주황 레버)", Part.makeCompound([l1, l2]))):
        o = doc.addObject("Part::Feature", "SJW%d" % len(out))
        o.Label = nm
        o.Shape = shp
        out.append(o)
    doc.recompute()
    return out
