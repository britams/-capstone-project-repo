# -*- coding: utf-8 -*-
"""S4 역학계산 2차 — D5e(움직이는 모델) 기준으로 M1~M6 다시 계산 (승준이 서현 CAP-AI-20 '남은 일 2번'을 이어서, CAP-AI-SJ-29)

실행: python3 design/calc/s4_calc_d5e_sj.py → 화면 + design/calc/s4_results_d5e_sj.json
서현 r2 스크립트(s4_calc.py)의 식(screw_torque, jam_solve, beam_point_load)을 그대로 불러 씀 — 교재·해설집 대조를 통과한 함수.
서현 파일은 고치지 않음 (CLAUDE.md 파일 규칙). 바뀐 것은 이 파일과 결과 json, 그림 스크립트 s4_fbd_module_sj.py.

질량·무게중심: 승준 PC FreeCAD 1.x에서 cad/D5e_module_kinematic.py의 build() + posed()로 읽은 부품별 부피·무게중심
               → design/calc/d5e_mass_cad_sj.json (자세 rest·mark·lift·xmin·ymin)
밀도: PLA 1.24(꽉 찬 값 = 상한) · 강 7.85 · 알루미늄 2.7 · 황동 8.5 g/cm³. 구매품은 사양 질량(마커 13, SG90 9, 28BYJ-48 37, LM8UU 15, LM6UU 8 g).

D5e에서 계산이 바뀌는 곳 (서현 로그 CAP-AI-20 남은 일 2번 + 승준이 찾은 것)
  M1  T8 플랜지 너트(황동) 추가로 바닥 묶음 질량 증가 / 안내봉 회전 막이 F_g = T/26 (서현) /
      [승준 추가] 나사(y −13)와 밀대(y 0)가 13 mm 어긋나 캐리지가 기울려 함 → 안내봉이 캐리지 두께 12 mm로 짝힘을 받음 (서랍 꼴)
  M2  Y 봉 z 438·468 (간격 30 그대로), D5e 질량 / X는 끼임 연립 그대로
  M3  홀더 안내가 레일 → 핀 2개(Ø3, 슬리브 40)로 → 핀 마찰은 편심 모멘트 / 슬리브 길이로
  M4  혼 팔 = 14 cos θ (혼 끝 둥근 면이 평평한 탭을 밂, 서현 11/01) + 혼–탭 미끄럼 마찰 + 핀 서랍 효과 2μ(e/h) + 스프링 늘어남
  M5  X 빔 판정은 같음(기하 같음) + 펜 홀더 핀 안내의 끼임 한계
  M6  X 봉 길이 163 (받침 사이, 서현), D5e 질량
단위: N, mm, s (토크 N·mm = mN·m)
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import s4_calc as base                       # noqa: E402  서현 r2
from s4_calc import screw_torque, jam_solve, beam_point_load   # noqa: E402

g = 9.81
P = dict(base.PARAM)
P.update(
    rho_brass=8.5e-3,                         # 황동 T8 너트 [가능성 높음]
    L_xrod=163.0,                             # X 봉 길이 = 받침 사이 최대 (서현 CAP-AI-20) — 받침 중심 간 151보다 길게 = 보수적
    yrod_z=(438.0, 468.0),                    # D5e Y 봉 높이 (끝 블록에 10 mm 끼우며 내림)
    # ---- 펜 홀더 안내 (D5e) ----
    mu_pin=0.30,                              # Ø3 강 핀 – PLA 슬리브 구멍 (PLA–강, s4_calc mu_pla와 같음) [가능성 높음]
    mu_pin_range=(0.2, 0.4),                  # 감도
    h_sleeve=40.0,                            # 슬리브 길이 = 짝힘 팔
    mu_horn=0.30,                             # 혼(나일론·PLA) 끝 – PLA 탭 미끄럼 [가능성 높음]
    k_spring=0.036, Fs_mark_max=0.18,         # 204: 승준 ME2 적용 (피아노선 Ø0.25, 코일 Ø6, 5 mm 눌림에 0.18 N) — 스프링 넣을 때
    lift_max=10.0,                            # 펜 들림 (혼 45.6° = 14 sin θ)
    # ---- 바닥 캐리지 (D5e) ----
    y_screw=-13.0, y_guide=13.0, y_push=0.0,  # 바닥 나사 · 안내봉 · 밀대(로드셀) y
    L_carriage=12.0,                          # 캐리지 두께 = 안내봉이 끼인 길이
    mu_guide=0.30,                            # Ø4 강 안내봉 – PLA 캐리지 구멍 [가능성 높음]
)

CAD = json.load(open(os.path.join(HERE, "d5e_mass_cad_sj.json"), encoding="utf-8"))
C = CAD["consts"]
MAT = {"140_lift_floor": "pla", "158_carriage": "pla", "159_floor_nut_T8": "brass", "148_load_cell": "al",
       "146_spring": "steel", "147_push_rod": "steel",
       "202_marker_holder_vblock": "pla", "203_clamp_strap": "pla", "204_holder_spring": "steel",
       "206_y_carriage": "pla", "223_holder_guide_pins": "steel", "205h_z_servo_horn": "pla", "224_y_nut_T8": "brass",
       "207_y_rods": "steel", "212_beam_end_blocks": "pla", "225_x_nut_T8": "brass", "211_y_motor_bracket": "pla",
       "210_y_coupling": "al", "208_y_lead_screw_T8": "steel"}
SPEC = {"201_marker": P["m_marker"], "205_z_servo_SG90": P["m_sg90"], "209_y_stepper_28BYJ48": P["m_28byj"],
        "221_y_bearings_LM6UU": 2 * P["m_lm6uu"], "222_x_bearings_LM8UU": 2 * P["m_lm8uu"]}
SKIP = {"205s_z_servo_spline", "209r_y_motor_shaft"}     # 구매품 사양 질량에 들어 있음
GROUP = {"floor": ["140_lift_floor", "158_carriage", "159_floor_nut_T8", "148_load_cell", "146_spring", "147_push_rod"],
         "floor_upper": ["140_lift_floor", "148_load_cell", "146_spring", "147_push_rod"],   # 캐리지 위에 얹힌 것 (로드셀 축 y 0)
         "floor_carriage": ["158_carriage", "159_floor_nut_T8"],
         "z": ["201_marker", "202_marker_holder_vblock", "203_clamp_strap"]}
GROUP["y"] = GROUP["z"] + ["204_holder_spring", "205_z_servo_SG90", "205h_z_servo_horn", "206_y_carriage",
                           "223_holder_guide_pins", "221_y_bearings_LM6UU", "224_y_nut_T8"]
GROUP["x"] = GROUP["y"] + ["207_y_rods", "208_y_lead_screw_T8", "209_y_stepper_28BYJ48", "210_y_coupling",
                           "211_y_motor_bracket", "212_beam_end_blocks", "222_x_bearings_LM8UU", "225_x_nut_T8"]


def parts(state="mark"):
    out = {}
    for n, (vol, x, y, z, *_r) in CAD[state].items():
        if n in SKIP:
            continue
        m = SPEC[n] if n in SPEC else vol * P["rho_" + MAT[n]] * 1000      # g
        out[n] = (m, x, y, z)
    return out


def group(name, state="mark"):
    pts = parts(state)
    ks = GROUP[name]
    m = sum(pts[k][0] for k in ks)
    cg = tuple(sum(pts[k][0] * pts[k][i] for k in ks) / m for i in (1, 2, 3))
    return m, cg


def geom(state="mark"):
    """D5e 치수에서 펜 홀더 주변 점 (cad/D5e_module_kinematic.py 식 그대로)"""
    xm = CAD[state]["201_marker"][1]
    ym = CAD[state]["201_marker"][2]
    R = C["MK"]["R"]
    xb = xm + R * math.sqrt(2) + 16                      # 빔·캐리지 중심 = Y 봉 x
    xhb = xb - 10                                        # 캐리지 면
    x_pin = xhb - 4.0                                    # 안내 핀 x
    x_ct = (xm + 9) + 1.0 + C["HORN"]["gap"] + 4.0 + 4.0     # SG90 출력축 원점 x (boss_h 4)
    x_F = x_ct - (4.0 + C["HORN"]["gap"]) - (4.0 - C["HORN"]["t"] / 2)   # 혼 팔 두께 가운데 = 탭을 미는 x
    y_axis = ym + 21.1                                   # 펜 서보 축 y
    x_s = xm + C["MK"]["R_max"] + 0.6 + 3.2              # 스프링 204 x
    z_mid = C["HZ0"] + C["PIN"]["sleeve_h"] / 2          # 슬리브 가운데 높이 (대기 기준)
    dz_tab = C["TAB_Z"] - z_mid                          # 탭 아래 면 − 슬리브 가운데
    return dict(xm=xm, ym=ym, xb=xb, xhb=xhb, x_pin=x_pin, x_F=x_F, y_axis=y_axis, x_s=x_s, dz_tab=dz_tab,
                pin_dy=C["PIN"]["dy"], Rt=C["HORN"]["Rt"], rr=C["HORN"]["rr"])


# ---------------------------------------------------------------- M1
def M1_floor(state="mark"):
    """바닥 승강 나사. 캐리지 자유물체: 아래에서 너트 추력 F_n(나사 축 y −13), 위에서 로드셀이 받는 F_up = W_upper + F_p (y 0),
       캐리지·너트 무게, 안내봉(y +13) 반력: ① 회전 막이 F_g = T/26 (서현) ② 기울어짐 짝힘 N_p = M/L_c (승준) → 마찰은 아래로"""
    m_up, cg_up = group("floor_upper", state)
    m_c, cg_c = group("floor_carriage", state)
    W_up, W_c = m_up / 1000 * g, m_c / 1000 * g
    F_up = W_up + P["F_press"]
    k_T = screw_torque(1.0, P["mu_screw"])["T_Nmm"]     # T = k_T × F (힘 1 N당 토크)
    s_g = P["y_guide"] - P["y_screw"]                    # 26
    M_tilt = F_up * (P["y_push"] - P["y_screw"]) + W_c * (cg_c[1] - P["y_screw"])   # 나사 축에 대한 기울임 모멘트
    N_p = M_tilt / P["L_carriage"]
    out = {}
    for name, mg, tilt in (("서현 r2와 같은 식 (안내봉 마찰 없음)", 0.0, False),
                           ("회전 막이만 (F_g = T/26)", P["mu_guide"], False),
                           ("회전 막이 + 기울어짐 짝힘 (보수적)", P["mu_guide"], True)):
        F_fric_tilt = 2 * mg * N_p if tilt else 0.0
        F_n = (F_up + W_c + F_fric_tilt) / (1 - mg * k_T / s_g)
        r = screw_torque(F_n, P["mu_screw"])
        F_g = r["T_Nmm"] / s_g
        r.update(F_up=F_up, W_c=W_c, F_g=F_g, N_p=N_p if tilt else 0.0, F_fric=F_n - F_up - W_c,
                 SF=P["T_motor_Nmm"] / r["T_Nmm"])
        out[name] = r
    W_all = (m_up + m_c) / 1000 * g
    off = screw_torque(W_all, P["mu_screw"])             # 전원 꺼짐: F_p 없음, 무게만
    out["_mass"] = dict(m_upper=m_up, m_carriage=m_c, m_total=m_up + m_c, W_total=W_all, cg_carriage=cg_c,
                        k_T=k_T, M_tilt=M_tilt, tilt_fric_ratio=2 * P["mu_guide"] * (P["y_push"] - P["y_screw"]) / P["L_carriage"],
                        TL_power_off=off["TL_Nmm"])
    # 기울어짐 짝힘은 하중(F_up·13)에서 생기고 추력(나사 축)에서는 안 생김 → 마찰이 추력을 키우지 않아 끼임은 없음 (마찰만 늚)
    return out


# ---------------------------------------------------------------- 홀더 핀 안내 (M3·M4·M5-b)
# 원점 = 두 안내 핀 사이 가운데 (x_pin, ym), 높이 = 슬리브 가운데. 핀은 세로라 세로 힘은 마찰로만 받고,
# 모멘트는 슬리브 위·아래 끝의 가로 접촉력 짝힘(팔 h = 40)으로 받음 → 접촉력 크기 합 ΣN ≈ 2(|M_x| + |M_y|)/h (보수)
def M4_servo(Fs0=0.0, k=0.0, mu_p=None, mu_h=None, n=92, state="mark"):
    """펜 들기: 혼 θ 0 → 45.6° (들림 0 → 10 mm). 미지수 F(혼이 탭을 미는 힘). 각 θ에서
       ΣF_z: F − W − F_s − f = 0,  f = μ_p ΣN,  ΣN = 2(|M_x| + |M_y|)/h + μ_h F  (보수: 두 모멘트 크기 합)
       T = F (14 cos θ + μ_h (14 sin θ + 2))   — 마찰력 μ_h F의 팔 = 축에서 접촉점까지 높이"""
    mu_p = P["mu_pin"] if mu_p is None else mu_p
    mu_h = P["mu_horn"] if mu_h is None else mu_h
    G = geom(state)
    mz, cg = group("z", state)
    W = mz / 1000 * g
    h = P["h_sleeve"]
    xG, yG = cg[0] - G["x_pin"], cg[1] - G["ym"]
    xF, xs = G["x_F"] - G["x_pin"], G["x_s"] - G["x_pin"]
    e_max = G["y_axis"] + G["Rt"] - G["ym"]              # θ = 0일 때 가장 멂 (35.1)
    coef = mu_p * (2 * (e_max + abs(xF) + abs(G["dz_tab"]) * mu_h) / h + mu_h)
    mu_c = 1 / (2 * (e_max + abs(xF) + abs(G["dz_tab"]) * mu_h) / h + mu_h)
    base_out = dict(W_h=W, cg=cg, xG=xG, yG=yG, xF=xF, xs=xs, dz_tab=G["dz_tab"], mu_p=mu_p, mu_h=mu_h, Fs0=Fs0, k=k,
                    jam_coef=coef, mu_c_pin=mu_c)
    if coef >= 1:                                        # F에 붙는 마찰 계수가 1 이상 → 아무리 밀어도 안 올라감
        base_out.update(jam=True, T_max=float("inf"), SF=0.0, note="끼임 — 핀 서랍 효과 (μ_pin ≥ μ_c)")
        return base_out
    rows = []
    for i in range(n):
        th = math.radians(45.6 * i / (n - 1))
        lift = G["Rt"] * math.sin(th)
        Fs = Fs0 + k * lift
        yF = G["y_axis"] + G["Rt"] * math.cos(th) - G["ym"]
        F = W + Fs
        for _ in range(100):
            # M_x = Σ(y F_z − z F_y): 혼 힘 F(y = e_y), 무게 W(y = yG), 탭 마찰 F_y = −μ_h F (z = dz_tab)
            Mx = yF * F - yG * W + G["dz_tab"] * mu_h * F
            # M_y = Σ(−x F_z): 혼 힘(x_F), 무게(x_G), 스프링(x_s, 아래로)
            My = -(xF * F) + xG * W + xs * Fs
            SN = 2 * (abs(Mx) + abs(My)) / h + mu_h * F
            F_new = W + Fs + mu_p * SN
            if abs(F_new - F) < 1e-12:
                break
            F = F_new
        SN_vec = 2 * math.hypot(Mx, My) / h + mu_h * F
        arm = G["Rt"] * math.cos(th) + mu_h * (G["Rt"] * math.sin(th) + G["rr"])
        rows.append(dict(theta=math.degrees(th), lift=lift, Fs=Fs, e_y=yF, F=F, f=mu_p * SN, SN=SN, SN_vec=SN_vec,
                         Mx=Mx, My=My, arm=arm, T=F * arm, T_ideal=(W + Fs) * G["Rt"] * math.cos(th)))
    worst = max(rows, key=lambda r: r["T"])
    # 벡터 합(접점 하나의 x·y 성분을 합친 크기) 기준 F — 덜 보수적인 값 (참고)
    F_vec = max(W + r["Fs"] + mu_p * r["SN_vec"] for r in rows)
    base_out.update(jam=False, worst=worst, first=rows[0], last=rows[-1], T_max=worst["T"], SF=P["T_servo_Nmm"] / worst["T"],
                    F_vec_ref=F_vec, rows=rows[::7] + [rows[-1]])
    return base_out


def M3_dab(Fs=0.0, mu_p=None, state="mark"):
    """찍을 때: 혼은 탭에서 떨어짐(θ −20°). 홀더가 말벌 등에 앉아 멈춤 → 핀 마찰 f는 위쪽(0 ~ f_max, 정지 마찰)
       N_tip = W + F_s − f,  f_max = μ_p · 2(|M_x| + |M_y|)/h,  팁은 (xm, ym) — 핀 줄에서 x로 −12.4 mm"""
    mu_p = P["mu_pin"] if mu_p is None else mu_p
    G = geom(state)
    mz, cg = group("z", state)
    W = mz / 1000 * g
    xG, yG = cg[0] - G["x_pin"], cg[1] - G["ym"]
    xT = G["xm"] - G["x_pin"]
    xs = G["x_s"] - G["x_pin"]
    N = W + Fs
    for _ in range(100):
        Mx = -yG * W
        My = -(xT * N) + xG * W + xs * Fs
        fmax = mu_p * 2 * (abs(Mx) + abs(My)) / P["h_sleeve"]
        N_new = W + Fs - fmax
        if abs(N_new - N) < 1e-12:
            break
        N = N_new
    return dict(W_h=W, Fs=Fs, xT=xT, xG=xG, f_max=fmax, N_tip_range=(N, W + Fs), Mx=Mx, My=My,
                hornet_stays=W + Fs <= P["F_press"], Fs_max=P["F_press"] - W, ink_ok=N >= P["F_ink_min"],
                rail_r2=dict(f_max=0.0888, N_tip_range=(0.2326, 0.3214)))


# ---------------------------------------------------------------- M2
def eccentric(state="mark"):
    my, cg = group("y", state)
    xb = geom(state)["xb"]
    e = cg[0] - xb
    M = my / 1000 * g * abs(e)
    s_y = P["yrod_z"][1] - P["yrod_z"][0]
    return dict(m_y=my, cg=cg, xb=xb, cg_x_minus_xb=e, M=M, H=M / s_y, s_y=s_y)


def M2_axes(state="mark"):
    out = {}
    ec = eccentric(state)
    my = ec["m_y"]
    for name, mu in (("Y (볼 부싱)", P["mu_ball"]), ("Y (PLA 부싱, 참고)", P["mu_pla"])):
        W = my / 1000 * g
        N_sum = W + 2 * ec["H"]
        Fi = my / 1000 * P["a_start"]
        F = mu * N_sum + Fi
        r = screw_torque(F, P["mu_screw"])
        r.update(W=W, H=ec["H"], N_sum=N_sum, F_fric=mu * N_sum, F_inertia=Fi, SF=P["T_motor_Nmm"] / r["T_Nmm"])
        out[name] = r
    mx, cgx = group("x", state)
    W = mx / 1000 * g
    W_B = W * (cgx[1] - P["ya"]) / (P["yb"] - P["ya"])
    for name, mu in (("X (볼 부싱)", P["mu_ball"]), ("X (PLA 부싱, 참고)", P["mu_pla"])):
        js = jam_solve(mu, W, W_B, mx / 1000, P["a_start"], P["L_lm8uu"], P["yb"] - P["ya"], P["z_xrod"] - P["z_xscrew"],
                       M_w=ec["M"], e_y=cgx[1] - P["ya"], k=1.0)
        if js["jam"]:
            out[name] = dict(jam=True, note="끼임 — 어떤 추력으로도 안 움직임 (M5)")
            continue
        r = screw_torque(js["P"], P["mu_screw"])
        r.update(W=W, W_B=W_B, Qp=js["Qp"], Qy=js["Qy"], SF=P["T_motor_Nmm"] / r["T_Nmm"], jam=False)
        out[name] = r
    out["eccentric"] = ec
    out["m_x"], out["cg_x"] = mx, cgx
    return out


# ---------------------------------------------------------------- M5 (X 빔: 서현 r2 함수 그대로 — 기하 같음)
def M5_jam():
    r = base.M5_jam()
    return r


# ---------------------------------------------------------------- M6
def M6_rods(state):
    out = {}
    mx, cgx = group("x", state)
    Wx = mx / 1000 * g
    R_A = Wx * (P["yb"] - cgx[1]) / (P["yb"] - P["ya"])
    R_B = Wx - R_A
    I8, S8 = math.pi * P["d_xrod"] ** 4 / 64, math.pi * P["d_xrod"] ** 3 / 32
    for name, F in (("X 봉 A (무게중심 배분)", R_A), ("X 봉 B (무게중심 배분)", R_B), ("X 봉 한 개가 전부 (최악)", Wx)):
        b = beam_point_load(F, P["L_xrod"], P["E_steel"], I8)
        out[name] = dict(F=F, delta=b["delta_max"], M=b["M_max"], sigma=b["M_max"] / S8, V=F / 2)
    ec = eccentric(state)
    Wy = ec["m_y"] / 1000 * g
    I6, S6 = math.pi * P["d_yrod"] ** 4 / 64, math.pi * P["d_yrod"] ** 3 / 32
    for name, Fv in (("Y 봉 (세로 반씩 + 수평 짝힘)", Wy / 2), ("Y 봉 한 개가 세로 전부 + 수평 짝힘 (최악)", Wy)):
        F = math.hypot(Fv, ec["H"])
        b = beam_point_load(F, P["L_yrod"], P["E_steel"], I6)
        out[name] = dict(F=F, F_vert=Fv, H=ec["H"], delta=b["delta_max"], M=b["M_max"], sigma=b["M_max"] / S6, V=F / 2)
    out["_beam"] = dict(m_g=mx, cg=cgx, R_A_share=R_A / Wx, Wx=Wx)
    return out


def run():
    R = {}
    R["mass_g"] = {k: group(k)[0] for k in ("floor", "z", "y", "x")}
    R["cg_mark"] = {k: group(k)[1] for k in ("floor", "z", "y", "x")}
    R["cg_rest"] = {k: group(k, "rest")[1] for k in ("floor", "z", "y", "x")}
    R["parts_mark_g"] = {n: round(v[0], 2) for n, v in parts("mark").items()}
    R["geom_mark"] = geom("mark")
    R["M1"] = M1_floor()
    R["M2"] = M2_axes()
    W_h = group("z")[0] / 1000 * g
    Fs_max = P["F_press"] - W_h                          # 말벌이 격자에 붙어 있을 스프링 상한 (D5e 홀더 무게로 0.177)
    R["M3"] = {"스프링 없음": M3_dab(0.0), "스프링 최대 (F_p − W_h)": M3_dab(Fs_max),
               "스프링 0.18 N (ME2 값 그대로)": M3_dab(P["Fs_mark_max"])}
    R["M4"] = {"스프링 없음": M4_servo(0.0, 0.0),
               "스프링 최대 + k 0.036 (10 mm 들면 +0.36 N)": M4_servo(Fs_max, P["k_spring"])}
    for mu in P["mu_pin_range"]:
        R["M4"]["스프링 없음, μ_pin %.1f" % mu] = M4_servo(0.0, 0.0, mu_p=mu)
        R["M4"]["스프링 최대, μ_pin %.1f" % mu] = M4_servo(Fs_max, P["k_spring"], mu_p=mu)
    R["M4"]["스프링 없음, μ_pin 0.5"] = M4_servo(0.0, 0.0, mu_p=0.5)
    R["M5"] = M5_jam()
    R["M5_holder_pins"] = {k: dict(mu_c_pin=v["mu_c_pin"], jam_coef=v["jam_coef"], mu_p=v["mu_p"]) for k, v in R["M4"].items()}
    R["M6"] = {"mark": M6_rods("mark"), "rest": M6_rods("rest")}
    R["r2_D5d"] = json.load(open(os.path.join(HERE, "s4_results.json"), encoding="utf-8"))   # 비교용 (서현 r2)
    return R


def _fmt(o):
    if isinstance(o, float):
        return round(o, 4)
    if isinstance(o, dict):
        return {k: _fmt(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_fmt(v) for v in o]
    return o


if __name__ == "__main__":
    R = run()
    out = {k: v for k, v in R.items() if k != "r2_D5d"}
    json.dump(_fmt(out), open(os.path.join(HERE, "s4_results_d5e_sj.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    show = _fmt(out)
    for k in ("M4", ):
        for kk in show[k]:
            show[k][kk].pop("rows", None)
    print(json.dumps(show, ensure_ascii=False, indent=1))
