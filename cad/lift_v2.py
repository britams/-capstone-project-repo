# -*- coding: utf-8 -*-
"""리프트 v2 — 기성품 + 나사만 (서현 11/12 14:34 "3D 프린트 절대 쓰지 마, 절단·재단도 못 해, 나사로 조이는 것만",
14:41 "마킹실 낮춰", 14:45 MiniSlide로, 15:10 "시제품 중 제일 싼 걸로"). 다른 부분과 아직 맞추지 않음 — 리프트부만.

좌표 (이 파일 혼자): 마킹실(PVC 크로스) 가운데 = 원점, z 위.
  마킹실  US Plastic 34566 (DuraClear 3/4" 투명 PVC 5방향 크로스, 소켓 깊이 1") — 구멍 ±x(입구·격리), ±z(위 망·아래 바닥 길), +y
          안지름 20.9 (3/4" 관 안) · 소켓 26.9 · 팔 끝까지 38 [추측 — 판매처가 소켓 깊이만 줌, 사서 잼]
  리프트  Haydon Kerk MiniSlide MSA02S-C0039-805 (50 mm 행정, 리드 1 mm, 20 mm 캔스택 7.5°, 5 V 350 mA) — 세워서, 모터 아래
          캐리지 M3 인서트 4개 16.0 × 12.7 [확실 — 판매처 STEP]. STEP은 PC에만 (받은도면 step파일)
  연결    메카노 앵글 거더 1½" (구멍 3, 간격 12.7, 구멍 Ø4.1, 날개 12.7) — 캐리지 위 구멍 줄 2개에 M3 × 6
          두께 1.0, 구멍 줄은 날개 가운데 [추측 — 메카노 표준 간격 ½"만 확실]
  기둥    M3 육각 스페이서 암-암 40 + 수-암 20 (6각 5.5) — 거더 아래에서 M3 × 6
  바닥    M6 DIN 9021 와셔 (바깥 18, 안 6.4, 두께 1.6) + M3 DIN 9021 와셔 (바깥 9, 0.8) + M3 낮은 머리 나사 (머리 1.65)
  행정    말벌이 옆 구멍 바닥 높이로 걸어 들어옴 → 바닥 윗면 z −10.45. 눌린 말벌 5 → 바닥 윗면 5.45 → 15.9 mm
"""
import os
import glob
import math
import FreeCAD as App
import Part

V = App.Vector
STEP_DIR = r"C:\Users\Seohyun_Lee\Desktop\capstone design\받은도면 step파일"
X = dict(bore=20.9, sock=26.9, sock_d=25.4, arm=38.0, od=33.4)
H = dict(rest=-10.45, press=5.45)
STROKE = H["press"] - H["rest"]
W6 = dict(od=18.0, id=6.4, t=1.6)
W3 = dict(od=9.0, id=3.2, t=0.8)
SO = (40.0, 20.0)                      # 스페이서 길이
G = dict(L=38.1, w=12.7, t=1.0, hole=4.1, p=12.7, hole_from_out=6.6)
YC = -G["hole_from_out"]                # 캐리지 앞면 y (거더 구멍이 축 위에 오게)
ZR = -41.0                              # 레일 국부 x → 세계 z 더하는 값 (레일 위 블록이 아래 팔 끝 −38 아래)
S0 = 27.7                               # 쉴 때 캐리지 위치 (레일 국부 0~53.8 중)


def cyl(r, h, p, d=V(0, 0, 1)):
    return Part.makeCylinder(r, h, p, d)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cross():
    """대표 모양: 팔 6개 중 5개 (−y 없음)"""
    r = X["od"] / 2
    body = None
    for d in (V(1, 0, 0), V(-1, 0, 0), V(0, 0, 1), V(0, 0, -1), V(0, 1, 0)):
        a = cyl(r, X["arm"], V(0, 0, 0), d)
        body = a if body is None else body.fuse(a)
    body = body.fuse(Part.makeSphere(r))
    for d in (V(1, 0, 0), V(-1, 0, 0), V(0, 0, 1), V(0, 0, -1), V(0, 1, 0)):
        body = body.cut(cyl(X["bore"] / 2, X["arm"] + 1, V(0, 0, 0), d))
        body = body.cut(cyl(X["sock"] / 2, X["sock_d"] + 1, d * (X["arm"] - X["sock_d"]), d))
    return body.removeSplitter()


def floor_stack(dz):
    """움직이는 바닥 묶음 (dz = 쉬는 자리에서 올라간 양). 반환 {이름: 모양}"""
    top = H["rest"] + dz
    w6 = cyl(W6["od"] / 2, W6["t"], V(0, 0, top - W6["t"])).cut(cyl(W6["id"] / 2, 5, V(0, 0, top - 3)))
    w3 = cyl(W3["od"] / 2, W3["t"], V(0, 0, top)).cut(cyl(W3["id"] / 2, 3, V(0, 0, top - 1)))
    head_z = top + W3["t"]
    scr_top = cyl(2.75, 1.65, V(0, 0, head_z)).fuse(cyl(1.5, 6.0, V(0, 0, head_z - 6.0)))
    z_so1 = top - W6["t"]                                   # 스페이서 윗면
    so = None
    z = z_so1
    for L in SO:
        R = 5.5 / 3 ** 0.5
        hexp = Part.makePolygon([V(R * math.cos(math.radians(60 * k + 30)), R * math.sin(math.radians(60 * k + 30)), z - L) for k in range(7)])
        hx = Part.Face(hexp).extrude(V(0, 0, L)).cut(cyl(1.5, L + 2, V(0, 0, z - L - 1)))
        so = hx if so is None else so.fuse(hx)
        z -= L
    z_g = z                                                  # 거더 누운 날개 윗면
    t = G["t"]
    girder = box(-6.35, -6.35 + G["L"], YC, YC + G["w"], z_g - t, z_g)                                     # 누운 날개
    girder = girder.fuse(box(-6.35, -6.35 + G["L"], YC, YC + t, z_g - G["w"], z_g))                        # 선 날개 (캐리지에 붙음)
    for i in range(3):
        xh = i * G["p"]
        girder = girder.cut(cyl(G["hole"] / 2, 3, V(xh, 0, z_g - 2)))
        girder = girder.cut(cyl(G["hole"] / 2, 3, V(xh, YC - 1, z_g - G["w"] / 2), V(0, 1, 0)))
    scr_bot = cyl(2.75, 1.65, V(0, 0, z_g - t - 1.65)).fuse(cyl(1.5, 6.0, V(0, 0, z_g - t)))
    car_scr = []
    for xh in (0.0, G["p"]):
        c = V(xh, YC + t, z_g - G["w"] / 2)
        car_scr.append(cyl(2.75, 1.65, c, V(0, 1, 0)).fuse(cyl(1.5, 6.0, c - V(0, 6.0, 0), V(0, 1, 0))))
    return {"floor_w6": w6, "floor_w3": w3, "floor_screw": scr_top, "standoffs": so, "girder": girder,
            "girder_screw": scr_bot, "carriage_screws": Part.makeCompound(car_scr)}, z_g


def slide(dz, z_row):
    """MiniSlide: STEP이 있으면 그것 (PC), 없으면 대표 상자. 캐리지 위 구멍 줄이 z_row에 오게 캐리지만 옮김"""
    f = glob.glob(os.path.join(STEP_DIR, "Haydon_MSA02_50mm_*.stp"))
    m = App.Matrix(0, 0, -1, 6.35, 0, 1, 0, YC - 6.35, 1, 0, 0, ZR, 0, 0, 0, 1)   # 국부 (x,y,z) → 세계 (−z+6.35, y+YC−6.35, x+ZR)
    if f:
        s = Part.read(f[0])
        sol = s.Solids
        car = sol[6].copy()
        car.translate(V(z_row - (-11.33 + ZR), 0, 0))             # 국부 x로: 위 구멍 줄(−11.33) → z_row
        fixed = Part.makeCompound([x for i, x in enumerate(sol) if i != 6])
        return fixed.transformed(m), car.transformed(m), "STEP"
    rail = box(-116.12, 1.5, -11.0, 5.33, -18.0, 18.0).cut(box(-85.69, -9.0, -12, 7, -11, 11))
    car = box(-31.9, -6.5, -6.35, 6.35, -17.78, 17.78)
    car.translate(V(z_row - (-11.33 + ZR), 0, 0))
    return rail.transformed(m), car.transformed(m), "대표"


def make(doc=None, dz=0.0):
    doc = doc or App.newDocument("Lift_v2")
    parts, z_g = floor_stack(dz)
    z_row = z_g - G["w"] / 2
    rail, car, src = slide(dz, z_row)
    gray, dark = (0.75, 0.75, 0.77), (0.35, 0.35, 0.37)
    shapes = [("C_cross", "300_chamber_cross (US Plastic 34566 DuraClear 3/4\" 투명 PVC 5방향 크로스, 구매) [치수 대표]", cross(), (0.75, 0.9, 1.0), 70),
              ("L_rail", "301_minislide (Haydon Kerk MSA02S-C0039-805 — 레일·모터·블록, 구매) [%s]" % src, rail, gray, 0),
              ("L_car", "301c_minislide_carriage (MiniSlide 캐리지 — 움직임) [%s]" % src, car, gray, 0),
              ("L_gird", "302_meccano_angle_girder (메카노 앵글 거더 1½\" 구멍 3, 구매)", parts["girder"], gray, 0),
              ("L_gs", "302s_screws (M3 × 6 냄비머리 — 거더 → 캐리지 2, 구매)", parts["carriage_screws"], dark, 0),
              ("L_so", "303_standoffs (M3 육각 스페이서 암-암 40 + 수-암 20, 구매)", parts["standoffs"], gray, 0),
              ("L_bs", "303s_screw (M3 × 6 — 거더 아래에서 스페이서로, 구매)", parts["girder_screw"], dark, 0),
              ("L_w6", "304_floor_washer_M6_DIN9021 (바닥 — 바깥 18 × 1.6, 구매)", parts["floor_w6"], gray, 0),
              ("L_w3", "304a_washer_M3_DIN9021 (바깥 9 × 0.8, 구매)", parts["floor_w3"], gray, 0),
              ("L_ts", "304s_screw (M3 낮은 머리 × 6 — 바닥 → 스페이서, 구매)", parts["floor_screw"], dark, 0)]
    for name, lab, shp, col, tr in shapes:
        o = doc.addObject("Part::Feature", name)
        o.Shape, o.Label = shp, lab
        if App.GuiUp:
            o.ViewObject.ShapeColor = col
            o.ViewObject.Transparency = tr
    doc.recompute()
    return doc


MOVING = ("301c", "302", "303", "304")
ALLOW = (("301c", "301_"), ("302s", "301c"),     # 301c↔301_: 판매처 STEP 자체가 캐리지 부싱과 안내 봉을 1.97 mm³씩 겹쳐 그림 (11/12 확인)
          ("302s", "302_"), ("303s", "302_"), ("303s", "303_"), ("304s", "303_"), ("304s", "304"), ("304_", "304a"))


def check(doc, steps=(0.0, 4.0, 8.0, 12.0, STROKE)):
    """쉬는 자리 → 누른 자리까지 움직이는 묶음 ↔ 고정 (마킹실·레일) 겹침, 그리고 움직이는 것끼리 (나사 물림 허용)"""
    obs = [o for o in doc.Objects if hasattr(o, "Shape")]
    mv = [o for o in obs if o.Label.startswith(MOVING)]
    fx = [o for o in obs if o not in mv]
    ok = lambda a, b: any(a.startswith(p) and b.startswith(q) or b.startswith(p) and a.startswith(q) for p, q in ALLOW)
    hits = []
    for dz in steps:
        for a in mv:
            s = a.Shape.copy()
            s.translate(V(0, 0, dz))
            for b in fx:
                if ok(a.Label.split(" ")[0], b.Label.split(" ")[0]):
                    continue
                if s.BoundBox.intersect(b.Shape.BoundBox):
                    v = s.common(b.Shape).Volume
                    if v > 0.01:
                        hits.append((dz, a.Label.split(" ")[0], b.Label.split(" ")[0], round(v, 2)))
    inner = []
    for i, a in enumerate(mv):
        for b in mv[i + 1:]:
            ka, kb = a.Label.split(" ")[0], b.Label.split(" ")[0]
            if a.Shape.BoundBox.intersect(b.Shape.BoundBox) and not ok(ka, kb):
                v = a.Shape.common(b.Shape).Volume
                if v > 0.01:
                    inner.append((ka, kb, round(v, 2)))
    return dict(stroke=round(STROKE, 2), sweep=hits, inner=inner)
