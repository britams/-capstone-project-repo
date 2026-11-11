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
     T너트: 길이 10 × 폭 9.5 × 두께 4.5 (판매품 'M5 sliding T-nut 2020, 6 mm slot' 표기값) — 목 5.8 × 1.3, 날개 9.5 × 2.0,
            아래 경사 1.2 (언더컷 사다리꼴에 맞춤) [가능성 높음 — 판매처 표기, 목·경사 나눔은 단면에 맞춘 값]
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
BR = dict(leg=20.0, w=18.0, t=3.5, rib=2.0, key_w=5.6, key_d=0.5, hole=5.5, hole_at=12.0)
BOLT = dict(d=5.0, L=8.0, head_d=8.5, head_h=5.0)
TNUT = dict(neck_w=5.8, top=-0.5, wing_w=9.5, wing_h=2.0, taper_h=1.2, taper_w=6.0, L=10.0)   # 두께 0.5→5.0 = 4.5


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
    """슬라이드 T너트 (판매품 10 × 9.5 × 4.5): 목은 홈 입구(면에서 0.5 아래부터), 날개는 언더컷 안, 아래는 경사"""
    tn = TNUT
    lip = P["lip"]
    y0 = -lip - tn["wing_h"]
    pts = [(-tn["neck_w"] / 2, tn["top"]), (tn["neck_w"] / 2, tn["top"]), (tn["neck_w"] / 2, -lip), (tn["wing_w"] / 2, -lip),
           (tn["wing_w"] / 2, y0), (tn["taper_w"] / 2, y0 - tn["taper_h"]), (-tn["taper_w"] / 2, y0 - tn["taper_h"]),
           (-tn["wing_w"] / 2, y0), (-tn["wing_w"] / 2, -lip), (-tn["neck_w"] / 2, -lip), (-tn["neck_w"] / 2, tn["top"])]
    face = Part.Face(Part.makePolygon([V(-tn["L"] / 2, y, z) for y, z in pts]))
    s = face.extrude(V(tn["L"], 0, 0)).cut(Part.makeCylinder(BOLT["d"] / 2, 12, V(0, 0, -8)))
    if on == "rail":
        s.translate(V(BR["hole_at"], 0, 0))
    else:
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


def joint_places():
    """가로대 100c(4개)·갠트리 레일 100d 끝 이음부 (CAP-AI-SJ-49). 부재 끝이 옆 레일 안쪽 면에 맞닿는 'T 이음'.
    브래킷은 부재의 양 옆면에 1개씩 (끝 1곳에 2개): 한 다리는 부재 옆면 홈, 다른 다리는 받는 레일 안쪽 면 홈.
    (아래면에 달면 받는 레일 높이 20 mm 밖으로 다리가 나가서 볼트 걸 홈이 없음 → 옆면으로)"""
    c = K.FR["c"]
    e = c - S / 2                                          # 160: 받는 레일 안쪽 면
    out = []
    for z in (K.FR["deck_z"] + S / 2, K.FR["top_z"] + S / 2):      # 100c: x 방향, y ±80
        for y in (-80.0, 80.0):
            for xe, ax in ((-e, 1), (e, -1)):
                for ny in (-1, 1):
                    out.append(((xe, y + ny * S / 2, z), (ax, 0, 0), (0, ny, 0)))
    zg = K.FR["gantry_z"] + S / 2                          # 100d: y 방향, x −18
    for ye, ay in ((-e, 1), (e, -1)):
        for nx in (-1, 1):
            out.append(((-18.0 + nx * S / 2, ye, zg), (0, ay, 0), (nx, 0, 0)))
    return out


# ---------------- 분류 ----------------
# (머리말, 분류) — 위에서부터 먼저 맞는 것
CATEGORY = [
    ("REF_camera_view", "X"), ("P204", "X"), ("190_pi5_aihat (D5e", "X"),
    ("REF_", "C"),
    ("195p_", "A"), ("198_", "A"), ("198p_", "A"), ("190r_", "A"), ("193_terminal", "A"), ("193w_", "A"), ("198u_", "A"), ("142n_", "A"), ("144n_", "A"), ("100h_", "A"), ("100i_", "A"),
    ("143i_", "A"), ("143t_", "A"), ("143s_", "A"), ("143m", "A"), ("144p", "A"), ("144h", "A"), ("144s_", "A"), ("144t_", "A"), ("227p", "A"),
    ("193s_", "A"), ("193v_", "A"), ("193g_", "A"), ("193j_", "A"), ("194f_", "A"), ("196m_", "A"), ("198h_", "A"), ("198m_", "A"),   # (SJ-49) 새 구매품
    ("_beam", "D"), ("196_gate_G", "A"), ("194_", "A"), ("193_", "D"), ("196_", "D"),
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
        # 숫자로 시작하는 머리말은 이름 앞에서만 비교 (설명 글 속 '100d' 같은 글자에 걸리지 않게, SJ-49)
        if (label.startswith(head) if head[:1].isdigit() else head in label):
            return cat
    return "B"


def add_joint_hw(doc, bl=None, bol_r=None, bol_p=None, tn_r=None, tn_p=None):
    """가로대·갠트리 레일 끝 T 이음 브래킷 20개 + 볼트 40 + T너트 40"""
    bl = bl or bracket_local()
    bol_r, bol_p = bol_r or bolt_local("rail"), bol_p or bolt_local("post")
    tn_r, tn_p = tn_r or tnut_local("rail"), tn_p or tnut_local("post")
    br, bo, tn = [], [], []
    for p, nx, nz in joint_places():
        br.append(to_world(bl, p, nx, nz))
        bo += [to_world(bol_r, p, nx, nz), to_world(bol_p, p, nx, nz)]
        tn += [to_world(tn_r, p, nx, nz), to_world(tn_p, p, nx, nz)]
    n = len(br)
    for nm, lst in (("100e2_bracket_2020_L_T이음 (%d)" % n, br), ("100f2_bolt_M5x8_T이음 (%d)" % (2 * n), bo),
                    ("100g2_tnut_M5_slot6_T이음 (%d)" % (2 * n), tn)):
        for o in list(doc.Objects):
            if o.Label.split(" ")[0] == nm.split(" ")[0]:
                doc.removeObject(o.Name)
        o = doc.addObject("Part::Feature", "P" + nm.split(" ")[0])
        o.Label = nm
        o.Shape = Part.makeCompound(lst)
    return n


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
    add_joint_hw(doc, bl, bol_r, bol_p, tn_r, tn_p)
    import D5g_feeder_uln as FU                     # 설탕물 급이 방 + ULN2003 실제 보드 (CAP-AI-SJ-40)
    import sys
    FU.make_into(doc, sys.modules[__name__])
    FU.support_fixes(doc)
    FU.release_exit_fix(doc)
    FU.release_shaft_apply(doc)
    _lid = doc.addObject('Part::Feature', 'SJ_lid'); _lid.Label = '143l_feed_trough_lid (뚜껑, 3D 프린트 PETG — 벌레 막기)'; _lid.Shape = FU.trough_lid()
    FU.feeder_detail_apply(doc)                     # (SJ-49) 급이 방 상세: 벽 보스·인서트·손나사·튜브 집게·코튼롤 잡이
    global PRESS_REPORT
    _o, PRESS_REPORT = FU.press_apply(doc)          # (CAP-AI-60, 교수님 피드백) 로드셀 → 스프링 받침 칸 + 걸쇠 + 누름 스위치 (SJ-49 로드셀 대신)
    import D5g_real_parts as RP                      # 전기 부품 실제 CAD (KiCad STEP·Pi 5 공식 STEP, 인터넷 필요)
    try:
        RP.apply(doc)
    except Exception as e:
        print('실제 부품 CAD 못 받음 (인터넷 확인):', e)
    import D5g_fasten as FA                          # (SJ-49) 얹기만 했던 부품 볼트 체결
    FA.fasten(doc, sys.modules[__name__])
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
    import D5g_fix_sj53 as FX          # (SJ-53, 서현 요청) 십자 냄비머리 볼트·문 서보 고정·모터 귀 나사·카메라 CM3·3D 프린트 색
    global FIX_REPORT
    FIX_REPORT = FX.apply(doc, sys.modules[__name__])
    import D5g_circuit_sj53 as FC      # (SJ-53) 허브 기판 2장(서현 hub_boards.py 배치)·MOSFET 모듈 자세히 — 인터넷 필요
    FIX_REPORT["circuit"] = FC.apply(doc)
    import D5g_c3_hx711_dcjack as C3   # (CAP-AI-55, 서현) HX711 모듈·받침 + 패널 DC 잭 (194b −y로 늘림)
    FIX_REPORT["c3"] = C3.apply(doc)
    import D5g_home_switches as HS     # (CAP-AI-55, 서현) 원점 스위치 F·X·Y + X 집게 226 + 투명 격자 130
    FIX_REPORT["switches"] = HS.apply(doc)
    # (11/11, CAP-AI-61) 급이 발 인서트·McMaster 나사 없앰 → 앵글 + M3 나사·너트 (D5g_feeder_uln.feeder_hardware) — D5g_feeder_mcm 지움
    import D5g_feeder_pump as FPMP     # (CAP-AI-59, 서현) 급이: 바깥 병 + 연동 펌프 + 관 + 걸이 (사용자 편의)
    FIX_REPORT["feeder_pump"] = FPMP.apply(doc)
    FIX_REPORT["press"] = FU.press_check(doc, PRESS_REPORT)   # (CAP-AI-60) 누름 장치 겹침·올림 길
    import D5g_print_color as PCOL     # (CAP-AI-58, 서현) 3D 프린트 부품만 파랑, 나머지 회색 — 맨 끝 (앞 단계 색을 덮음)
    FIX_REPORT["print_color"] = PCOL.apply(doc)
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
