# -*- coding: utf-8 -*-
"""D5e 이음부 검사 + 움직임 간섭 검사 (CAP-AI-20)

FreeCAD에서 D5e_module_kinematic.py를 불러 쓴다:
    ns = {}; exec(open(D5e_module_kinematic.py).read(), ns); P, M = ns["build"](); R = run(ns, P, M)
검사 3가지
  1) 이음부 (JOINTS 표): 끼움 길이(insert), 면 접촉(contact), 나사 길(screw — 두 부품의 구멍이 한 줄인지 탐침 원기둥으로),
     미끄럼·회전 틈(slide — 닿지도 겹치지도 않아야 함, 또는 맞닿음만), 혼–탭 밀기(push)
  2) 겹침·뜬 부품·프레임 연결 (관절 0 자세)
  3) 움직임 간섭: 자세 여러 개에서 움직이는 부품과 다른 부품의 겹침
"""
import json
import FreeCAD as App
import Part

V = App.Vector
TOL = 1e-3


def solid_fill(shp):
    """구멍을 메운 외곽 (끼움 길이 계산용): 바운딩 박스"""
    bb = shp.BoundBox
    return Part.makeBox(max(bb.XLength, 1e-3), max(bb.YLength, 1e-3), max(bb.ZLength, 1e-3), V(bb.XMin, bb.YMin, bb.ZMin))


def overlap(a, b):
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    try:
        return a.common(b).Volume
    except Exception:
        return -1.0


def dist(a, b):
    if not a.BoundBox.intersect(b.BoundBox):
        bb = a.BoundBox
        bb2 = b.BoundBox
        gx = max(0, max(bb.XMin, bb2.XMin) - min(bb.XMax, bb2.XMax))
        gy = max(0, max(bb.YMin, bb2.YMin) - min(bb.YMax, bb2.YMax))
        gz = max(0, max(bb.ZMin, bb2.ZMin) - min(bb.ZMax, bb2.ZMax))
        if max(gx, gy, gz) > 0.5:
            return max(gx, gy, gz)
    return a.distToShape(b)[0]


def insert_len(a, b, sec):
    """a(축·봉)가 b(구멍 가진 부품)의 외곽 안에 들어간 길이 = 겹친 부피 / a 단면적"""
    return a.common(solid_fill(b)).Volume / sec


def screw_probe(p, d, r, L):
    return Part.makeCylinder(r, L, V(p) - V(d).normalize() * (L / 2), V(d))


def check_joint(j, S):
    kind = j["kind"]
    a, b = S[j["a"]], S[j["b"]]
    out = dict(id=j["id"], desc=j["desc"], a=j["a"], b=j["b"], kind=kind)
    ov = overlap(a, b)
    out["overlap_mm3"] = round(ov, 3)
    if kind == "insert":
        import math
        sec = j["sec"] if "sec" in j else math.pi * j["ra"] ** 2
        L = insert_len(a, b, sec)
        out["value"] = round(L, 2)
        out["ok"] = (ov < 0.05) and L >= j["min"] - 0.05
        out["need"] = "끼움 ≥ %.1f mm, 겹침 0" % j["min"]
    elif kind == "contact":
        d = dist(a, b)
        out["value"] = round(d, 4)
        out["ok"] = d < TOL and ov < 0.05
        out["need"] = "면 접촉 (거리 0, 겹침 0)"
    elif kind == "slide":
        d = dist(a, b)
        out["value"] = round(d, 4)
        out["ok"] = ov < 0.05
        out["need"] = "겹침 0 (미끄럼·회전 틈)"
    elif kind == "push":
        d = dist(a, b)
        out["value"] = round(d, 4)
        out["ok"] = d < 0.05 and ov < 0.5
        out["need"] = "혼 끝이 탭을 밂 (거리 0)"
    elif kind == "screw":
        pr = screw_probe(j["p"], j["d"], j["r"], j["L"])
        va, vb = overlap(pr, a), overlap(pr, b)
        hit_a = pr.BoundBox.intersect(a.BoundBox)
        hit_b = pr.BoundBox.intersect(b.BoundBox)
        out["value"] = [round(va, 3), round(vb, 3)]
        out["ok"] = va < 0.05 and vb < 0.05 and hit_a and hit_b and dist(a, b) < TOL
        out["need"] = "구멍이 한 줄 (탐침 Ø%.1f가 두 부품 재료에 안 닿음) + 면 접촉" % (2 * j["r"])
    return out


def joints(ns, P, M):
    """이음부 표. 자세(J)를 같이 적어 그 자세에서 검사"""
    J0 = dict(ns["JOINT0"])
    cx, sy = ns["cx"], -13.0
    XY, M28, NUT = ns["XY"], ns["M28"], ns["NUT"]
    JL = []

    def add(id_, desc, a, b, kind, pose=None, **kw):
        d = dict(id=id_, desc=desc, a=a, b=b, kind=kind, pose=pose or {})
        d.update(kw)
        JL.append(d)

    # 바닥 승강 (153~159)
    for sx in (-1, 1):
        add("F1%s" % ("a" if sx < 0 else "b"), "바닥 모터 귀 ↔ 모터판 (M4 나사)", "153_floor_stepper_28BYJ48", "152_motor_plate", "screw",
            p=V(cx - sx * M28["ear_c"] / 2, sy + M28["off"], 225), d=V(0, 0, 1), r=1.9, L=8)
    add("F2", "바닥 모터 축 ↔ 커플링 (5 mm 쪽)", "153r_floor_motor_shaft", "154_coupling", "insert", sec=14.04, min=6.0)
    add("F3", "T8 나사 ↔ 커플링 (8 mm 쪽)", "155_lead_screw_T8", "154_coupling", "insert", ra=4.0, min=10.0)
    add("F4a", "T8 나사 ↔ 바닥 너트 (내림)", "155_lead_screw_T8", "159_floor_nut_T8", "insert", ra=4.0, min=14.9)
    add("F4b", "T8 나사 ↔ 바닥 너트 (올림 36.5)", "155_lead_screw_T8", "159_floor_nut_T8", "insert", pose=dict(floor=36.5), ra=4.0, min=14.9)
    add("F5", "바닥 너트 플랜지 ↔ 캐리지 (M3 ×4)", "159_floor_nut_T8", "158_carriage", "screw", p=V(cx + 5.657, sy + 5.657, 262), d=V(0, 0, 1), r=1.4, L=8)
    add("F6a", "가이드봉 ↔ 모터판 (끼움)", "157_guide_rod", "152_motor_plate", "insert", ra=2.0, min=2.9)
    add("F6b", "가이드봉 ↔ 바닥판 121 (끼움)", "157_guide_rod", "121_chamber_base", "insert", ra=2.0, min=2.9)
    add("F6c", "가이드봉 ↔ 캐리지 (미끄럼, 돌림 막이)", "157_guide_rod", "158_carriage", "slide")
    add("F7a", "캐리지 ↔ 로드셀", "158_carriage", "148_load_cell", "contact")
    add("F7b", "로드셀 ↔ 스프링 146", "148_load_cell", "146_spring", "contact")
    add("F7c", "스프링 146 ↔ 밀대 턱 (힘이 스프링을 지남)", "146_spring", "147_push_rod", "contact")
    add("F7d", "밀대 ↔ 승강 바닥 (끼움 3)", "147_push_rod", "140_lift_floor", "insert", ra=2.0, min=2.9)
    add("F7e", "밀대 ↔ 바닥판 구멍 (미끄럼)", "147_push_rod", "121_chamber_base", "slide")
    add("F8a", "모터판 ↔ 옆판 L", "152_motor_plate", "151_drive_side_L", "contact")
    add("F8b", "옆판 L ↔ 받침판 101", "151_drive_side_L", "101_deck", "contact")
    add("F8c", "옆판 L ↔ 바닥판 121", "151_drive_side_L", "121_chamber_base", "contact")
    # 문 3개
    for g, key in (("112_entry_gate", "door_entry"), ("170_isolation_gate", "door_iso"), ("176_release_gate", "door_rel")):
        add(g + "-1", "문 서보 귀 ↔ 기둥 1", g + "_servo_MG90S", g + "_post1", "contact")
        add(g + "-2", "기둥 1 ↔ 하우징", g + "_post1", g + "_housing", "contact")
        add(g + "-3", "서보 스플라인 ↔ 혼 허브", g + "_servo_spline", g + "_horn", "insert", ra=2.4, min=2.0)
        for st, ang in (("닫힘", 60.0), ("열림", -60.0)):
            add(g + "-4" + st, "혼 핀 ↔ 문판 홈 (%s)" % st, g + "_horn", g + "_flap", "slide", pose={key: ang})
            add(g + "-5" + st, "문판 ↔ 하우징 슬롯 (%s)" % st, g + "_flap", g + "_housing", "slide", pose={key: ang})
            add(g + "-6" + st, "혼 ↔ 하우징 (%s)" % st, g + "_horn", g + "_housing", "slide", pose={key: ang})
        add(g + "-7", "하우징 ↔ 마킹실 벽", g + "_housing", "120_chamber_walls", "contact")
    # 펜 들기
    add("Z1", "SG90 귀 ↔ 캐리지 기둥", "205_z_servo_SG90", "206_y_carriage", "contact")
    add("Z2", "SG90 스플라인 ↔ 혼 허브", "205s_z_servo_spline", "205h_z_servo_horn", "insert", ra=2.4, min=2.4)
    add("Z3", "혼 끝 ↔ 홀더 탭 (밂, 혼 30°)", "205h_z_servo_horn", "202_marker_holder_vblock", "push", pose=dict(horn=30.0))
    add("Z4", "혼 ↔ 홀더 (내림 −20°, 안 닿음)", "205h_z_servo_horn", "202_marker_holder_vblock", "slide")
    add("Z5a", "안내 핀 ↔ 홀더 슬리브 (내림)", "223_holder_guide_pins", "202_marker_holder_vblock", "slide")
    add("Z5b", "안내 핀 ↔ 홀더 슬리브 (10 mm 들림)", "223_holder_guide_pins", "202_marker_holder_vblock", "slide", pose=dict(horn=45.6))
    add("Z6", "안내 핀 ↔ 캐리지 (끼움 아래 4 + 위 8)", "223_holder_guide_pins", "206_y_carriage", "insert", ra=1.5, min=23.5)
    add("Z7a", "스프링 204 ↔ 홀더 윗면", "204_holder_spring", "202_marker_holder_vblock", "contact")
    add("Z7b", "스프링 204 ↔ 멈춤 탭", "204_holder_spring", "206_y_carriage", "contact")
    add("Z8a", "마커 ↔ V홈 홀더", "201_marker", "202_marker_holder_vblock", "contact")
    add("Z8b", "마커 ↔ 조임 띠", "201_marker", "203_clamp_strap", "contact")
    add("Z8c", "조임 띠 ↔ 홀더 (M2 나사)", "203_clamp_strap", "202_marker_holder_vblock", "contact")
    add("Z9", "대기: 마커 원뿔 ↔ 캡 컵", "201_marker", "219_cap_cup", "contact")
    # Y 축
    add("Y1", "Y 너트 ↔ 캐리지 (M3 ×4)", "224_y_nut_T8", "206_y_carriage", "screw",
        p=V(ns["XB0"] + 5.657, -40 + 15, XY["yscrew_z"] + 5.657), d=V(0, 1, 0), r=1.4, L=8)
    for (xm, ym) in ((65, -40), (65, 18)):
        add("Y2@%d" % ym, "Y 나사 ↔ Y 너트 (ym %d)" % ym, "208_y_lead_screw_T8", "224_y_nut_T8", "insert", pose=dict(xm=xm, ym=ym), ra=4.0, min=14.9)
    add("Y3", "LM6UU ↔ 캐리지 구멍", "221_y_bearings_LM6UU", "206_y_carriage", "contact")
    add("Y4", "Y 봉 ↔ LM6UU (끼워 지나감)", "207_y_rods", "221_y_bearings_LM6UU", "insert", ra=3.0, min=37.9)
    add("Y5", "Y 봉 ↔ 끝 블록 (양쪽 10 mm씩)", "207_y_rods", "212_beam_end_blocks", "insert", ra=3.0, min=39.9)
    add("Y6", "Y 모터 축 ↔ 커플링", "209r_y_motor_shaft", "210_y_coupling", "insert", sec=14.04, min=6.0)
    add("Y7", "Y 나사 ↔ 커플링", "208_y_lead_screw_T8", "210_y_coupling", "insert", ra=4.0, min=10.0)
    for sx in (-1, 1):
        add("Y8%s" % ("a" if sx < 0 else "b"), "Y 모터 귀 ↔ 모터 브래킷 (M4)", "209_y_stepper_28BYJ48", "211_y_motor_bracket", "screw",
            p=V(ns["XB0"] + sx * M28["ear_c"] / 2, -74 - 26.9 - 3, XY["yscrew_z"] + M28["off"]), d=V(0, 1, 0), r=1.9, L=8)
    add("Y9", "Y 모터 브래킷 ↔ 끝 블록 A", "211_y_motor_bracket", "212_beam_end_blocks", "contact")
    # X 축
    add("X1", "X 너트 ↔ 끝 블록 A (M3 ×4)", "225_x_nut_T8", "212_beam_end_blocks", "screw",
        p=V(ns["XB0"] - XY["eb_hw"], XY["ya"] + 5.657, XY["xscrew_z"] + 5.657), d=V(1, 0, 0), r=1.4, L=8)
    for xm in (37, 73):
        add("X2@%d" % xm, "X 나사 ↔ X 너트 (xm %d)" % xm, "214_x_lead_screw_T8", "225_x_nut_T8", "insert", pose=dict(xm=xm), ra=4.0, min=14.9)
    add("X3", "LM8UU ↔ 끝 블록 구멍", "222_x_bearings_LM8UU", "212_beam_end_blocks", "contact")
    add("X4", "X 봉 ↔ LM8UU", "213_x_rods", "222_x_bearings_LM8UU", "insert", ra=4.0, min=47.9)
    add("X5", "X 봉 ↔ 봉 받침 (양 끝 12 mm)", "213_x_rods", "218_rod_supports", "insert", ra=4.0, min=47.9)
    add("X6", "봉 받침 ↔ 갠트리 레일", "218_rod_supports", "100_frame", "contact")
    for sy_ in (-1, 1):
        add("X7%s" % ("a" if sy_ < 0 else "b"), "X 모터 귀 ↔ 모터판 217 (M4)", "215_x_stepper_28BYJ48", "217_x_motor_plate", "screw",
            p=V(145, XY["ya"] + sy_ * M28["ear_c"] / 2, XY["xscrew_z"] - M28["off"]), d=V(1, 0, 0), r=1.9, L=8)
    add("X8", "모터판 217 ↔ 갠트리 레일 (아래 면)", "217_x_motor_plate", "100_frame", "contact")
    add("X9", "X 모터 축 ↔ 커플링", "215r_x_motor_shaft", "216_x_coupling", "insert", sec=14.04, min=6.0)
    add("X10", "X 나사 ↔ 커플링", "214_x_lead_screw_T8", "216_x_coupling", "insert", ra=4.0, min=10.0)
    add("C1", "캡 컵 ↔ 컵 받침", "219_cap_cup", "220_cup_bracket", "contact")
    add("C2", "컵 받침 ↔ 마킹실 벽", "220_cup_bracket", "120_chamber_walls", "contact")
    return JL


def static_checks(S):
    names = sorted(n for n in S if not n.startswith("REF"))
    over, touch = [], {n: [] for n in names}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            A, B = S[a].BoundBox, S[b].BoundBox
            if not A.intersect(B):
                continue
            d = S[a].distToShape(S[b])[0]
            if d < TOL:
                v = S[a].common(S[b]).Volume
                if v > 0.05:
                    over.append((a, b, round(v, 2)))
                touch[a].append(b)
                touch[b].append(a)
    seen, stack = {"100_frame"}, ["100_frame"]
    while stack:
        n = stack.pop()
        for m in touch[n]:
            if m not in seen:
                seen.add(m)
                stack.append(m)
    return dict(overlap=over, floating=[n for n in names if not touch[n]], not_connected=[n for n in names if n not in seen])


def sweep(ns, P, M, poses, moving_kinds=None):
    """자세마다 움직이는 부품 ↔ 나머지 겹침"""
    res = []
    mk = moving_kinds or {"floor", "rot_floor", "beam", "rot_x", "rot_y", "carriage", "holder", "pen_horn", "gate_flap", "gate_horn", "spring"}
    allow = set(tuple(sorted(x)) for x in ns.get("ALLOW_SWEEP", []))
    for label, Jd in poses:
        J = dict(ns["JOINT0"])
        J.update(Jd)
        S = ns["posed"](P, M, J)
        names = [n for n in S if not n.startswith("REF")]
        mov = [n for n in names if M[n][0] in mk]
        hits = []
        for a in mov:
            for b in names:
                if a == b or (b in mov and b < a):
                    continue
                if tuple(sorted((a, b))) in allow:
                    continue
                v = overlap(S[a], S[b])
                if v > 0.05:
                    hits.append((a, b, round(v, 2)))
        res.append(dict(pose=label, J={k: J[k] for k in Jd}, collisions=hits))
    return res


def run(ns, P, M, poses=None):
    out = {}
    S0 = ns["posed"](P, M, ns["JOINT0"])
    out["static"] = static_checks(S0)
    jr = []
    for j in joints(ns, P, M):
        J = dict(ns["JOINT0"])
        J.update(j["pose"])
        S = ns["posed"](P, M, J) if j["pose"] else S0
        try:
            jr.append(check_joint(j, S))
        except Exception as e:
            jr.append(dict(id=j["id"], desc=j["desc"], ok=False, error=str(e)))
    out["joints"] = jr
    if poses:
        out["sweep"] = sweep(ns, P, M, poses)
    return out
