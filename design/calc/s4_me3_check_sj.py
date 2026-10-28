"""S4 기계요소설계 유제 3개 — 교재 정답 대조와 우리 설계 적용 (이승준, CAP-AI-SJ-23)

서현 S4(`design/2026-10-28_S4_역학계산_1차.md`)의 '기계요소설계' 분야 유제를 보강한다. 서현 파일은 고치지 않고 이 파일과
`design/2026-10-28_S4_기계요소설계_유제3_승준.md`를 새로 만든다. 나사 토크는 서현 `s4_calc.screw_torque`를 그대로 씀.

ME1  DANotes (Wright, UWA) Threaded fasteners — Tutorial problem 1 : Acme 동력나사 올림·내림 토크, 효율, 자립
ME2  DANotes (Wright, UWA) Springs — Tutorial problem 2 : 압축 코일 스프링 강성, 밀착 응력, 피로 안전율
ME3  Oriental Motor Technical Reference — Selection calculation: ball screw drive (stepping motor) : 펄스·부하 토크·관성·가속 토크

출처 문제는 원문을 옮기지 않고 수치만 씀. 실행: python s4_me3_check_sj.py → s4_me3_results_sj.json
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s4_calc import screw_torque  # noqa: E402  (서현 함수 — sec α 포함 Shigley 식)

g = 9.807
out = {}


def pct(ai, ref):
    return round((ai - ref) / ref * 100, 2)


# ---------------------------------------------------------------- ME1 동력나사
F = 100e3                     # N
d, p = 30.0, 6.0              # Acme 30 mm, 1줄, 피치 6 → 리드 6
dm = d - p / 2                # 27 mm (유효지름 근사 = 바깥지름 − 피치/2)
mu, mu_c, dc = 0.15, 0.10, 40.0
T_c = F * mu_c * dc / 2 / 1000                    # 칼라(스러스트 베어링) 마찰 토크 N·m
r_book = screw_torque(F, mu, lead=p, dm=dm, alpha_deg=0.0)       # 교재 풀이처럼 sec α 무시
r_exact = screw_torque(F, mu, lead=p, dm=dm, alpha_deg=14.5)     # Acme 29°/2 = 14.5° 포함
T_raise_book = r_book["T_Nmm"] / 1000 + T_c
T_raise_exact = r_exact["T_Nmm"] / 1000 + T_c
P_1Hz = 2 * math.pi * 1.0 * T_raise_book
eff = F * p / 1000 / (2 * math.pi * T_raise_book)
TL_book = r_book["TL_Nmm"] / 1000                 # 내릴 때 필요한 토크 (s4_calc 부호: 양수 = 돌려야 내려감 = 자립)
r_half = screw_torque(F, mu / 2, lead=p, dm=dm, alpha_deg=0.0)
out["ME1"] = dict(
    source="DANotes Threaded fasteners Tutorial problem 1 (https://danotes.mech.uwa.edu.au/threads/problems/problems.html)",
    T_raise_Nm=round(T_raise_book, 1), book_T_raise=501, diff_pct=pct(T_raise_book, 501),
    T_raise_secalpha_Nm=round(T_raise_exact, 1), note_secalpha="Acme 반각 14.5°를 넣으면 508 N·m — 교재 답 501은 sec α 무시 (서현 수기 508과 같은 원인)",
    P_1Hz_kW=round(P_1Hz / 1000, 2), book_P=3.15, eff_pct=round(eff * 100, 1), book_eff=19,
    selflock=r_book["selflock"], T_lower_Nm=round(TL_book, 1), book_T_lower=106, diff_lower_pct=pct(TL_book, 106),
    half_mu_selflock=r_half["selflock"], half_mu_margin_mm=round(r_half["selflock_lhs"] - p, 3),
)
# 우리 설계 적용: M1 승강 나사 Tr8×8 (서현 값) — 내림 토크 부호와 '자립 여부'
r_m1 = screw_torque(0.910, 0.15)   # P 기본값 = Tr8×8, μ 0.15, α 15°
out["ME1"]["apply_M1"] = dict(T_Nmm=round(r_m1["T_Nmm"], 3), TL_Nmm=round(r_m1["TL_Nmm"], 3), selflock=r_m1["selflock"],
                              lead_angle=round(r_m1["lead_angle_deg"], 1), fric_angle=round(r_m1["fric_angle_deg"], 1),
                              mu_needed_for_selflock=round(r_m1["lead"] / (math.pi * r_m1["dm"]) * math.cos(math.radians(15)), 3))

# ---------------------------------------------------------------- ME2 압축 코일 스프링
D, dw, Na, Lf = 76.0, 12.5, 5, 140.0
G = 79.3e3                      # MPa (강, 교재 답 110 N/mm는 G ≈ 79 GPa일 때) — A229 표값 77.2 GPa면 107 N/mm
C = D / dw
k = G * dw**4 / (8 * D**3 * Na)
Nt = Na + 2                     # 끝 처리: 맞대고 연삭 (DANotes 문제 모음 머리말 "squared and ground")
Ls = dw * Nt
Ks = 1 + 0.5 / C                # 직접 전단 보정
Kw = (4 * C - 1) / (4 * C - 4) + 0.615 / C   # Wahl (교재의 Kh '전체 응력 집중' 자리에 씀 — 가정)
F_solid = k * (Lf - Ls)
tau = lambda K, Fx: K * 8 * Fx * D / (math.pi * dw**3)
tau_solid = tau(Ks, F_solid)
Sut = 1855 / dw**0.187          # A229 Sut = A/d^m, A = 1855 MPa·mm^m, m = 0.187 (Shigley 표 10-4)
Sus, Ses, Sys = 0.63 * Sut, 0.13 * Sut, 0.48 * Sut   # DANotes Springs 표 2 비 (A229)
Fm, Fa = 2500.0, 500.0
tm, ta = tau(Ks, Fm), tau(Kw, Fa)
n_f = 1 / (tm / Sus + ta / Ses)
n_y = Sys / (tm + ta)
out["ME2"] = dict(
    source="DANotes Springs Tutorial problem 2 (https://danotes.mech.uwa.edu.au/springs/problems/problems.html), 피로 식 DANotes Springs fatigue Eq.4a",
    C=round(C, 3), k_N_mm=round(k, 1), book_k=110, diff_k_pct=pct(k, 110),
    Ls_mm=Ls, F_solid_N=round(F_solid), tau_solid_MPa=round(tau_solid, 1), book_tau_solid=619, diff_tau_pct=pct(tau_solid, 619),
    Sut_MPa=round(Sut), tau_m=round(tm, 1), tau_a=round(ta, 1), n_fatigue=round(n_f, 2), book_n=1.3, diff_n_pct=pct(n_f, 1.3),
    n_yield=round(n_y, 2),
)
# 우리 설계 적용: 홀더 스프링 204 — 찍는 힘 보탬 F_s ≤ 0.18 N (S4 M3), 압축 행정은 잠정 5 mm (홀더가 눌리는 거리)
Gm = 81.7e3                     # 피아노선(음악선) G
d204, D204, comp = 0.25, 6.0, 5.0
k204 = 0.18 / comp              # 행정 5 mm에서 0.18 N이 넘지 않게: k ≤ 0.036 N/mm
Na204 = Gm * d204**4 / (8 * D204**3 * k204)
C204 = D204 / d204
Sut204 = 2211 / d204**0.145     # 음악선 A228: A = 2211, m = 0.145 (Shigley 표 10-4), 범위 0.10~6.5 mm
t204 = (1 + 0.5 / C204) * 8 * 0.18 * D204 / (math.pi * d204**3)
out["ME2"]["apply_204"] = dict(wire_d=d204, coil_D=D204, compression_mm=comp, k_max_N_mm=round(k204, 4),
                               Na=round(Na204, 1), C=C204, tau_at_0p18N_MPa=round(t204, 1),
                               Ssy_MPa=round(0.45 * Sut204), SF_static=round(0.45 * Sut204 / t204, 1),
                               note="잠정 — F_s는 F_ink 시험 후 정함 (D6). 피아노선 Ø0.25, 코일 Ø6, 유효 감김 약 %.0f" % Na204)

# ---------------------------------------------------------------- ME3 나사 구동 스테핑 모터 선정
m, mu_s, eta, mu0 = 40.0, 0.05, 0.9, 0.3
DB, LB, rho, PB = 0.015, 0.600, 7.9e3, 0.015
dl, feed, t0, t1, Sf = 0.03, 0.180, 0.8, 0.2, 2.0
theta_s = 360 * dl / (PB * 1000)
A = feed / PB * 360 / theta_s
f2 = A / (t0 - t1)
NM = f2 * theta_s / 360 * 60
Fx = m * g * (math.sin(0) + mu_s * math.cos(0))
F0 = Fx / 3
TL = Fx * PB / (2 * math.pi * eta) + mu0 * F0 * PB / (2 * math.pi)
JB = math.pi / 32 * rho * LB * DB**4
Jm = m * (PB / (2 * math.pi))**2
JL = JB + Jm
J0 = 380e-7
Ta = (J0 + JL) * (f2 / t1) * (math.pi * theta_s / 180)
TM = (TL + Ta) * Sf
out["ME3"] = dict(
    source="Oriental Motor, Technical Reference — Selection Calculations, ball screw drive example (https://www.orientalmotor.com/products/pdfs/2012-2013/G/usa_tech_calculation.pdf p.G-7~8)",
    theta_s_deg=round(theta_s, 3), book_theta=0.72, pulses=round(A), book_pulses=6000, f2_Hz=round(f2), book_f2=10000,
    NM_rpm=round(NM), book_NM=1200, F_N=round(Fx, 2), book_F=19.6, TL_Nm=round(TL, 4), book_TL=0.0567, diff_TL_pct=pct(TL, 0.0567),
    JB=JB, book_JB=0.236e-4, Jm=Jm, book_Jm=2.28e-4, JL=JL, book_JL=2.52e-4,
    TM_Nm=round(TM, 3), book_TM=0.48, diff_TM_pct=pct(TM, 0.48), inertia_ratio=round(JL / J0, 1), book_ratio=6.6,
)


# 우리 설계 적용: X축 (X 빔 묶음 386.5 g, LM8UU, T8 리드 8) — 같은 순서로 '토크가 모자란가, 속도가 모자란가'
def axis_check(name, steps_rev_motor, gear, rotor_J, T_avail_Nm, f_max_Hz, dist_mm, t_acc_frac=0.25):
    m_x = 0.3865
    mu_lin = 0.005                   # 볼 부싱 마찰계수 (카탈로그 0.002~0.003, 여유 2배) [가능성 높음]
    eta_s = 0.66                     # T8×8 사다리꼴 나사 효율 (S4 M1 0.661)
    lead = 0.008
    F_ax = m_x * g * mu_lin
    TL_load = F_ax * lead / (2 * math.pi * eta_s) / gear      # 모터 축 기준
    v_max = f_max_Hz / steps_rev_motor * lead * 1000           # mm/s (출력축 rev = steps_rev_motor 펄스)
    t_move = dist_mm / v_max / (1 - t_acc_frac)                # 사다리꼴: 가감속이 전체의 t_acc_frac씩
    t_acc = t_move * t_acc_frac
    JL_x = m_x * (lead / (2 * math.pi))**2 / gear**2
    omega_dot = (v_max / 1000 / lead * 2 * math.pi * gear) / t_acc
    T_acc = (rotor_J + JL_x) * omega_dot
    T_req = (TL_load + T_acc) * 2
    return dict(name=name, v_max_mm_s=round(v_max, 2), t_move_s=round(t_move, 2), T_load_Nm=TL_load, T_acc_Nm=T_acc,
                T_req_Nm=T_req, T_avail_Nm=T_avail_Nm, SF=round(T_avail_Nm / T_req, 1) if T_req else None)


out["ME3"]["apply_X"] = [
    # 28BYJ-48 단극(ULN2003): 출력축 반걸음 4075.77/rev, 공회전 최대 약 1000 Hz (사양서) → 펄스 속도가 한계
    axis_check("28BYJ-48 + ULN2003 (보유) — 58 mm", 4075.77, 1.0, 0.0, 0.0343, 1000, 58, 0.05),
    axis_check("28BYJ-48 + ULN2003 (보유) — 구멍 사이 4.4 mm", 4075.77, 1.0, 0.0, 0.0343, 1000, 4.4, 0.05),
    # NEMA17 (예: 17HS4401) + A4988 1/8 마이크로스텝: 1600 펄스/rev, 600 rpm까지 실사용 [가능성 높음], 회전자 관성 약 54 g·cm²
    axis_check("NEMA17 + A4988 (구매 시) — 58 mm", 1600, 1.0, 54e-7, 0.40, 16000, 58),
    axis_check("NEMA17 + A4988 (구매 시) — 4.4 mm", 1600, 1.0, 54e-7, 0.40, 16000, 4.4),
]

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s4_me3_results_sj.json")
with open(path, "w", encoding="utf-8") as fp:
    json.dump(out, fp, ensure_ascii=False, indent=1, default=float)
print(json.dumps(out, ensure_ascii=False, indent=1, default=float))
