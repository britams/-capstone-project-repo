# -*- coding: utf-8 -*-
"""S4 동역학 추가 계산 M7~M10 (D5e 기준) + 교재 유제 해설집 대조 — CAP-AI-21 (서현, 2026-11-02 발표용)
실행: python3 design/calc/s4_dyn_calc.py → design/calc/s4_dyn_results.json
유제: Meriam·Kraige·Bolton Dynamics 9판 SI 5/26(스카치 요크), 3/108(낙하 질량 + 미리 눌린 스프링), 2/27(가속·속도 제한 최소 시간), 8/8(정적 처짐 → 고유진동수)
해설집(미국판, 문제별 PDF) 값은 서현 PC Documents\\공주대\\동역학 — 레포에 안 올림. 이 파일에는 문제 번호와 주어진 수치만.
D5e 값: cad/D5e_module_kinematic.py(GATE·HORN·PIN), 승준 design/calc/s4_results_d5e_sj.json(질량·처짐, CAP-AI-SJ-29)
"""
import json
import math
import os

g = 9.81
HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------- 교재 유제 (해설집 대조) ----------------
def tb_5_26(r, d, th, w, al):
    """스카치 요크: s = r cos θ + d → v = −rω sin θ, a = −rα sin θ − rω² cos θ (해설집 식)"""
    return dict(s=r * math.cos(th) + d, v=-r * w * math.sin(th), a=-r * al * math.sin(th) - r * w ** 2 * math.cos(th))


def tb_3_108(m=6.0, h=0.100, x0=0.050, k=4000.0):
    """낙하 거리 h 뒤 미리 x0 눌린 스프링을 δ 더 누름: m g (h + δ) = ∫_{x0}^{x0+δ} k x dx"""
    W = m * g
    # (k/2) δ² + (k x0 − W) δ − W h = 0
    A, B, C = k / 2, k * x0 - W, -W * h
    return (-B + math.sqrt(B * B - 4 * A * C)) / (2 * A)


def tb_2_27(D=10000.0, amax=0.6 * g, vmax=400 / 3.6):
    """가속 a, 속도 상한 v, 거리 D의 최소 시간 (사다리꼴). D < v²/a 이면 삼각형"""
    if D >= vmax ** 2 / amax:
        return D / vmax + vmax / amax, "trapezoid"
    return 2 * math.sqrt(D / amax), "triangle"


def tb_8_8(m=30.0, dst=0.050):
    k = m * g / dst
    return k, math.sqrt(k / m) / (2 * math.pi)


def check_textbook():
    # 5/26은 문자 답 → 임의 값에서 위치를 수치 미분해 식과 대조
    r, d, th, w, al, dt = 0.05, 0.2, 0.7, 3.0, 2.0, 1e-5
    def s_of(t):
        return r * math.cos(th + w * t + 0.5 * al * t * t) + d
    v_num = (s_of(dt) - s_of(-dt)) / (2 * dt)
    a_num = (s_of(dt) - 2 * s_of(0) + s_of(-dt)) / dt ** 2
    f = tb_5_26(r, d, th, w, al)
    t227, shape = tb_2_27()
    k88, f88 = tb_8_8()
    return {
        "5/26": dict(manual="v = −rω sin θ, a = −rα sin θ − rω² cos θ", ai_v=f["v"], num_v=v_num, ai_a=f["a"], num_a=a_num,
                     err_v=abs(f["v"] - v_num) / abs(v_num), err_a=abs(f["a"] - a_num) / abs(a_num)),
        "3/108": dict(manual_mm=29.4, ai_mm=tb_3_108() * 1e3),
        "2/27": dict(manual_s=108.9, ai_s=t227, shape=shape),
        "8/8": dict(manual_k=5890, manual_fn=2.23, ai_k=k88, ai_fn=f88),
    }


# ---------------- D5e 입력 ----------------
SJ = json.load(open(os.path.join(HERE, "s4_results_d5e_sj.json"), encoding="utf-8"))
D = dict(
    # 문 (GATE): 혼 핀 반지름 r = 9 mm, 관절 φ +60(닫힘) ~ −60(열림), 문판 y = 9 sin φ
    r_gate=9.0, phi_open=-60.0, phi_closed=60.0,
    m_flap=0.78,              # g, 문판 부피 ≈ 1.5×26.7×14 + 1.5×8×5.3 = 624 mm³ × PLA 1.24 [가능성 높음]
    mu_slot=0.3,              # PLA 문판–PLA 슬롯 [가능성 높음]
    # MG90S (4.8 V): 0.1 s/60°, 정지 토크 2.0 kgf·cm [가능성 높음 — 판매처 사양 1.8~2.2]
    w_mg90s=math.radians(60) / 0.10, T_mg90s=2.0 * 9.81 * 10,
    # SG90 (4.8 V): 0.1 s/60°, 혼 끝 반지름 Rt 14 mm, 말벌 등에 닿는 혼 각 θ_c = asin(0.56/14)
    w_sg90=math.radians(60) / 0.10, Rt=14.0, support=0.56,
    m_holder=33.0,            # g (승준 SJ-29 FreeCAD)
    f_pin=0.0125,             # N, 찍을 때 핀 마찰 상한 (승준 M3)
    F_s_max=0.144,            # N, 스프링 204 권장 상한 (승준: 4 mm 눌림)
    F_p=0.5,                  # N, 바닥이 말벌을 격자에 붙이는 힘 [가정, M3]
    k_c=(300.0, 1000.0, 3000.0),   # N/m, 펠트 팁 + 말벌 흉부 접촉 강성 [추측 — 시험으로 정함]
    # 이송: 28BYJ-48 반 스텝 4096/회전, 10~15 rpm, T8 리드 8 → 1.33~2.0 mm/s, 가속 0.02 m/s² (S4 가정)
    lead=8.0, rpm=(10.0, 15.0), a_xy=20.0, steps_rev=4096,
    dx=28.0, dy=58.0, dz=36.5,        # 대기 → 흉부 최대 이동(mm), 바닥 행정
    lead_belt=40.0,                   # 비교: GT2 20T 풀리 1회전 40 mm
)


# ---------------- M7 문 미닫이 (스카치 요크) ----------------
def M7_gate():
    r = D["r_gate"] * 1e-3
    w = D["w_mg90s"]
    m = D["m_flap"] * 1e-3
    rows = []
    for ph in range(-60, 61, 15):
        p = math.radians(ph)
        th = math.pi / 2 - p                       # 교재 θ = 90° − φ  (s = r cos θ = r sin φ)
        k = tb_5_26(r, 0.0, th, w, 0.0)
        F_in = m * abs(k["a"])                      # 관성력
        F_fr = D["mu_slot"] * m * g                 # 슬롯 마찰
        T_need = (F_in + F_fr) * r * abs(math.cos(p)) * 1e3     # N·mm, 혼 핀에서 문판 방향 힘의 팔 = r cos φ
        F_close = D["T_mg90s"] / (D["r_gate"] * max(abs(math.cos(p)), 1e-6))   # 서보 최대 토크가 문판 방향으로 낼 수 있는 힘 N
        rows.append(dict(phi=ph, y_mm=r * math.sin(p) * 1e3, v_mms=k["v"] * 1e3, a_ms2=k["a"], F_inertia_N=F_in,
                         F_fric_N=F_fr, T_need_Nmm=T_need, F_close_max_N=F_close))
    t_close = math.radians(D["phi_closed"] - D["phi_open"]) / w
    return dict(rows=rows, v_max_mms=r * w * 1e3, a_max_ms2=r * w ** 2 * math.sin(math.radians(60)), t_close_s=t_close,
                stroke_mm=2 * D["r_gate"] * math.sin(math.radians(60)), T_need_max_Nmm=max(x["T_need_Nmm"] for x in rows),
                SF_torque=D["T_mg90s"] / max(x["T_need_Nmm"] for x in rows),
                F_close_mid_N=D["T_mg90s"] / D["r_gate"], F_close_end_N=D["T_mg90s"] / (D["r_gate"] * math.cos(math.radians(60))))


# ---------------- M8 펜 내려찍기 충격 (일-에너지) ----------------
def M8_impact():
    m = D["m_holder"] * 1e-3
    W = m * g
    th_c = math.asin(D["support"] / D["Rt"])
    out = []
    for F_s in (0.0, D["F_s_max"]):
        Wp = W + F_s - D["f_pin"]                   # 아래로 미는 순힘 (마찰은 위로 — 보수적으로 f를 빼면 작아지므로 하한; 상한은 f = 0)
        Wp_hi = W + F_s
        for k in D["k_c"]:
            v_full = D["Rt"] * 1e-3 * D["w_sg90"] * math.cos(th_c)
            Fmax_full = Wp_hi + v_full * math.sqrt(k * m)
            v_allow = (D["F_p"] - Wp_hi) / math.sqrt(k * m) if D["F_p"] > Wp_hi else 0.0
            w_allow = v_allow / (D["Rt"] * 1e-3 * math.cos(th_c))
            out.append(dict(F_s=F_s, k=k, W_net=Wp_hi, v_full_mms=v_full * 1e3, F_max_full_N=Fmax_full,
                            ratio=Fmax_full / Wp_hi, v_allow_mms=v_allow * 1e3, w_allow_dps=math.degrees(w_allow),
                            f_contact_Hz=math.sqrt(k / m) / (2 * math.pi)))
    # 권장: 마지막 2 mm를 60°/s 로 → 시간
    v60 = D["Rt"] * 1e-3 * math.radians(60)
    return dict(rows=out, theta_contact_deg=math.degrees(th_c), W_N=W,
                rec_dps=60.0, rec_v_mms=v60 * 1e3, t_slow_2mm_s=0.002 / v60,
                F_max_rec=[dict(k=k, F_s=F_s, F=W + F_s + v60 * math.sqrt(k * m)) for F_s in (0.0, D["F_s_max"]) for k in D["k_c"]])


# ---------------- M9 이송 시간 (사다리꼴) ----------------
def move_time(dist, v, a):
    if dist >= v * v / a:
        return dist / v + v / a
    return 2 * math.sqrt(dist / a)


def M9_time():
    rows = []
    for rpm in D["rpm"]:
        v = D["lead"] * rpm / 60.0            # mm/s
        f_step = rpm / 60.0 * D["steps_rev"]
        tx, ty, tz = (move_time(d_, v, D["a_xy"]) for d_ in (D["dx"], D["dy"], D["dz"]))
        rows.append(dict(rpm=rpm, v_mms=v, f_step_Hz=f_step, t_x=tx, t_y=ty, t_xy=max(tx, ty), t_z=tz,
                         accel_share=(v / D["a_xy"]) / ty))
    vb = D["lead_belt"] * 15 / 60
    belt = dict(v_mms=vb, t_y=move_time(D["dy"], vb, 200.0))
    return dict(rows=rows, belt=belt)


# ---------------- M10 고유진동수와 스텝 공진 ----------------
def M10_vib():
    m6 = SJ.get("M6", {})
    d_rest = 0.0072e-3
    d_worst = 0.0100e-3
    try:                                           # 승준 SJ-29 결과 (mm)
        d_rest = m6["rest"]["X 봉 A (무게중심 배분)"]["delta"] * 1e-3
        d_worst = m6["mark"]["X 봉 한 개가 전부 (최악)"]["delta"] * 1e-3
    except (KeyError, TypeError):
        pass
    fn = lambda dst: math.sqrt(g / dst) / (2 * math.pi)
    out = dict(delta_rest_mm=d_rest * 1e3, delta_worst_mm=d_worst * 1e3, fn_rest=fn(d_rest), fn_worst=fn(d_worst),
               fn_yrod=fn(0.0026e-3))
    band = (min(out["fn_rest"], out["fn_worst"]) * 0.9, max(out["fn_rest"], out["fn_worst"]) * 1.1)
    out["band_Hz"] = band
    out["band_rpm"] = tuple(f * 60 / D["steps_rev"] for f in band)
    out["f_step_10_15"] = tuple(r / 60 * D["steps_rev"] for r in D["rpm"])
    out["f_step_1p8rpm"] = 120.0
    out["holder_on_contact_Hz"] = {k: math.sqrt(k / (D["m_holder"] * 1e-3)) / (2 * math.pi) for k in D["k_c"]}
    return out


if __name__ == "__main__":
    R = dict(textbook=check_textbook(), D=D, M7=M7_gate(), M8=M8_impact(), M9=M9_time(), M10=M10_vib())
    json.dump(R, open(os.path.join(HERE, "s4_dyn_results.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
    tb = R["textbook"]
    print("5/26 err v %.2e a %.2e" % (tb["5/26"]["err_v"], tb["5/26"]["err_a"]))
    print("3/108 %.2f mm (해설집 29.4)" % tb["3/108"]["ai_mm"])
    print("2/27 %.1f s %s (해설집 108.9)" % (tb["2/27"]["ai_s"], tb["2/27"]["shape"]))
    print("8/8 k %.0f fn %.3f (해설집 5890, 2.23)" % (tb["8/8"]["ai_k"], tb["8/8"]["ai_fn"]))
    m7 = R["M7"]
    print("M7 vmax %.1f mm/s amax %.3f t %.3f s stroke %.2f Tneed %.4f SF %.0f Fclose mid %.1f end %.1f" % (
        m7["v_max_mms"], m7["a_max_ms2"], m7["t_close_s"], m7["stroke_mm"], m7["T_need_max_Nmm"], m7["SF_torque"], m7["F_close_mid_N"], m7["F_close_end_N"]))
    m8 = R["M8"]
    print("M8 th_c %.2f W %.3f" % (m8["theta_contact_deg"], m8["W_N"]))
    for x in m8["rows"]:
        print("  Fs %.3f k %5.0f v %.0f mm/s Fmax %.3f (x%.2f) v_allow %.1f mm/s w_allow %.0f deg/s f %.1f Hz" % (
            x["F_s"], x["k"], x["v_full_mms"], x["F_max_full_N"], x["ratio"], x["v_allow_mms"], x["w_allow_dps"], x["f_contact_Hz"]))
    print("  rec 60 dps v %.2f mm/s t2mm %.3f s" % (m8["rec_v_mms"], m8["t_slow_2mm_s"]), [round(x["F"], 3) for x in m8["F_max_rec"]])
    for x in R["M9"]["rows"]:
        print("M9", {k: round(v, 3) for k, v in x.items()})
    print("M9 belt", R["M9"]["belt"])
    print("M10", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in R["M10"].items()})
