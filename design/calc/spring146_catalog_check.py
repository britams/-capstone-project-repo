# -*- coding: utf-8 -*-
"""스프링 146 기성품 검사 (서현, 2026-11-06, CAP-AI-26) — 서현 결정 "새 스프링을 기본으로, 기성품을 무조건"

기성품은 치수를 우리가 정할 수 없다 → 새 사양(d 0.229, D 2.63, Na 15, L0 14.7, k 103.6)은 '목표'이고,
카탈로그 값(바깥지름, 선 지름, 자유 길이, 강성, 밀착 길이)을 넣어 아래 조건을 모두 통과하는 것을 산다.
조건의 근거: design/2026-11-06_S4_스프링146_역학계산_2차_서현.md (1차 C1~C3, Shigley 10-1·10-2)

  K  강성        94 ≤ k ≤ 118 N/m                       (C2 낮은 말벌도 F_p, C3 고장 때 ≤ F_safe 1.0 N)
  T  쓸 수 있는 길이  L0 − Ls ≥ (1 + ξ)·y_max, ξ 0.15     (Shigley 식 10-17, y_max = 바닥 무게 + h_max 8.5 mm)
  S  밀착 안전율   ns = Ssy / τ(밀착) ≥ 1.2                (Shigley 식 10-21, Ssy = 0.45 Sut)
  F  피로          nf ≥ 1.2 (Zimmerli, Goodman)
  O  바깥지름      OD ≤ 9 mm (D5e 스프링 자리)
  R  안내 봉       ID − 봉 지름 ≥ 0.3 mm 인 봉이 1.5 / 2 / 3 / 4 mm 중에 있음 (좌굴 안내, Shigley 10-1 (g))
  H  서지          지금 반걸음 1000 Hz가 서지 주파수의 ±15 % 밖이면 OK (아니면 펌웨어 반걸음 간격을 바꿈 — 금지 대역 = 서지 ±15 %)
  C  스프링 지수    정보만 (기성품은 이미 감겨 있어 감기 어려움은 제조사 몫)
사용: python3 design/calc/spring146_catalog_check.py  (아래 CANDIDATES에 카탈로그 값을 넣음)
"""
import math
import sys

sys.path.insert(0, __import__("os").path.dirname(__file__))
from spring146_calc2 import IN, G_music, KB   # noqa: E402

g = 9.81
RODS = (1.5, 2.0, 3.0, 4.0)

# 이름, 바깥지름 mm, 선 지름 mm, 자유 길이 mm, 강성 N/mm, 밀착 길이 mm(없으면 None), 유효 감김(없으면 None), 출처
CANDIDATES = [
    ("목표 (2차 사양, 기성품 아님)", 2.858, 0.229, 14.73, 0.1036, 3.89, 15, "spring146_calc2.py"),
    ("차선 (1차 사양, 기성품 아님)", 7.90, 0.40, 14.04, 0.1045, 3.20, 6, "1차 문서"),
]


def check(name, OD, d, L0, k_Nmm, Ls=None, Na=None, src=""):
    D = OD - d
    C = D / d
    k = k_Nmm * 1e3
    G = G_music(d)
    if Na is None:
        Na = G * (d * 1e-3) ** 4 / (8 * (D * 1e-3) ** 3 * k)
    if Ls is None:
        Ls = (Na + 2) * d                                   # squared & ground 가정
    W = IN["m_floor"] * g
    y_max = (W / k + IN["h_max"]) * 1e3                     # mm
    Sut = IN["A"] / d ** IN["mexp"]                         # MPa
    Ssy = 0.45 * Sut
    F_solid = k * (L0 - Ls) * 1e-3
    tau = KB(C) * 8 * F_solid * D / (math.pi * d ** 3)      # MPa (N, mm)
    Fmin, Fmax = W, W + IN["F_p"] * 1.25
    ta = KB(C) * 8 * (Fmax - Fmin) / 2 * D / (math.pi * d ** 3)
    tm = KB(C) * 8 * (Fmax + Fmin) / 2 * D / (math.pi * d ** 3)
    Ssu = 0.67 * Sut
    Sse = 241 / (1 - 379 / Ssu)
    nf = 1 / (ta / Sse + tm / Ssu)
    Wsp = math.pi ** 2 * (d * 1e-3) ** 2 * (D * 1e-3) * Na * IN["gamma"] / 4
    surge = 0.5 * math.sqrt(k * g / Wsp)
    ID = D - d
    rod = max([r for r in RODS if ID - r >= 0.3], default=None)
    res = dict(K=94 <= k <= 118, T=(L0 - Ls) >= 1.15 * y_max - 0.02, S=Tau_ok(Ssy, tau), F=nf >= 1.2, O=OD <= 9.0, R=rod is not None,
               H=abs(IN["step_rate"] - surge) / surge >= 0.15)
    print("%s  [%s]" % (name, src))
    print("   k %.1f N/m, OD %.2f, ID %.2f, d %.3f, C %.1f, Na %.1f, L0 %.2f, Ls %.2f, 쓸 수 있는 길이 %.2f (필요 %.2f)" %
          (k, OD, ID, d, C, Na, L0, Ls, L0 - Ls, 1.15 * y_max))
    print("   ns %.2f, nf %.2f, 서지 %.0f Hz (반걸음 금지 %.0f~%.0f Hz), 안내 봉 %s mm" % (Ssy / tau, nf, surge, surge * 0.85, surge * 1.15, rod))
    print("   " + "  ".join("%s %s" % (key, "OK" if v else "✗") for key, v in res.items()) + ("   → 통과" if all(res.values()) else "   → 불합격"))
    return all(res.values())


def Tau_ok(Ssy, tau):
    return Ssy / tau >= 1.2


if __name__ == "__main__":
    for c in CANDIDATES:
        check(*c)
