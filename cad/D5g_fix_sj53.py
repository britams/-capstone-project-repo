# -*- coding: utf-8 -*-
"""D5g 승준 고침 (2026-11-08, CAP-AI-SJ-53) — 서현이 승준에게 CAD 수정을 맡김. D5g_frame_detail.make() 끝에서 부름.

승준 지적과 고친 것 (사진 순서):
 1) 브래킷 볼트 머리 겹침 + 육각 렌치 → 볼트를 모두 '십자 냄비머리'(ISO 7045, 드라이버)로.
    [확실 — 검사] 브래킷 52개 모두 두 볼트 머리가 1.49 mm³씩 겹쳤음: 구멍이 안쪽 면에서 8.5 mm인데
    육각 구멍 볼트 머리(Ø8.5 × 높이 5)는 8.5 − 4.25 < 5 이라 서로 부딪힘.
    냄비머리 M5(Ø9.5 × 3.5)는 8.5 − 4.75 = 3.75 > 3.5 → 0.25 mm 띄워짐.
    육각 구멍 볼트를 써야 할 이유: 머리가 작고 세게 조일 수 있음 — 우리 힘(수 N)에는 필요 없음 → 드라이버로 바꿈.
    커플링 멈춤나사(M4 무두)는 커플링에 붙어 오는 것이라 육각 렌치(2 mm)가 그대로 필요함.
 7) 문 서보 MG90S가 한쪽 귀만 붙어 있었음 [확실 — 검사]: 기둥 1(y −39.2)이 하우징(y −37.0까지) 밖이라 선으로만 닿음.
    → 하우징을 −y로 7.4 mm 늘려 기둥 1을 받치고, 기둥 2개는 하우징과 한 덩어리로 출력, 귀 구멍마다 M2 셀프 탭 나사(서보에 들어 있음).
    같은 문제: 28BYJ-48 모터 3개 귀에 나사가 없었음 → M4 십자 + 너트.
 색) 3D 프린트 부품만 주황(이 색은 다른 데 안 씀), 판 가공은 베이지, 놋쇠 부품(인서트·기둥·T너트)은 놋쇠색, 와고 레버는 회색.
 카메라) Raspberry Pi Camera Module 3 (Sony IMX708, 표준 렌즈) — AI 카메라(IMX500)는 최대 30 fps라 60 fps를 못 냄.
    1536 × 864 @ 120 fps 모드에서 720p 60 fps, 사진은 4608 × 2592. 초점 10 cm ~ 무한대(자동 초점), 25 × 24 × 11.5 mm.
    자리: 마킹실 격자 가운데 바로 위, 렌즈 끝 ~ 격자 윗면 155 mm (펜을 들고 지나가는 마커 꼭대기 528보다 12 mm 위).
    위판(105) 아래로 내려오는 걸이 181(3D 프린트)에 M2 나사 4개로 닮.
"""
import math

import FreeCAD as App
import Part

V = App.Vector

# ISO 7045 십자 냄비머리 (H형): d → (머리 지름 dk, 머리 높이 k, 드라이버 번호) [확실 — ISO 7045 최대값]
PAN = {2.0: (4.0, 1.6, 1), 2.5: (5.0, 2.0, 1), 3.0: (5.6, 2.4, 1), 4.0: (8.0, 3.1, 2), 5.0: (9.5, 3.5, 2)}
NUT = {4.0: (7.0, 3.2), 3.0: (5.5, 2.4)}                     # 육각 너트 (맞변 s, 두께 m) ISO 4032
BOLT_PRE = ("100h_bolt", "100j_bolt", "100m_bolt", "143s_bolt", "148m4_bolt", "148m5_bolt", "193s_bolt")   # 브래킷 볼트(100f·100f2)는 frame_bolts
DRIVER_R = {1: 2.25, 2: 3.0}                                  # 드라이버 축 반지름 (PH1 Ø4.5, PH2 Ø6)

CAM = dict(pcb=(25.0, 24.0, 1.0), hole_x=10.5, hole_y=(10.0, -2.5), hole_d=2.2, lens_y=2.5, lens_h=10.5,
           tip_z=540.0, x=55.0, y=0.0)                        # CM3: CM2와 같은 기판 25 × 24·구멍 (21 × 12.5) [가능성 높음 — 판매처 '같은 PCB']


def _get(doc, pre):
    return [o for o in doc.Objects if o.Label.startswith(pre) and hasattr(o, "Shape")]


def _placed(shp, p, n):
    """국부 +z 를 n 으로, 원점을 p 로"""
    s = shp.copy()
    s.Placement = App.Placement(V(p), App.Rotation(V(0, 0, 1), V(n)))
    return s


def pan_head(d):
    """국부: 받침면 z=0, 머리는 +z. 위 모서리 둥글게 + 십자 홈"""
    dk, k, ph = PAN[d]
    h = Part.makeCylinder(dk / 2, k)
    top = [e for e in h.Edges if hasattr(e.Curve, "Radius") and abs(e.BoundBox.ZMin - k) < 1e-6]
    try:
        h = h.makeFillet(0.35 * k, top)
    except Exception:
        pass
    w, Lc, dep = 0.13 * dk, 0.56 * dk, 0.5 * k
    cross = Part.makeBox(Lc, w, dep, V(-Lc / 2, -w / 2, k - dep)).fuse(Part.makeBox(w, Lc, dep, V(-w / 2, -Lc / 2, k - dep)))
    return h.cut(cross)


REG = []          # 이번에 만든 나사·너트: (종류 "screw"/"nut", 점, 방향, 지름) — 자리파기·드라이버 검사에 씀


def pan_screw(p, n, d, L):
    """p: 머리 받침면 점, n: 머리 쪽(바깥) 방향. 몸통은 −n 으로 L"""
    n = V(n)
    n.normalize()
    REG.append(("screw", V(p), V(n), d))
    shank = Part.makeCylinder(d / 2, L, V(0, 0, -L))
    return _placed(shank.fuse(pan_head(d)), p, n)


def hex_nut(p, n, d):
    """p: 너트 받침면 점, n: 너트가 쌓이는 방향"""
    s_, m_ = NUT[d]
    REG.append(("nut", V(p), V(n), d))
    hexa = Part.makePolygon([V(s_ / math.sqrt(3) * math.cos(math.radians(30 + 60 * i)), s_ / math.sqrt(3) * math.sin(math.radians(30 + 60 * i)), 0) for i in range(7)])
    nut = Part.Face(hexa).extrude(V(0, 0, m_)).cut(Part.makeCylinder(d / 2, m_ + 1, V(0, 0, -0.5)))
    return _placed(nut, p, n)


FLAT = {3.0: (5.5, 1.65, 1)}                                   # ISO 7046 십자 접시머리 M3: 머리 지름 5.5, 높이 1.65


def flat_screw(p, n, d, L):
    """접시머리: p = 머리 윗면(판 윗면과 같은 높이), 머리는 판 속으로 묻힘. L은 머리 포함 길이 (접시머리 규격)"""
    dk, k, ph = FLAT[d]
    n = V(n)
    n.normalize()
    REG.append(("flat", V(p), V(n), d))
    head = Part.makeCone(d / 2, dk / 2, k, V(0, 0, -k))
    w, Lc, dep = 0.13 * dk, 0.56 * dk, 0.6 * k
    head = head.cut(Part.makeBox(Lc, w, dep, V(-Lc / 2, -w / 2, -dep)).fuse(Part.makeBox(w, Lc, dep, V(-w / 2, -Lc / 2, -dep))))
    shank = Part.makeCylinder(d / 2, L - k, V(0, 0, -L))
    return _placed(shank.fuse(head), p, n)


def countersink(p, n, d):
    dk, k, _ = FLAT[d]
    return _placed(Part.makeCone(d / 2 + 0.2, dk / 2 + 0.3, k + 0.2, V(0, 0, -k - 0.2)).fuse(Part.makeCylinder(dk / 2 + 0.3, 2.0)), p, n)


def _cyl_faces(sol):
    return [f for f in sol.Faces if f.Surface.__class__.__name__ == "Cylinder"]


def bolt_info(sol):
    """기존 볼트 고체(몸통 원기둥 + 머리 원기둥) → (받침점 p, 머리 방향 n, 지름 d, 몸통 길이 L)"""
    cy = _cyl_faces(sol)
    head = max(cy, key=lambda f: f.Surface.Radius)
    rest = [f for f in cy if f.Surface.Radius < head.Surface.Radius - 0.1]
    shank = max(rest, key=lambda f: f.ParameterRange[3] - f.ParameterRange[2])
    a = V(head.Surface.Axis)
    o = V(head.Surface.Center)

    def ends(f):                                   # 면의 축 방향 범위 (모서리 위 점을 축에 투영)
        ts = [(V(e.valueAt(e.FirstParameter + (e.LastParameter - e.FirstParameter) * k)) - o).dot(a)
              for e in f.Edges for k in (0.0, 0.5, 1.0)]
        return min(ts), max(ts)
    h0, h1 = ends(head)
    s0, s1 = ends(shank)
    if (h0 + h1) / 2 > (s0 + s1) / 2:              # 머리가 +a 쪽 → 받침면 h0, 몸통은 h0 에서 s0 까지
        n, base, L = a, h0, h0 - s0
    else:
        n, base, L = a * -1, h1, s1 - h1
    d = round(2 * shank.Surface.Radius * 2) / 2.0
    return o + a * base, n, d, L


def frame_bolts(doc, G):
    """브래킷 볼트 100f(32 × 2)·100f2(20 × 2): 자리를 G.bracket_places()·G.joint_places() 에서 다시 계산
    (transformGeometry 로 만든 모양은 원기둥 정보가 없어 bolt_info 로 못 읽음)"""
    t, ha = G.BR["t"], G.BR["hole_at"]
    rep = []
    for pre, places in (("100f_bolt", G.bracket_places()), ("100f2_bolt", G.joint_places())):
        new = []
        for p, nx, nz in places:
            ex, ez = V(nx), V(nz)
            for loc, n in (((ha, 0, t), ez), ((t, 0, ha), ex)):              # 레일 다리 / 기둥 다리
                q = V(p) + ex * loc[0] + ez * loc[2]
                new.append(pan_screw(q, n, 5.0, 8.0))
        o = _get(doc, pre)[0]
        o.Shape = Part.makeCompound(new)
        o.Label = o.Label.split(" (")[0] + " (%d) — 십자 냄비머리 ISO 7045 M5 × 8" % len(new)
        rep.append((pre, len(new), ["M5×8"]))
    return rep


def phillips_all(doc):
    """BOLT_PRE 볼트를 모두 냄비머리 십자로. 반환: [(라벨, 개수, 지름 목록)]"""
    rep = []
    for pre in BOLT_PRE:
        for o in _get(doc, pre):
            new, ds = [], set()
            for s in o.Shape.Solids:
                p, n, d, L = bolt_info(s)
                L = min([x for x in (6, 8, 10, 12, 14, 16) if x >= L - 0.3] or [round(L)])
                new.append(pan_screw(p, n, d, L))
                ds.add("M%g×%d" % (d, L))
            o.Shape = Part.makeCompound(new)
            o.Label = o.Label.replace("McMaster 91292A1", "십자 냄비머리 (구 McMaster 91292A1").replace("91292A113)", "91292A113 육각 구멍 → 십자))")
            if "십자" not in o.Label:
                o.Label = o.Label + " — 십자 냄비머리 ISO 7045"
            rep.append((o.Label.split(" ")[0], len(new), sorted(ds)))
    return rep


# ---------------- 7) 문 서보 고정 ----------------
def gate_servo_fix(doc):
    """하우징을 −y로 늘려 기둥 1 받침, 기둥을 하우징에 합침, 귀마다 M2 × 8 셀프 탭 (서보 동봉) [가능성 높음 — 판매품 구성]"""
    screws, rep = [], []
    for g in ("112_entry_gate", "170_isolation_gate", "176_release_gate"):
        hs = _get(doc, g + "_housing")[0]
        posts = [_get(doc, g + "_post%d" % k)[0] for k in (1, 2)]
        hb = hs.Shape.BoundBox
        sh = hs.Shape
        for po in posts:
            pb = po.Shape.BoundBox
            zc, yc = pb.Center.z, pb.Center.y
            if yc - 2.2 < hb.YMin:                                       # 하우징 밖으로 나간 기둥 → 받침 블록
                y0 = yc - 2.2 - 3.0
                sh = sh.fuse(Part.makeBox(hb.XLength, hb.YMin - y0 + 0.01, 14.0, V(hb.XMin, y0, zc - 7.0)))
                rep.append("%s: 하우징 −y %.1f mm 늘림" % (g.split("_")[0], hb.YMin - y0))
            sh = sh.fuse(po.Shape)
            # 나사: 귀(두께 2.5) 바깥에서 기둥 쪽으로
            side_neg = pb.XMax < hb.XMax - 0.5 and pb.XMin < hb.XMin            # 서보가 −x 쪽
            if side_neg:
                p, n = V(pb.XMin - 2.5, yc, zc), V(-1, 0, 0)
            else:
                p, n = V(pb.XMax + 2.5, yc, zc), V(1, 0, 0)
            screws.append(pan_screw(p, n, 2.0, 8.0))
            doc.removeObject(po.Name)
        hs.Shape = sh.removeSplitter()
        hs.Label = hs.Label.split(" (")[0] + " (D5f 빔 구멍 + 서보 기둥 2개 한 덩어리 출력, SJ-53 −y 받침)"
    o = doc.addObject("Part::Feature", "SJ53_servo_screws")
    o.Label = "112s_gate_servo_screws (M2 × 8 셀프 탭 6개 — MG90S에 들어 있음)"
    o.Shape = Part.makeCompound(screws)
    return rep


# ---------------- 28BYJ-48 귀 볼트 ----------------
def _segment(shp, q, a, lo=-20.0, hi=20.0, step=0.25):
    ts = [lo + i * step for i in range(int((hi - lo) / step) + 1)]
    ins = [t for t in ts if shp.isInside(q + a * t, 1e-4, True)]
    return (min(ins), max(ins)) if ins else None


def stepper_ear_bolts(doc):
    """28BYJ-48 귀(구멍 Ø4.2, 몸통 중심에서 17.5) → 판. M4는 머리(반지름 4)·너트(모서리 4.04)가 몸통(반지름 14)에
    0.5 mm 걸림 [확실 — 17.5 − 4 < 14] → M3 × 10 십자 냄비머리(반지름 2.8)를 판 쪽에서, M3 너트를 귀 쪽에 (서현 M4 결정과 다름 — 확인 요청)"""
    bolts, nuts, rep, csk, grooves = [], [], [], [], []
    for mot, plate in (("153_floor_stepper", "152_motor_plate"), ("209_y_stepper", "211_y_motor_bracket"), ("215_x_stepper", "217_x_motor_plate")):
        mo = _get(doc, mot)[0]
        m, pl = mo.Shape, _get(doc, plate)[0].Shape
        for f in [f for f in m.Faces if f.Surface.__class__.__name__ == "Cylinder" and abs(f.Surface.Radius - 2.1) < 0.05]:
            a = V(f.Surface.Axis)
            c = f.BoundBox.Center
            to_c = m.BoundBox.Center - c                                  # 몸통 쪽으로 2.6 mm (귀 살 속)
            to_c = to_c - a * to_c.dot(a)
            to_c.normalize()
            q = c + to_c * 2.6
            se, sp = _segment(m, q, a), _segment(pl, q, a)
            if not se or not sp:
                rep.append("%s: 귀/판 못 찾음" % mot)
                continue
            if (se[0] + se[1]) / 2 < (sp[0] + sp[1]) / 2:                 # 판이 +a 쪽 → 머리는 판 바깥(+a)
                t_head, t_nut, n = sp[1], se[0], V(a)
            else:
                t_head, t_nut, n = sp[0], se[1], a * -1
            grip = abs(t_head - t_nut)
            L = min(x for x in (6, 8, 10, 12, 16) if x >= grip + NUT[3.0][1] + 0.8)
            ph = c + a * t_head
            if mot.startswith("153"):
                # 바닥 모터: 판 152 위 1.3 mm에 로드셀 막대(z 229.3)가 지나감 → 냄비머리(2.4)는 걸림 [확실 — 검사 0.24 mm³]
                # → 접시머리(판 속에 묻힘) + 판에 접시 자리, 드라이버가 옆판 151에 걸려 옆판 안쪽 면에 세로 홈(반지름 2.55)
                bolts.append(flat_screw(ph, n, 3.0, L))
                csk.append(countersink(ph, n, 3.0))
                grooves.append(_placed(Part.makeCylinder(DRIVER_R[1] + 0.3, 120.0), ph, n))
                kind = "접시머리"
            else:
                bolts.append(pan_screw(ph, n, 3.0, L))
                kind = "냄비머리"
            nuts.append(hex_nut(c + a * t_nut, n * -1, 3.0))
            rep.append("%s: M3 × %d %s + 너트 (판+귀 %.1f)" % (mot.split("_")[0], L, kind, grip))
    if csk:
        po = _get(doc, "152_motor_plate")[0]
        po.Shape = po.Shape.cut(Part.makeCompound(csk)).removeSplitter()
        for side in ("151_drive_side_L", "151_drive_side_R"):
            so = _get(doc, side)[0]
            hit = [g for g in grooves if so.Shape.common(g).Volume > 0.01]
            if hit:
                so.Shape = so.Shape.cut(Part.makeCompound(hit)).removeSplitter()
                rep.append("%s: 드라이버 홈 %d (안쪽 면, 반지름 2.55)" % (side.split("_")[0] + side[-1], len(hit)))
    for nm, lab, lst in (("SJ53_stepper_bolts", "153b_stepper_ear_bolts (28BYJ-48 귀 M3 × %d 십자 6개 — 판 쪽에서, 바닥 모터는 접시머리)" % L, bolts),
                         ("SJ53_stepper_nuts", "153n_stepper_ear_nuts (M3 육각 너트 6개 — 귀 쪽)", nuts)):
        o = doc.addObject("Part::Feature", nm)
        o.Label, o.Shape = lab, Part.makeCompound(lst)
    return rep


# ---------------- 카메라 ----------------
def camera_cm3(doc):
    c = CAM
    L, W, t = c["pcb"]
    x0, y0 = c["x"], c["y"] - c["lens_y"]                              # 기판 가운데 (렌즈는 기판 가운데에서 +y 2.5)
    zb = c["tip_z"] + c["lens_h"]                                      # 기판 아랫면 550.5
    pcb = Part.makeBox(L, W, t, V(x0 - L / 2, y0 - W / 2, zb))
    for sx in (-1, 1):
        for hy in c["hole_y"]:
            pcb = pcb.cut(Part.makeCylinder(c["hole_d"] / 2, t + 2, V(x0 + sx * c["hole_x"], y0 + hy, zb - 1)))
    lx, ly = c["x"], c["y"]
    lens = Part.makeBox(8.5, 8.5, 3.0, V(lx - 4.25, ly - 4.25, zb - 3.0)).fuse(Part.makeCylinder(3.6, c["lens_h"] - 3.0, V(lx, ly, c["tip_z"])))
    ffc = Part.makeBox(21.0, 5.5, 2.5, V(x0 - 10.5, y0 - W / 2, zb + t))          # 뒷면 15핀 FFC 커넥터
    cam = Part.makeCompound([pcb, lens, ffc])
    # 걸이 181: 받침판(3 mm) + 기둥 보스 4 (높이 3, 커넥터 피함) + 위판까지 기둥 2 (10 × 8) + 위 M3 인서트 자리
    tp = _get(doc, "105_top_plate")[0]
    top_bot, top_top = tp.Shape.BoundBox.ZMin, tp.Shape.BoundBox.ZMax       # 위판 105 아랫면·윗면 (모델에서 읽음: 610 / 615)
    zp0 = zb + t + 3.0
    plate = Part.makeBox(32.0, 42.0, 3.0, V(x0 - 16.0, y0 - 21.0, zp0))
    for sx in (-1, 1):
        for hy in c["hole_y"]:
            hx, hyy = x0 + sx * c["hole_x"], y0 + hy
            plate = plate.fuse(Part.makeCylinder(2.4, 3.0, V(hx, hyy, zb + t)))
            plate = plate.cut(Part.makeCylinder(0.85, 8.0, V(hx, hyy, zb)))            # M2 셀프 탭 구멍 Ø1.7
    CY = 17.0                                                          # 기둥은 ±y (±x 쪽은 돔 연결부 104가 위판 위에 있어 볼트 못 냄)
    for sy in (-1, 1):
        col = Part.makeBox(10.0, 8.0, top_bot - (zp0 + 3.0), V(x0 - 5.0, y0 + sy * CY - 4.0, zp0 + 3.0))
        col = col.cut(Part.makeCylinder(2.0, 6.0, V(x0, y0 + sy * CY, top_bot - 6.0)))     # M3 인서트 자리
        plate = plate.fuse(col)
    # 링 조명 받침 팔 2개 (기판 바깥 ±x → 링)
    ring_z = c["tip_z"] - 3.0
    for sx in (-1, 1):
        plate = plate.fuse(Part.makeBox(3.0, 6.0, zp0 - ring_z, V(x0 + sx * 15.0 - 1.5, ly - 3.0, ring_z + 3.0)))
        plate = plate.fuse(Part.makeBox(abs(15.0 - 12.0) + 1.5, 6.0, 2.0, V(min(x0 + sx * 15.0, x0 + sx * 12.0) - (0 if sx > 0 else 1.5), ly - 3.0, ring_z + 3.0)))
    ring = Part.makeCylinder(15.0, 3.0, V(lx, ly, ring_z)).cut(Part.makeCylinder(7.0, 5.0, V(lx, ly, ring_z - 1)))
    m2 = [pan_screw(V(x0 + sx * c["hole_x"], y0 + hy, zb), V(0, 0, -1), 2.0, 6.0) for sx in (-1, 1) for hy in c["hole_y"]]
    m3 = [pan_screw(V(x0, y0 + sy * CY, top_top), V(0, 0, 1), 3.0, 10.0) for sy in (-1, 1)]
    ins = [Part.makeCylinder(2.0, 4.3, V(x0, y0 + sy * CY, top_bot - 4.3)).cut(Part.makeCylinder(1.5, 5, V(x0, y0 + sy * CY, top_bot - 4.8))) for sy in (-1, 1)]
    # 위판 구멍
    tsh = tp.Shape
    for sy in (-1, 1):
        tsh = tsh.cut(Part.makeCylinder(1.7, 10, V(x0, y0 + sy * CY, top_bot - 1)))
    tp.Shape = tsh.removeSplitter()
    for pre, lab, shp in (("180_camera", "180_camera (Raspberry Pi Camera Module 3 표준 렌즈 IMX708 — 720p 60 fps, 렌즈 끝 z 540 = 격자 위 155 mm)", cam),
                          ("181_camera_bracket", "181_camera_bracket (3D 프린트 — 위판에서 내려오는 걸이, 카메라 M2 × 6 네 개, 링 조명 팔)", plate),
                          ("182_light_ring", "182_light_ring (링 조명 Ø30 — 렌즈 둘레, 걸이 팔에 붙임)", ring)):
        o = _get(doc, pre)
        if o:
            o[0].Shape, o[0].Label = shp, lab
    for nm, lab, shp in (("SJ53_cam_m2", "180s_camera_screws (M2 × 6 십자 냄비머리 4)", Part.makeCompound(m2)),
                         ("SJ53_cam_m3", "181s_bracket_bolts (M3 × 10 십자 냄비머리 2 — 위판 위에서)", Part.makeCompound(m3)),
                         ("SJ53_cam_ins", "181i_bracket_inserts (M3 인서트 2)", Part.makeCompound(ins))):
        o = doc.addObject("Part::Feature", nm)
        o.Label, o.Shape = lab, shp
    # 시야: 렌즈 끝 → 격자 윗면 40 × 40 (사각뿔)
    grid = _get(doc, "130_grid")[0].Shape.BoundBox
    gz = grid.ZMax
    apex = V(lx, ly, c["tip_z"])
    base = Part.makePolygon([V(55 - 20, -20, gz), V(55 + 20, -20, gz), V(55 + 20, 20, gz), V(55 - 20, 20, gz), V(55 - 20, -20, gz)])
    fr = Part.Face(base)
    sides = [Part.Face(Part.makePolygon([base.Vertexes[i].Point, base.Vertexes[(i + 1) % 4].Point, apex, base.Vertexes[i].Point])) for i in range(4)]
    view = Part.Solid(Part.Shell([fr] + sides))
    r = _get(doc, "REF_camera_view")
    if r:
        r[0].Shape = view
    return dict(dist=round(c["tip_z"] - gz, 1), view=view)


def view_block(doc, view):
    """카메라 시야(사각뿔)를 가리는 부품 — 카메라·링·격자·말벌·마킹실 벽 빼고"""
    skip = ("180", "181", "182", "130_grid", "REF_", "GSJ_", "120_chamber")
    out = []
    for o in doc.Objects:
        if not hasattr(o, "Shape") or o.Shape.isNull() or o.Label.startswith(skip) or o.TypeId == "App::DocumentObjectGroup":
            continue
        if not o.Shape.BoundBox.intersect(view.BoundBox):
            continue
        v = o.Shape.common(view).Volume
        if v > 0.5:
            out.append((o.Label[:40], round(v, 1)))
    return out


# ---------------- 자리파기 · 드라이버 검사 ----------------
NEW_A = ("112s_", "153b_", "153n_", "180s_", "181s_", "181i_")       # 이번에 새로 만든 구매품 (나사·너트·인서트)


def _printed(doc, G):
    return [o for o in doc.Objects if hasattr(o, "Shape") and o.TypeId == "Part::Feature" and not o.Shape.isNull()
            and G.category(o.Label) == "B" and not o.Label.startswith(PLATES)]


def _clear_shape(kind, p, n, d):
    """나사 머리 / 너트가 들어갈 자리 (+0.4 mm 틈)"""
    if kind == "screw":
        dk, k, _ = PAN[d]
        return _placed(Part.makeCylinder(dk / 2 + 0.4, k + 1.0), p, n)
    s_, m_ = NUT[d]
    r = s_ / math.sqrt(3) + 0.3
    hexa = Part.makePolygon([V(r * math.cos(math.radians(30 + 60 * i)), r * math.sin(math.radians(30 + 60 * i)), 0) for i in range(7)])
    return _placed(Part.Face(hexa).extrude(V(0, 0, m_ + 0.5)), p, n)


def pockets(doc, G):
    """새 나사 머리·너트가 3D 프린트 부품에 걸리면 그 부품에 자리를 판다 (나사가 지나는 구멍은 이미 있음)"""
    pr = _printed(doc, G)
    cuts = {}
    for kind, p, n, d in REG:
        if kind == "flat":                                             # 접시머리 자리는 stepper_ear_bolts 에서 팜
            continue
        c = _clear_shape(kind, p, n, d)
        for o in pr:
            if o.Shape.BoundBox.intersect(c.BoundBox) and o.Shape.common(c).Volume > 0.01:
                cuts.setdefault(o.Name, []).append(c)
    rep = []
    for nm, cs in cuts.items():
        o = doc.getObject(nm)
        o.Shape = o.Shape.cut(Part.makeCompound(cs)).removeSplitter()
        rep.append("%s: 자리 %d곳" % (o.Label.split(" ")[0], len(cs)))
    return rep


def driver_access(doc, reach=60.0):
    """나사마다 머리 위로 드라이버 축(PH1 Ø4.5 / PH2 Ø6)을 reach mm 세워 보고 막히면 보고 (나사·너트·인서트 자신은 뺌)"""
    fast = ("100f_", "100f2_", "100h_", "100j_", "100m_", "143s_", "148m", "193s_", "112s_", "153b_", "153n_", "180s_", "181s_",
            "100g", "100i_", "100k_", "100n_", "143i_", "181i_", "198s_")
    objs = [o for o in doc.Objects if hasattr(o, "Shape") and o.TypeId == "Part::Feature" and not o.Shape.isNull()
            and not o.Label.startswith(fast) and not o.Label.startswith(("REF_", "190_pi5_aihat")) and "_beam" not in o.Label[:22]]
    blocked = []
    for kind, p, n, d in REG:
        if kind == "nut":
            continue
        dk, k, ph = PAN[d] if kind == "screw" else (FLAT[d][0], -0.3, FLAT[d][2])
        r = DRIVER_R[ph]
        first = None
        for seg in range(int(reach / 10)):
            probe = _placed(Part.makeCylinder(r, 10.0, V(0, 0, k + 0.3 + seg * 10.0)), p, n)
            hit = [o.Label.split(" ")[0] for o in objs if o.Shape.BoundBox.intersect(probe.BoundBox) and o.Shape.common(probe).Volume > 0.05]
            if hit:
                first = (seg * 10, hit[:2])
                break
        if first:
            blocked.append(("M%g" % d, (round(p.x), round(p.y), round(p.z)), first[0], first[1]))
    return blocked


# ---------------- 색 ----------------
PLATES = ("101_deck", "105_top_plate")
BRASS = ("100g", "100i_", "100k_", "100n_", "143i_", "181i_", "198", "153n_")
PRINT_COLOR, PLATE_COLOR, BRASS_COLOR = (0.95, 0.45, 0.05), (0.86, 0.78, 0.60), (0.80, 0.68, 0.30)


def recolor(doc, G):
    """B 묶음을 B1 3D 프린트 / B2 판 가공으로 나누고, 3D 프린트 색(주황)은 다른 데 안 쓰게"""
    b1 = [o for o in doc.Objects if o.Name == "GSJ_B"][0]
    b1.Label = "B1 3D 프린트 (주황 — Craft-Lab, PETG)"
    b2 = doc.addObject("App::DocumentObjectGroup", "GSJ_B2")
    b2.Label = "B2 판 가공 (베이지 — 5 mm 판)"
    printed = []
    for o in list(b1.Group):
        if o.Label.startswith(PLATES):
            b1.removeObject(o)
            b2.addObject(o)
            if App.GuiUp:
                o.ViewObject.ShapeColor, o.ViewObject.Transparency = PLATE_COLOR, 0
        else:
            printed.append(o.Label.split(" ")[0])
            if App.GuiUp:
                o.ViewObject.ShapeColor = PRINT_COLOR
    a = [o for o in doc.Objects if o.Name == "GSJ_A"][0]
    for o in doc.Objects:
        if o.TypeId == "App::DocumentObjectGroup" or not hasattr(o, "Shape"):
            continue
        cat = G.category(o.Label)
        if cat == "A" and o not in a.Group:
            for g in o.InList:
                if g.TypeId == "App::DocumentObjectGroup":
                    g.removeObject(o)
            a.addObject(o)
        if not App.GuiUp:
            continue
        if o.Label.startswith(BRASS):
            o.ViewObject.ShapeColor = BRASS_COLOR
        elif o.Label.startswith("193w_wago_levers"):
            o.ViewObject.ShapeColor = (0.55, 0.55, 0.55)
        elif cat == "A" and o.Label.startswith(("112s_", "153b_", "180s_", "181s_")):
            o.ViewObject.ShapeColor = (0.25, 0.25, 0.28)
        elif (cat == "B" or o.Label.startswith("212_")) and o not in b2.Group:   # 212는 이름 속 '_beam' 때문에 D로 잘못 갔었음
            o.ViewObject.ShapeColor = PRINT_COLOR
            if o not in b1.Group:
                for g in o.InList:
                    if g.TypeId == "App::DocumentObjectGroup":
                        g.removeObject(o)
                b1.addObject(o)
    return sorted(set(printed))


def apply(doc, G):
    """D5g_frame_detail.make() 안에서 분류·색칠 다음에 부름"""
    del REG[:]
    if ("212_", "B") not in G.CATEGORY:                              # 새 구매품은 A, 212(이름 속 '_beam')는 3D 프린트
        G.CATEGORY[:0] = [(h, "A") for h in NEW_A] + [("212_", "B")]
    rep = {}
    rep["bolts"] = frame_bolts(doc, G) + phillips_all(doc)
    rep["gates"] = gate_servo_fix(doc)
    rep["steppers"] = stepper_ear_bolts(doc)
    cam = camera_cm3(doc)
    rep["camera_dist"] = cam["dist"]
    rep["pockets"] = pockets(doc, G)
    doc.recompute()
    rep["printed"] = recolor(doc, G)
    doc.recompute()
    return rep
