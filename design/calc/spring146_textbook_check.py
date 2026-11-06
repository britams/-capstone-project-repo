# -*- coding: utf-8 -*-
"""스프링 146 역학계산 2차 — 교재 유제 5개 직접 풀이 + 교재 답 대조 (서현, 2026-11-06, CAP-AI-25)

교재 원문·그림은 레포에 넣지 않는다 (공개 레포). 문제 번호와 주어진 수치만 쓴다.
  T8  Riley·Sturges, Engineering Mechanics: Statics, Example Problem 9-6      (정역학: 두 접촉점 마찰 + 넘어짐)
  T9  Gere·Goodno, Mechanics of Materials SI 9e, Example 2-1                  (고체역학: 강체 막대 + 스프링, 변위 적합)
  T10 Meriam·Kraige, Dynamics SI 9e, Sample Problem 8/1                       (동역학: 스프링-질량 자유진동)
  T11 Budynas·Nisbett, Shigley's MED 11e SI, Example 10-1                     (기계요소: 압축 스프링 해석)
  T12 Budynas·Nisbett, Shigley's MED 11e SI, Example 10-2                     (기계요소: 정적 스프링 설계 표)
판정: 교재 답과 상대 차이 ≤ 2 % → 일치. 넘으면 원인을 적는다 (교재 반올림·단위 변환 오타 포함).
실행: python3 design/calc/spring146_textbook_check.py → spring146_textbook_check.json
"""
import json
import math
import os

import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
TOL = 0.02
rows = []


def cmp(prob, item, mine, book, unit="", note=""):
    rel = abs(mine - book) / abs(book) if book else abs(mine)
    rows.append(dict(problem=prob, item=item, mine=round(mine, 5), book=book, unit=unit, rel_diff_pct=round(100 * rel, 3),
                     ok=rel <= TOL, note=note))


# ---------------------------------------------------------------- T8 Riley 9-6
def t8():
    W, mu, x_half, x_cg = 600.0, 0.6, 0.4, 0.4       # N, -, 바퀴 간격 0.8 m의 반, 무게중심은 B에서 0.4 m
    An, Bn, P, h = sp.symbols("An Bn P h", real=True)
    # ΣFx: P − μAn − μBn = 0, ΣFy: An + Bn − W = 0, ΣM_B: x_cg·W − h·P − 0.8·An = 0
    s = sp.solve([P - mu * An - mu * Bn, An + Bn - W, x_cg * W - h * P - 0.8 * An], [An, Bn, P], dict=True)[0]
    P_val = float(s[P])
    h_tip = float(sp.solve(sp.Eq(s[An], 0), h)[0])    # 넘어지기 직전: An = 0
    cmp("T8 Riley 9-6", "미끄러지기 시작하는 힘 P", P_val, 360.0, "N")
    cmp("T8 Riley 9-6", "넘어지지 않는 최대 높이 h", h_tip, 0.667, "m", "교재는 240/360 = 0.667로 반올림")
    # 다른 방법 확인: 넘어짐 직전 tanφ = μ → 0.4/h = 0.6
    cmp("T8 Riley 9-6", "h 다른 방법 (0.4/μ)", 0.4 / mu, 0.667, "m")


# ---------------------------------------------------------------- T9 Gere 2-1
def t9():
    P, k, L = sp.symbols("P k L", positive=True)
    dC, dD = sp.symbols("dC dD", real=True)
    dB = dC / 2
    th = dD / L
    kR = sp.Rational(2, 5) * k * L ** 2
    eq1 = sp.Eq(k * dB * L / 2 + k * (dC - dD) * L - P * L, 0)   # ΣM_A, 막대 ABC
    eq2 = sp.Eq(k * (dC - dD) * L - kR * th, 0)                  # ΣM_F, 막대 DEF
    s = sp.solve([eq1, eq2], [dC, dD], dict=True)[0]
    book = dict(dD=sp.Rational(4, 3) * P / k, dC=sp.Rational(28, 15) * P / k, th=sp.Rational(4, 3) * P / (k * L),
                FB=sp.Rational(14, 15) * P, FCD=sp.Rational(8, 15) * P, ME=sp.Rational(8, 15) * P * L)
    mine = dict(dD=s[dD], dC=s[dC], th=s[dD] / L, FB=k * s[dC] / 2, FCD=k * (s[dC] - s[dD]), ME=kR * s[dD] / L)
    for key in book:
        same = sp.simplify(mine[key] - book[key]) == 0
        # 기호식이라 수치로도 (P=1, k=1, L=1) 비교
        mv = float(mine[key].subs({P: 1, k: 1, L: 1}))
        bv = float(book[key].subs({P: 1, k: 1, L: 1}))
        cmp("T9 Gere 2-1", key + (" (기호식 같음)" if same else " (기호식 다름!)"), mv, bv, "P/k 등 무차원")


# ---------------------------------------------------------------- T10 Meriam 8/1
def t10():
    m, k, v0, g = 10.0, 2500.0, 0.5, 9.81
    d_st = m * g / k
    wn = math.sqrt(k / m)
    fn = wn / (2 * math.pi)
    amp = v0 / wn
    cmp("T10 Meriam 8/1", "정적 처짐 δst", d_st * 1e3, 39.2, "mm")
    cmp("T10 Meriam 8/1", "ωn", wn, 15.81, "rad/s")
    cmp("T10 Meriam 8/1", "fn", fn, 2.52, "Hz")
    cmp("T10 Meriam 8/1", "주기 τ", 1 / fn, 0.397, "s")
    cmp("T10 Meriam 8/1", "진폭 x0'/ωn", amp * 1e3, 31.6, "mm")
    cmp("T10 Meriam 8/1", "최대 속도", amp * wn, 0.5, "m/s")
    cmp("T10 Meriam 8/1", "최대 가속도", amp * wn ** 2, 7.91, "m/s²")
    # 운동방정식을 수치 적분해서 진폭 확인 (해석해와 독립)
    x, v, dt, xmax = 0.0, v0, 1e-5, 0.0
    for _ in range(int(0.2 / dt)):
        a = -k / m * x
        v += a * dt
        x += v * dt
        xmax = max(xmax, abs(x))
    cmp("T10 Meriam 8/1", "진폭 (수치 적분)", xmax * 1e3, 31.6, "mm")


# ---------------------------------------------------------------- T11 Shigley 10-1
def KB(C):
    return (4 * C + 2) / (4 * C - 3)


def t11():
    d, OD, Nt = 0.94, 11.113, 12.5          # mm, 양끝 squared (닫음, 연마 안 함)
    A, mexp, G = 2211.0, 0.145, 81.7e3      # MPa·mm^m, -, MPa (Table 10-4, 10-5: 0.8~1.6 mm)
    Sut = A / d ** mexp
    Ssy = 0.45 * Sut
    D = OD - d
    C = D / d
    F = math.pi * d ** 3 * Ssy / (8 * KB(C) * D)
    Na = Nt - 2
    k = d ** 4 * G / (8 * D ** 3 * Na)
    y = F / k
    Ls = (Nt + 1) * d
    L0 = y + Ls
    L0cr = 2.63 * D / 0.5
    p = (L0 - 3 * d) / Na
    for item, mv, bv, u in (("Sut", Sut, 2231, "MPa"), ("Ssy", Ssy, 1004, "MPa"), ("C", C, 10.8, ""), ("KB", KB(C), 1.124, ""),
                            ("F (항복 하중)", F, 28.26, "N"), ("k", k, 0.7207, "N/mm"), ("y", y, 39.70, "mm"),
                            ("Ls", Ls, 12.69, "mm"), ("L0", L0, 52.39, "mm"), ("(L0)cr", L0cr, 53.51, "mm"), ("피치 p", p, 4.72, "mm")):
        note = ""
        if item.startswith("F "):
            note = "교재 산술 오류: π(0.94³)(1004)/(8·1.124·10.1727) = 28.63 N. 교재 (d) y = 39.70 = 28.61/0.7207이라 뒤 계산은 28.6을 씀"
        cmp("T11 Shigley 10-1", item, mv, bv, u, note)


# ---------------------------------------------------------------- T12 Shigley 10-2
def design_row(d, Fmax, ymax, A=2211.0, mexp=0.145, G=81.0e3, ns=1.2, xi=0.15):
    """Figure 10-3 흐름 (as-wound, 구멍·봉 없음, 양끝 squared & ground)"""
    Ssy = 0.45 * A / d ** mexp
    alpha = Ssy / ns
    beta = 8 * (1 + xi) * Fmax / (math.pi * d ** 2)
    C = (2 * alpha - beta) / (4 * beta) + math.sqrt(((2 * alpha - beta) / (4 * beta)) ** 2 - 3 * alpha / (4 * beta))
    D = C * d
    tau_s = KB(C) * 8 * (1 + xi) * Fmax * D / (math.pi * d ** 3)
    Na = G * d ** 4 * ymax / (8 * D ** 3 * Fmax)
    Nt = Na + 2
    Ls = d * Nt
    L0 = Ls + (1 + xi) * ymax
    L0cr = 2.63 * D / 0.5
    fom = -2.6 * math.pi ** 2 * d ** 2 * Nt * D / 4
    return dict(d=d, Ssy=Ssy, alpha=alpha, beta=beta, C=C, D=D, KB=KB(C), tau_s=tau_s, ns=Ssy / tau_s, OD=D + d,
                Na=Na, Nt=Nt, Ls=Ls, L0=L0, L0cr=L0cr, fom_mm3=fom)


def t12():
    r = design_row(2.03, 89.0, 50.8)
    for item, key, bv, u in (("Ssy", "Ssy", 897.9, "MPa"), ("α", "alpha", 748.3, "MPa"), ("β", "beta", 63.2, "MPa"), ("C", "C", 10.5, ""),
                             ("D", "D", 21.3, "mm"), ("KB", "KB", 1.128, ""), ("τs", "tau_s", 748, "MPa"), ("ns", "ns", 1.2, ""),
                             ("OD", "OD", 23.3, "mm"), ("Na", "Na", 10.16, "회"), ("Nt", "Nt", 12.16, "회"), ("Ls", "Ls", 24.3, "mm"),
                             ("L0", "L0", 82.7, "mm"), ("(L0)cr", "L0cr", 112, "mm")):
        note = ""
        if key == "Ls":
            note = "교재 산술 오류: 2.03 × 12.16 = 24.68 (교재 24.3). 그래서 교재 L0 82.7도 0.4 mm 작음 (맞는 값 83.1)"
        elif key == "L0":
            note = "위 Ls 오류가 이어짐"
        cmp("T12 Shigley 10-2", item, r[key], bv, u, note)
    # 교재 반올림 재현: D = 21.3 고정
    Na_r = 81.0e3 * 2.03 ** 4 * 50.8 / (8 * 21.3 ** 3 * 89.0)
    cmp("T12 Shigley 10-2", "Na (D=21.3 반올림 재현)", Na_r, 10.16, "회")
    # 교재 표 (d별) 몇 칸 대조 — 표의 L0cr 줄은 2.63 D/0.5로 계산됨
    table = {1.600: dict(C=6.205, D=9.931, Na=39.1), 1.905: dict(C=9.178, D=17.475, Na=14.2), 2.413: dict(C=15.02, D=36.245, Na=4.1)}
    for d, bk in table.items():
        G = 81.0e3 if d > 1.6 else 81.7e3
        rr = design_row(d, 89.0, 50.8, G=G)
        cmp("T12 Shigley 10-2 표", "d=%.3f C" % d, rr["C"], bk["C"], "")
        cmp("T12 Shigley 10-2 표", "d=%.3f D" % d, rr["D"], bk["D"], "mm")
        cmp("T12 Shigley 10-2 표", "d=%.3f Na" % d, rr["Na"], bk["Na"], "회")
    # 교재 본문 오류 기록 (계산 아님): 표 아래 문장의 "0.203 mm"는 2.03 mm, fom 식의 (25.4)^3은 인치 환산 흔적
    return r


def main():
    t8(); t9(); t10(); t11(); t12()
    out = dict(rows=rows, n=len(rows), n_ok=sum(r["ok"] for r in rows),
               textbook_errata=["Shigley 10-2 표 아래 문장: 'diameters less than 0.203 mm'·'0.203 mm wire'는 2.03 mm의 SI 변환 오타 (표·본문 계산은 2.03)",
                                "Shigley 10-1 (b): F = 28.26 N은 산술 오류, 맞는 값 28.6 N (교재 (d)는 28.6으로 계산)",
                                "Shigley 10-2: Ls = 2.03(12.16) = 24.68 mm인데 교재 24.3 → L0도 82.7 대신 83.1 mm",
                                "Shigley 10-2 fom 식에 (25.4)^3 나눗셈 — 인치판 단위 환산 흔적, 비교용이라 결론에는 영향 없음",
                                "Shigley 10-4 (d): G 11.75(10^6)·중력 386 (in/s²)이 SI 식에 섞임 — 이번 유제에서는 쓰지 않음, 서지 주파수는 식 (10-25)를 SI로 직접 계산"])
    with open(os.path.join(HERE, "spring146_textbook_check.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    for r in rows:
        print("%-20s %-30s 나 %-12s 교재 %-9s %6.2f%% %s %s" % (r["problem"], r["item"], r["mine"], r["book"], r["rel_diff_pct"], "OK" if r["ok"] else "★", r["note"]))
    print("일치 %d / %d" % (out["n_ok"], out["n"]))


if __name__ == "__main__":
    main()
