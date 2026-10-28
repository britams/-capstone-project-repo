# -*- coding: utf-8 -*-
"""S4 ③ 교과서 유제 대조 — s4_calc.py의 공용 식이 교재 정답·해설집 값을 재현하는지 먼저 확인 (CAP-AI-19)

실행: python3 design/calc/s4_textbook_check.py  →  화면 표 + design/calc/s4_textbook_check.json
교재 (문제 원문·해설 그림은 저작권 때문에 레포에 넣지 않음 — 번호·쪽·주어진 수치만 적음):
  Riley·Sturges, Engineering Mechanics: Statics 2판 (Wiley) + 같은 판 Instructor's Solutions Manual
  Meriam·Kraige·Bolton, Engineering Mechanics: Dynamics 9판 SI (Wiley) + 9판 해설집(문제별 PDF)
  Gere·Goodno, Mechanics of Materials 9판 SI (Cengage 2018) + 해설집 9장 (미국판 — 단위·수치가 SI판과 다름)
'AI'는 이 스크립트 값, '본인'(서현 수기)은 S4 문서 ③에 적는다.
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s4_calc import screw_torque, beam_point_load, jam_solve   # noqa: E402

g = 9.81
rows = []


def add(m, prob, qty, book, manual, ai, unit, note=""):
    def pct(ref):
        return None if ref is None or ref == 0 else 100 * (ai - ref) / abs(ref)
    rows.append(dict(M=m, problem=prob, qty=qty, book=book, manual=manual, ai=ai, unit=unit,
                     diff_book_pct=pct(book), diff_manual_pct=pct(manual), note=note))


# ---------- M1  Riley 9-66 (p.518): 사각나사 프레스, r_m 20 mm, 리드 100 mm, μ 0.15, 누르는 힘 400 N ----------
r = screw_torque(400.0, 0.15, lead=100.0, dm=40.0, alpha_deg=0.0)
add("M1", "Riley 9-66", "조이는 모멘트 M", 8.59e3, 8.592e3, r["T_Nmm"], "N·mm",
    "Shigley 식에 α = 0 → Riley 식 M = W r tan(α_lead + φ)와 같음. 리드각 %.3f°, 마찰각 %.3f°" % (r["lead_angle_deg"], r["fric_angle_deg"]))
add("M1", "Riley 9-66", "자립 여부 (1 = 자립)", 0, 0, 1.0 if r["selflock"] else 0.0, "-",
    "책·해설집: 자립 안 함(풀 때 모멘트 불필요). AI: π μ d_m = %.2f < l = 100 → 자립 안 함, 내림 토크 %.0f N·mm (음수 = 저절로 풀림)" % (r["selflock_lhs"], r["TL_Nmm"]))

# ---------- M2  Meriam 3/1, 3/2 (p.P-41): 마찰 있는 직선 운동 F = ma ----------
def crate_incline(m, th_deg, mus, muk, Pf):
    """경사면(θ) 위 상자, 경사면과 나란한 힘 P(위쪽 +). 정지 마찰 검사 → 미끄러지면 운동 마찰로 a (위쪽 +)"""
    th = math.radians(th_deg)
    N = m * g * math.cos(th)
    drive = Pf - m * g * math.sin(th)                # 마찰 빼고 위로 미는 힘
    if abs(drive) <= mus * N:
        return 0.0, N, drive
    return (drive - math.copysign(muk * N, drive)) / m, N, drive


v0, mu = 6.0, 0.40
a1 = mu * g
add("M2", "Meriam 3/1", "멈출 때까지 시간 t", 1.529, 1.529, v0 / a1, "s")
add("M2", "Meriam 3/1", "미끄러진 거리 x", 4.59, 4.59, v0 ** 2 / (2 * a1), "m")
for Pf, book in ((0.0, -1.118), (150.0, 0.0), (300.0, 2.04)):
    a, N, drive = crate_incline(50.0, 15.0, 0.20, 0.15, Pf)
    add("M2", "Meriam 3/2", "가속도 a (P = %.0f N, 위 +)" % Pf, book, book, a, "m/s²",
        "N = %.1f N, 마찰 없이 미는 힘 %.1f N vs 최대 정지 마찰 %.1f N" % (N, drive, 0.2 * N))

# ---------- M3  Riley 6-49 (p.295~296): 접촉 반력이 0이 되는 순간 (넘어감 시작) ----------
# 300 lb 원기둥(반지름 9 in)이 20° 경사면 위, 경사면에서 3 in 높이 모서리 B. 중심에 수평 P. 넘어가기 시작: 경사면 반력 A = 0
W, R_, hb, th = 300.0, 9.0, 3.0, math.radians(20)
beta = math.acos((R_ - hb) / R_)                    # 중심–모서리 선과 경사면 법선 사이
n = (-math.sin(th), math.cos(th)); s_ = (math.cos(th), math.sin(th))
u = (math.cos(beta) * n[0] - math.sin(beta) * s_[0], math.cos(beta) * n[1] - math.sin(beta) * s_[1])   # 모서리 → 중심 방향
RB = W / u[1]
P649 = -RB * u[0]
add("M3", "Riley 6-49", "필요한 힘 P (A = 0)", None, 750.0, P649, "lb",
    "장말 정답 없음(별표 아님) → 해설집과만 대조. 모서리 반력 %.1f lb" % RB)

# ---------- M4  Riley 6-41 (p.294): 핀 A에 대한 모멘트 평형 (레버) ----------
Pp, ang = 30.0, math.radians(30)                    # C (4, 11) in, P 수평 아래로 30°; Q 수평, B (4, 5.5)
Q = (Pp * math.cos(ang) * 11 + Pp * math.sin(ang) * 4) / 5.5
Ax, Ay = Q - Pp * math.cos(ang), Pp * math.sin(ang)
add("M4", "Riley 6-41", "브레이크 실린더 힘 Q", None, 62.87, Q, "lb", "장말 정답 없음 → 해설집과만 대조")
add("M4", "Riley 6-41", "핀 반력 |A|", None, 39.82, math.hypot(Ax, Ay), "lb", "각 %.2f° (해설집 22.13°)" % math.degrees(math.atan2(Ay, Ax)))

# ---------- M5  Riley 9-43 (p.495): 손잡이 하나로 당기는 서랍 ----------
def drawer(Wd, mu_s, mu_b, w, L, a_h, gap, mode):
    """서랍 폭 w, 깊이 L, 손잡이는 왼쪽 옆면에서 a_h, 틈 gap. 대각 두 모서리(뒤 왼쪽 A, 앞 오른쪽 B)가 옆면에 닿음.
       mode 'manual': sinθ = gap/L (해설집), 'exact': w cosθ + L sinθ = w + gap, 'zero': θ = 0 (작은 각)"""
    if mode == "manual":
        t = math.asin(gap / L)
    elif mode == "exact":
        Rr, ph = math.hypot(w, L), math.atan2(L, w)
        t = ph - math.acos((w + gap) / Rr)
    else:
        t = 0.0
    a_arm = (w - a_h) * math.cos(t)                 # 손잡이 → B 수평 거리
    b_arm = w * math.cos(t) + L * math.sin(t)       # A → B 수평 거리
    d_arm = L * math.cos(t) - w * math.sin(t)       # A → B 세로 거리
    den = 2 * mu_s * a_arm - d_arm - mu_s * b_arm   # ≥ 0 이면 끼임
    if den >= 0:
        return dict(jam=True, theta=math.degrees(t), mu_c=d_arm / (2 * a_arm - b_arm))
    N = mu_b * Wd * (b_arm / 2 - a_arm) / den
    return dict(jam=False, theta=math.degrees(t), N=N, P=mu_b * Wd + 2 * mu_s * N, mu_c=d_arm / (2 * a_arm - b_arm))


dm_ = drawer(2.0, 0.60, 0.10, 30.0, 18.0, 3.0, 0.75, "manual")
de_ = drawer(2.0, 0.60, 0.10, 30.0, 18.0, 3.0, 0.75, "exact")
dz_ = drawer(2.0, 0.60, 0.10, 30.0, 18.0, 3.0, 0.75, "zero")
add("M5", "Riley 9-43", "당기는 힘 P (해설집 기하, θ %.3f°)" % dm_["theta"], None, 1.202, dm_["P"], "lb",
    "장말 정답 없음. 해설집 sinθ = 0.75/18 근사")
add("M5", "Riley 9-43", "당기는 힘 P (정확한 기울기 θ %.3f°)" % de_["theta"], None, 1.202, de_["P"], "lb",
    "w cosθ + L sinθ = w + 틈으로 θ를 다시 구함 — 결과 같음")
add("M5", "Riley 9-43", "당기는 힘 P (기울기 무시 θ = 0)", None, 1.202, dz_["P"], "lb",
    "끼임 한계(μ_c = %.2f)에 가까워 기울기를 무시하면 17 %% 작게 나옴 → 끼임 근처에서는 기하를 정확히" % dz_["mu_c"])
# 같은 꼴을 s4_calc.jam_solve로: 손잡이를 옆면(봉 A 선) 위로 옮기면(a_h = 0) 서랍 한계 μ_c = L/w 와 jam_solve(k = 0.5, h = 0) 한계 L/d 가 같은 식
js = jam_solve(0.6, 2.0, 1.0, 0.0, 0.0, 18.0, 30.0, 0.0, k=0.5)
dz0 = drawer(2.0, 0.60, 0.10, 30.0, 18.0, 0.0, 0.75, "zero")
add("M5", "Riley 9-43 변형 (손잡이를 옆면 위로)", "끼임 한계 μ_c", None, None, js["mu_crit"], "-",
    "서랍 식 μ_c = L/(w − 2a_h) = %.3f 와 같음 → M5의 'A·B 나눔(대각 접촉)' 경계 = 이 모델" % dz0["mu_c"])

# ---------- M6  Gere 9.3-1 (p.880): 단순보 집중하중 (예제 9-3 식) ----------
I_ipn300 = 9800e4                                    # mm4 (부록 IPN 300, 9800 cm4)
for E, tag in ((200e3, "E = 200 GPa"), (210e3, "E = 210 GPa")):
    b = beam_point_load(45e3, 3000.0, E, I_ipn300, a=2100.0)
    add("M6", "Gere 9.3-1 SI판 (%s)" % tag, "최대 처짐 δ_max", 1.04, None, b["delta_max"], "mm",
        "문제에 E가 없음 — 정답 1.04 mm는 E = 200 GPa일 때 나옴" if E == 200e3 else "210 GPa로 풀면 정답과 5 % 다름")
    add("M6", "Gere 9.3-1 SI판 (%s)" % tag, "A 회전각 θ_A", 9.4e-4, None, b["theta_A"], "rad")
bu = beam_point_load(10.0, 120.0, 29000.0, 285.0, a=84.0)    # 해설집(미국판): kip, in, ksi
add("M6", "Gere 9.3-1 해설집(미국판 수치)", "최대 처짐 δ_max", None, 0.0349, bu["delta_max"], "in",
    "해설집은 L 10 ft, P 10 kip, I 285 in⁴ — SI판과 수치가 다른 판. 같은 식으로 해설집 값 재현")
add("M6", "Gere 9.3-1 해설집(미국판 수치)", "A 회전각 θ_A", None, 7.93e-4, bu["theta_A"], "rad")
bc = beam_point_load(1.0, 153.0, 200e3, math.pi * 8 ** 4 / 64)
add("M6", "M6 특수형 (가운데 하중)", "δ / F (Ø8, L 153)", None, None, bc["delta_max"], "mm/N",
    "a = L/2 이면 같은 함수가 PL³/48EI = %.6f mm/N" % (153.0 ** 3 / (48 * 200e3 * math.pi * 8 ** 4 / 64)))

if __name__ == "__main__":
    def f(v):
        if v is None:
            return "—"
        return ("%.4g" % v) if abs(v) < 1e4 else ("%.0f" % v)
    print("%-4s %-34s %-34s %10s %10s %10s %8s %8s" % ("M", "문제", "값", "책 정답", "해설집", "AI", "책%", "해설%"))
    for r in rows:
        print("%-4s %-34s %-34s %10s %10s %10s %8s %8s" % (r["M"], r["problem"], r["qty"], f(r["book"]), f(r["manual"]), f(r["ai"]),
              f(r["diff_book_pct"]), f(r["diff_manual_pct"])))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s4_textbook_check.json")
    json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
