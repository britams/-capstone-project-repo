# -*- coding: utf-8 -*-
"""D5g — 2020 프레임 상세 + 부품 분류 (승준, 2026-11-06, CAP-AI-SJ-39)

D5f 전체 조립(cad/D5f_electrical_layout.py)을 그대로 만든 뒤 두 가지를 바꾼다. D5e·D5f 스크립트는 고치지 않는다.

1) 2020 프레임을 '실제 제품' 모양으로
   - 단면: 20 × 20, 홈 입구 6.2, 입구 턱 1.8, 언더컷 폭 11.0(턱 아래 2.2 수직) → 사다리꼴로 깊이 6.1에서 코어 7.4,
     가운데 Ø4.2 (M5 탭 구멍). 근거: 2020 슬롯 6 데이터시트(S6-20×20: 홈 6.2, 홈 깊이 6.1, 0.50 kg/m, I 0.72 cm⁴),
     미스미 LCF6-2020(홈 6, 0.47 kg/m, 표준 0.46 / 경량 0.45). McMaster 20 mm 시리즈는 페이지가 필터만 보여 단면 숫자를 못 읽음.
     → 검사 section_check(): 이 단면 0.452 kg/m · Ixx 0.719 cm⁴ (데이터시트 0.45~0.50 kg/m · 0.72 cm⁴) [확실 — 계산 대조]
     언더컷 폭 11.0·수직 2.2·코어 7.4는 위 두 값에 맞춘 값 [가능성 높음 — 제조사마다 ±0.5 다름]
   - 브래킷: 다이캐스트 2020 L 브래킷 — 다리 20 × 20, 폭 18, 두께 3.5, 양옆 리브 2, 홈 키(5.6 × 1.0), 구멍 Ø5.5 (모서리에서 12)
     [가능성 높음 — 국내 판매 '2020 코너 브래킷' 대표 치수, 실물로 확인]
   - 체결: 브래킷 1개당 M5 × 8 육각 구멍붙이 볼트(ISO 4762, 미스미 짝 E-GSCB5-8) 2 + 2020용 M5 슬라이드 T너트 2
     T너트: 목 5.8 × 1.5, 날개 10.4 × 2.0, 길이 10 [추측 — 실물 캘리퍼로 확인]
2) 모든 부품을 4가지로 나눠 묶고 색칠 (모델 트리에서 바로 구분)
   A 구매품(실제 제품) — 은색·회색 계열 / B 우리가 설계할 것(3D 프린트·가공) — 주황 /
   C 참고: 상용 트랩·말벌 — 반투명 초록 / D 자리 표시(전기 블록·빔) — 보라
   분류표는 CATEGORY, 이유는 NOTE.

실행 (FreeCAD 1.x):
    import sys; sys.path.insert(0, r"<repo>/cad"); import D5g_frame_detail as G
    doc = G.make();  print(G.section_check(), G.check(doc));  G.bom(doc)
"""
import FreeCAD as App
import Part

import D5e_full_assembly as A
import D5e_module_kinematic as K
import D5f_electrical_layout as E

V = App.Vector
DOC = "D5g_frame_detail"
S = 20.0

# ---------------- 2020 단면 ----------------
P = dict(open_w=6.2, lip=1.8, cav_w=11.0, cav_v=2.2, cav_d=6.1, core=7.4, bore=4.2)
REF = dict(kg_m=(0.45, 0.50), I_cm4=0.72)      # 데이터시트 (위 docstring)
RHO = 2.70e-3                                   # g/mm³, 6063-T5


def section_solid(t=1.0):
    """원점 중심 XY 단면을 z 0~t 로 민 고체"""
    h = S / 2
    sol = Part.makeBox(S, S, t, V(-h, -h, 0))
    y_lip = h - P["lip"]
    y_v = y_lip - P["cav_v"]
    y_bot = h - P["cav_d"]
    for ang in (0, 90, 180, 270):
        pts = [(-P["open_w"] / 2, h + 1), (P["open_w"] / 2, h + 1), (P["open_w"] / 2, y_lip), (P["cav_w"] / 2, y_lip),
               (P["cav_w"] / 2, y_v), (P["core"] / 2, y_bot), (-P["core"] / 2, y_bot), (-P["cav_w"] / 2, y_v),
               (-P["cav_w"] / 2, y_lip), (-P["open_w"] / 2, y_lip), (-P["open_w"] / 2, h + 1)]
        pr = Part.Face(Part.makePolygon([V(x, y, -1) for x, y in pts])).extrude(V(0, 0, t + 2))
        pr.rotate(V(0, 0, 0), V(0, 0, 1), ang)
        sol = sol.cut(pr)
    sol = sol.cut(Part.makeCylinder(P["bore"] / 2, t + 2, V(0, 0, -1)))
    return sol.Solids[0]


def section_check():
    s = section_solid(1.0)
    A_ = s.Volume
    kg_m = A_ * RHO
    I = (s.MatrixOfInertia.A11 - A_ / 12.0) / 1e4        # 판 두께 항 빼고 cm⁴
    ok = REF["kg_m"][0] - 0.01 <= kg_m <= REF["kg_m"][1] and abs(I - REF["I_cm4"]) / REF["I_cm4"] < 0.03
    return dict(area_mm2=round(A_, 1), kg_m=round(kg_m, 3), I_cm4=round(I, 3), ok=ok)


SEC = None


def member(p0, p1):
    global SEC
    if SEC is None:
        SEC = [f for f in section_solid(1.0).Faces if abs(f.normalAt(0, 0).z) > 0.99 and f.CenterOfMass.z < 0.5][0]
    p0, p1 = V(*p0), V(*p1)
    d = p1 - p0
    sol = SEC.copy().extrude(V(0, 0, d.Length))
    sol.Placement = App.Placement(p0, App.Rotation(V(0, 0, 1), d))
    return sol


# ---------------- 브래킷·볼트·T너트 (브래킷 지역 좌표) ----------------
# 지역 좌표: 원점 = 기둥 면·레일 중심선·레일 면이 만나는 점 (D5e A.bracket 과 같음)
#   x: 레일 따라 (기둥에서 멀어짐), z: 레일 면에서 바깥(브래킷 쪽), y: 폭 방향. 레일은 z<0, 기둥은 x<0.
BR = dict(leg=20.0, w=18.0, t=3.5, rib=2.0, key_w=5.6, key_d=1.0, hole=5.5, hole_at=12.0)
BOLT = dict(d=5.0, L=8.0, head_d=8.5, head_h=5.0)
TNUT = dict(neck_w=5.8, neck_h=1.5, wing_w=10.4, wing_h=2.0, L=10.0)


def bracket_local():
    b = BR
    w2 = b["w"] / 2
    s = Part.makeBox(b["leg"], b["w"], b["t"], V(0, -w2, 0)).fuse(Part.makeBox(b["t"], b["w"], b["leg"], V(0, -w2, 0)))
    for y0 in (-w2, w2 - b["rib"]):                                  # 양옆 삼각 리브
        tri = Part.Face(Part.makePolygon([V(b["t"], y0, b["t"]), V(b["leg"], y0, b["t"]), V(b["t"], y0, b["leg"]), V(b["t"], y0, b["t"])]))
        s = s.fuse(tri.extrude(V(0, b["rib"], 0)))
    s = s.fuse(Part.makeBox(b["leg"] - 6, b["key_w"], b["key_d"], V(5, -b["key_w"] / 2, -b["key_d"])))          # 레일 홈 키
    s = s.fuse(Part.makeBox(b["key_d"], b["key_w"], b["leg"] - 6, V(-b["key_d"], -b["key_w"] / 2, 5)))          # 기둥 홈 키
    s = s.cut(Part.makeCylinder(b["hole"] / 2, 10, V(b["hole_at"], 0, -3)))
    s = s.cut(Part.makeCylinder(b["hole"] / 2, 10, V(-3, 0, b["hole_at"]), V(1, 0, 0)))
    return s.removeSplitter()


def bolt_local(on="rail"):
    """M5 × 8: 머리는 브래킷 위, 몸통은 면 안으로"""
    t, bo = BR["t"], BOLT
    if on == "rail":
        p, d = V(BR["hole_at"], 0, t), V(0, 0, -1)
    else:
        p, d = V(t, 0, BR["hole_at"]), V(-1, 0, 0)
    shank = Part.makeCylinder(bo["d"] / 2, bo["L"], p, d)
    head = Part.makeCylinder(bo["head_d"] / 2, bo["head_h"], p, d * -1)
    head = head.cut(Part.makeCylinder(2.0, 2.5, p - d * (bo["head_h"] - 2.5), d * -1))     # 육각 구멍 자리 (원으로 표시)
    return shank.fuse(head)


def tnut_local(on="rail"):
    """슬라이드 T너트: 목은 홈 입구, 날개는 언더컷 안. 레일 따라 길이 L."""
    tn = TNUT
    lip = P["lip"]
    neck = Part.makeBox(tn["L"], tn["neck_w"], tn["neck_h"], V(-tn["L"] / 2, -tn["neck_w"] / 2, -lip))
    wing = Part.makeBox(tn["L"], tn["wing_w"], tn["wing_h"], V(-tn["L"] / 2, -tn["wing_w"] / 2, -lip - 0.1 - tn["wing_h"]))
    s = neck.fuse(wing).cut(Part.makeCylinder(BOLT["d"] / 2, 10, V(0, 0, -6)))
    if on == "rail":
        s.translate(V(BR["hole_at"], 0, 0))
    else:      # 기둥 면: 지역 x<0 이 기둥 안, 기둥 따라(z) 길이
        s.rotate(V(0, 0, 0), V(0, 1, 0), 90)      # 지역 z<0(면 안) → x<0(기둥 안), 길이 x → z
        s.translate(V(0, 0, BR["hole_at"]))
    return s


def to_world(shp, p, nx, nz):
    m = App.Matrix()
    ex, ez = V(*nx), V(*nz)
    ey = ez.cross(ex)
    m.A11, m.A21, m.A31 = ex.x, ex.y, ex.z
    m.A12, m.A22, m.A32 = ey.x, ey.y, ey.z
    m.A13, m.A23, m.A33 = ez.x, ez.y, ez.z
    s = shp.transformGeometry(m)
    s.translate(V(*p))
    return s


def bracket_places():
    """D5e A.frame() 의 브래킷 자리 그대로 (4단 × 기둥 4 × 2 = 32)"""
    c, s = K.FR["c"], S
    levels = [("0", 0.0), ("deck", K.FR["deck_z"]), ("gantry", K.FR["gantry_z"]), ("top", K.FR["top_z"])]
    out = []
    for nm, z in levels:
        for (x, y) in ((-c, -c), (c, -c), (c, c), (-c, c)):
            sx, sy = (1 if x < 0 else -1), (1 if y < 0 else -1)
            zb = z + s if nm == "0" else z
            nzv = (0, 0, 1) if nm == "0" else (0, 0, -1)
            out.append(((x + sx * s / 2, y, zb), (sx, 0, 0), nzv))
            out.append(((x, y + sy * s / 2, zb), (0, sy, 0), nzv))
    return out


# ---------------- 분류 ----------------
# (머리말, 분류) — 위에서부터 먼저 맞는 것
CATEGORY = [
    ("REF_camera_view", "X"), ("P204", "X"), ("190_pi5_aihat (D5e", "X"),
    ("REF_", "C"),
    ("193_", "D"), ("194_", "D"), ("195_", "D"), ("196_", "D"),
    ("100", "A"), ("153_", "A"), ("153r_", "A"), ("209_", "A"), ("209r_", "A"), ("215_", "A"), ("215r_", "A"),
    ("154_", "A"), ("210_", "A"), ("216_", "A"), ("155_", "A"), ("208_", "A"), ("214_", "A"),
    ("159_", "A"), ("224_", "A"), ("225_", "A"), ("157_", "A"), ("207_", "A"), ("213_", "A"), ("223_", "A"),
    ("221_", "A"), ("222_", "A"), ("146_", "A"), ("147_", "A"), ("148_", "A"), ("149_", "A"),
    ("_servo_MG90S", "A"), ("_servo_spline", "A"), ("_horn", "A"), ("205_z_servo", "A"), ("205s_", "A"), ("205h_", "A"),
    ("114_entry_sensor", "A"), ("180_", "A"), ("182_", "A"), ("190_", "A"), ("191_", "A"), ("192_", "A"), ("201_", "A"),
    ("", "B"),
]
NOTE = {
    "A": "구매품 — 판매 규격 그대로 산다. 치수는 카탈로그·실측으로 확인 (purchase/ 표)",
    "B": "우리가 설계 — 3D 프린트(PLA/PETG) 또는 판 가공. 승준이 상세 설계(구멍·두께·체결)",
    "C": "참고 — 산 상용 트랩·말벌 크기 (고치지 않음)",
    "D": "자리 표시 — 전기 부품 블록. 실제 모양은 제품 외형도로 바꿀 것 (구매품)",
}
GROUP_LABEL = {"A": "A 구매품 (실제 제품)", "B": "B 우리가 설계할 것 (3D 프린트·가공)",
               "C": "C 참고: 상용 트랩·말벌", "D": "D 자리 표시 (전기, 실제 모양 아님)"}
COLOR = {"A": (0.62, 0.66, 0.72), "B": (0.95, 0.55, 0.15), "C": (0.40, 0.75, 0.35), "D": (0.55, 0.35, 0.75)}


def category(label):
    for head, cat in CATEGORY:
        if head in label:
            return cat
    return "B"


def make():
    E.DOC = DOC
    A.DOC = DOC
    if DOC in App.listDocuments():
        App.closeDocument(DOC)
    doc = E.make()
    # 1) 프레임 부재를 상세 단면으로 (자리는 같음)
    mem, _ = A.frame()
    names = {"P" + nm.replace("+", "p").replace("-", "m"): nm for nm, _s, _L in mem}
    for o in doc.Objects:
        if o.Name in names:
            for nm, shp, L in mem:
                if names[o.Name] == nm:
                    bb = shp.BoundBox
                    d = [bb.XLength, bb.YLength, bb.ZLength]
                    ax = d.index(max(d))
                    c = bb.Center
                    p0, p1 = [c.x, c.y, c.z], [c.x, c.y, c.z]
                    p0[ax] -= L / 2
                    p1[ax] += L / 2
                    o.Shape = member(p0, p1)
                    o.Label = "%s (2020 상세, L %d)" % (nm, round(L))
    # 2) 브래킷·볼트·T너트
    for o in list(doc.Objects):
        if o.Label == "100_brackets":
            doc.removeObject(o.Name)
    br, bo, tn = [], [], []
    bl, bol_r, bol_p, tn_r, tn_p = bracket_local(), bolt_local("rail"), bolt_local("post"), tnut_local("rail"), tnut_local("post")
    for p, nx, nz in bracket_places():
        br.append(to_world(bl, p, nx, nz))
        bo += [to_world(bol_r, p, nx, nz), to_world(bol_p, p, nx, nz)]
        tn += [to_world(tn_r, p, nx, nz), to_world(tn_p, p, nx, nz)]
    for nm, lst in (("100e_bracket_2020_L (32)", br), ("100f_bolt_M5x8 (64)", bo), ("100g_tnut_M5_slot6 (64)", tn)):
        o = doc.addObject("Part::Feature", "P" + nm.split(" ")[0])
        o.Label = nm
        o.Shape = Part.makeCompound(lst)
    for o in list(doc.Objects):        # D5f에서 스프링 204 뺀 뒤 남은 바탕 원기둥
        if o.Label in ("P204a", "P204b"):
            doc.removeObject(o.Name)
    # 3) 분류 묶음 + 색
    groups = {}
    for k in ("A", "B", "C", "D"):
        g = doc.addObject("App::DocumentObjectGroup", "GSJ_" + k)
        g.Label = GROUP_LABEL[k]
        groups[k] = g
    for o in list(doc.Objects):
        if o.TypeId == "App::DocumentObjectGroup" or not hasattr(o, "Shape"):
            continue
        k = category(o.Label)
        if k == "X":
            if App.GuiUp:
                o.ViewObject.Visibility = False
            continue
        for g in o.InList:
            if g.TypeId == "App::DocumentObjectGroup":
                g.removeObject(o)
        groups[k].addObject(o)
        if App.GuiUp and not o.Label.startswith("196_gate") and "beam" not in o.Label:
            o.ViewObject.ShapeColor = COLOR[k]
            if k == "C" and "container" not in o.Label:
                o.ViewObject.Transparency = 60
    for o in list(doc.Objects):        # 빈 옛 묶음 지우기
        if o.TypeId == "App::DocumentObjectGroup" and not o.Name.startswith("GSJ_") and not o.Group:
            doc.removeObject(o.Name)
    doc.recompute()
    return doc


def check(doc):
    """겹침 검사: 상세 프레임 ↔ 브래킷·볼트·T너트, 그리고 다른 부품 ↔ 상세 프레임 (0.5 mm³ 넘으면 보고)"""
    frame = [o for o in doc.Objects if o.Label.startswith("100") and "2020 상세" in o.Label]
    hw = [o for o in doc.Objects if o.Label.startswith(("100e_", "100f_", "100g_"))]
    out = []
    for h in hw:
        for s in h.Shape.Solids:
            for f in frame:
                if s.BoundBox.intersect(f.Shape.BoundBox):
                    v = s.common(f.Shape).Volume
                    if v > 0.5:
                        out.append((h.Label, f.Label, round(v, 1)))
    others = [o for o in doc.Objects if hasattr(o, "Shape") and o.TypeId != "App::DocumentObjectGroup" and o not in frame and o not in hw
              and o.ViewObject.Visibility and not o.Label.startswith(("REF_", "196_gate"))]
    for o in others:
        for f in frame:
            if o.Shape.BoundBox.intersect(f.Shape.BoundBox):
                v = o.Shape.common(f.Shape).Volume
                if v > 0.5:
                    out.append((o.Label, f.Label, round(v, 1)))
    return out


def bom(doc):
    """분류별 목록 출력 (A: 사는 것, B: 설계할 것)"""
    rows = {}
    for o in doc.Objects:
        if o.TypeId == "App::DocumentObjectGroup" and o.Name.startswith("GSJ_"):
            rows[o.Label] = sorted(x.Label for x in o.Group)
    for k, v in rows.items():
        print("== %s (%d)" % (k, len(v)))
        for x in v:
            print("   ", x)
    return rows
